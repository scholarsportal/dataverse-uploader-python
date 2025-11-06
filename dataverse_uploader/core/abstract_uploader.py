"""Abstract base class for repository uploaders."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from dataverse_uploader.core.config import UploaderConfig
from dataverse_uploader.core.exceptions import UploaderException
from dataverse_uploader.resources.base import Resource
from dataverse_uploader.resources.file_resource import FileResource
from dataverse_uploader.utils.http_client import HTTPClient

logger = logging.getLogger(__name__)


class AbstractUploader(ABC):
    """Abstract base class for all repository uploaders.
    
    This class provides the common framework for uploading files to
    repositories. Specific implementations (Dataverse, SEAD) extend
    this class with repository-specific logic.
    """

    def __init__(self, config: UploaderConfig):
        """Initialize the uploader.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.http_client = HTTPClient(config)
        
        # Statistics tracking
        self.total_files = 0
        self.uploaded_files = 0
        self.skipped_files = 0
        self.failed_files = 0
        self.total_bytes = 0
        self.uploaded_bytes = 0
        
        # ID mappings for tracking uploaded resources
        self.resource_id_map: dict[str, str] = {}
        
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging based on configuration."""
        log_level = logging.DEBUG if self.config.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    def process_requests(self, paths: list[str | Path]) -> None:
        """Process upload requests for the given paths.
        
        Args:
            paths: List of file or directory paths to upload
        """
        logger.info("=" * 80)
        logger.info("Starting upload process")
        logger.info(f"Server: {self.config.server_url}")
        logger.info(f"Dataset: {self.config.dataset_pid}")
        logger.info(f"List only: {self.config.list_only}")
        logger.info("=" * 80)
        
        # Track failed uploads for retry
        self.failed_uploads: list[tuple[Resource, str]] = []
        
        try:
            # Validate configuration
            self.validate_configuration()
            
            # Process each path
            for path_str in paths:
                path = Path(path_str)
                if not path.exists():
                    logger.warning(f"Path does not exist: {path}")
                    continue
                
                resource = FileResource(path)
                self._process_resource(resource, parent_path="/")
            
            # Retry failed uploads with delays
            if self.failed_uploads and not self.config.list_only:
                self._retry_failed_uploads()
            
            # Print summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise
        finally:
            self.http_client.close()

    def _retry_failed_uploads(self) -> None:
        """Retry failed uploads with exponential backoff.
        
        Sometimes Dataverse is still processing previous uploads,
        causing temporary failures. This retries those uploads.
        """
        import time
        
        max_retry_attempts = 3
        retry_delay = 5  # seconds
        
        for attempt in range(1, max_retry_attempts + 1):
            if not self.failed_uploads:
                break
            
            logger.info("=" * 80)
            logger.info(f"Retry attempt {attempt}/{max_retry_attempts} for {len(self.failed_uploads)} failed file(s)")
            logger.info(f"Waiting {retry_delay} seconds for Dataverse to finish processing...")
            logger.info("=" * 80)
            
            time.sleep(retry_delay)
            
            # Reload existing files (some may have been processed)
            if hasattr(self, '_load_existing_files'):
                try:
                    self._load_existing_files()
                except Exception as e:
                    logger.warning(f"Could not reload existing files: {e}")
            
            # Try uploading failed files again
            still_failed = []
            for resource, parent_path in self.failed_uploads:
                logger.info(f"Retrying: {resource.get_name()}")
                
                # Check if it now exists (may have been processed)
                existing_id = self.get_existing_resource_id(resource, parent_path)
                if existing_id:
                    logger.info(f"File now exists (was being processed): {resource.get_name()}")
                    self.skipped_files += 1
                    self.failed_files -= 1  # It wasn't really failed, just processing
                    continue
                
                # Try uploading again
                file_id = self.upload_file(resource, parent_path)
                
                if file_id:
                    self.uploaded_files += 1
                    self.uploaded_bytes += resource.length()
                    self.failed_files -= 1
                    logger.info(f"Successfully uploaded on retry: {resource.get_name()}")
                else:
                    # Still failed, add back to list
                    still_failed.append((resource, parent_path))
                    
                # Small delay between retries
                time.sleep(2)
            
            # Update failed list
            self.failed_uploads = still_failed
            
            # Increase delay for next attempt (exponential backoff)
            retry_delay *= 2
        
        if self.failed_uploads:
            logger.warning(f"{len(self.failed_uploads)} file(s) still failed after {max_retry_attempts} retry attempts")
            for resource, _ in self.failed_uploads:
                logger.warning(f"  - {resource.get_name()}")

    def _process_resource(self, resource: Resource, parent_path: str) -> Optional[str]:
        """Recursively process a resource (file or directory).
        
        Args:
            resource: Resource to process
            parent_path: Path of the parent directory
            
        Returns:
            Resource ID if uploaded, None otherwise
        """
        self.total_files += 1
        
        # Check skip limit
        if self.total_files <= self.config.skip_files:
            logger.info(f"Skipping {resource.get_path()} (#{self.total_files})")
            self.skipped_files += 1
            return None
        
        # Check max files limit
        if self.config.max_files and self.uploaded_files >= self.config.max_files:
            logger.info(f"Reached max files limit ({self.config.max_files})")
            return None
        
        try:
            if resource.is_directory():
                return self._process_directory(resource, parent_path)
            else:
                return self._process_file(resource, parent_path)
        except Exception as e:
            logger.error(f"Failed to process {resource.get_path()}: {e}")
            self.failed_files += 1
            return None

    def _process_directory(self, directory: Resource, parent_path: str) -> Optional[str]:
        """Process a directory resource.
        
        Args:
            directory: Directory resource
            parent_path: Path of the parent
            
        Returns:
            Directory ID if created
        """
        logger.info(f"Processing directory: {directory.get_path()}")
        
        # Check if directory exists in repository
        dir_id = self.get_existing_resource_id(directory, parent_path)
        
        if dir_id is None and not self.config.list_only:
            # Create directory
            dir_id = self.create_directory(directory, parent_path)
        
        # Process children
        if self.config.recurse_directories:
            new_parent = f"{parent_path.rstrip('/')}/{directory.get_name()}"
            for child in directory.list_resources():
                self._process_resource(child, new_parent)
            
            # Post-process directory (e.g., finalize uploads)
            if dir_id and not self.config.list_only:
                self.post_process_directory(directory, dir_id)
        
        return dir_id

    def _process_file(self, file: Resource, parent_path: str) -> Optional[str]:
        """Process a file resource.
        
        Args:
            file: File resource
            parent_path: Path of the parent directory
            
        Returns:
            File ID if uploaded
        """
        logger.info(f"Processing file: {file.get_path()} ({file.length()} bytes)")
        
        # Check if file exists in repository
        existing_id = self.get_existing_resource_id(file, parent_path)
        
        if existing_id:
            if self.config.verify_checksums:
                # Verify checksum matches
                if self.verify_checksum(file, existing_id):
                    logger.info(f"File exists and checksum matches: {file.get_name()}")
                    self.skipped_files += 1
                    return existing_id
                else:
                    logger.warning(f"File exists but checksum differs: {file.get_name()}")
                    if not self.config.force_new:
                        self.skipped_files += 1
                        return existing_id
            else:
                logger.info(f"File already exists: {file.get_name()}")
                self.skipped_files += 1
                return existing_id
        
        if self.config.list_only:
            logger.info(f"Would upload: {file.get_path()}")
            return None
        
        # Upload the file
        file_id = self.upload_file(file, parent_path)
        
        if file_id:
            self.uploaded_files += 1
            self.uploaded_bytes += file.length()
            logger.info(f"Successfully uploaded: {file.get_name()}")
        else:
            # Track failed upload for retry
            self.failed_files += 1
            if hasattr(self, 'failed_uploads'):
                self.failed_uploads.append((file, parent_path))
        
        return file_id

    def _print_summary(self):
        """Print upload summary statistics."""
        logger.info("=" * 80)
        logger.info("Upload Summary")
        logger.info(f"Total files processed: {self.total_files}")
        logger.info(f"Files uploaded: {self.uploaded_files}")
        logger.info(f"Files skipped: {self.skipped_files}")
        logger.info(f"Files failed: {self.failed_files}")
        logger.info(f"Total bytes uploaded: {self.uploaded_bytes:,}")
        logger.info("=" * 80)

    @abstractmethod
    def validate_configuration(self) -> None:
        """Validate that configuration is sufficient for upload.
        
        Raises:
            UploaderException: If configuration is invalid
        """
        pass

    @abstractmethod
    def get_existing_resource_id(self, resource: Resource, parent_path: str) -> Optional[str]:
        """Check if resource already exists in the repository.
        
        Args:
            resource: Resource to check
            parent_path: Path of the parent directory
            
        Returns:
            Resource ID if exists, None otherwise
        """
        pass

    @abstractmethod
    def create_directory(self, directory: Resource, parent_path: str) -> str:
        """Create a directory in the repository.
        
        Args:
            directory: Directory resource
            parent_path: Path of the parent
            
        Returns:
            Created directory ID
        """
        pass

    @abstractmethod
    def upload_file(self, file: Resource, parent_path: str) -> Optional[str]:
        """Upload a file to the repository.
        
        Args:
            file: File resource
            parent_path: Path of the parent directory
            
        Returns:
            Uploaded file ID if successful, None otherwise
        """
        pass

    @abstractmethod
    def verify_checksum(self, file: Resource, file_id: str) -> bool:
        """Verify that uploaded file checksum matches local file.
        
        Args:
            file: Local file resource
            file_id: ID of file in repository
            
        Returns:
            True if checksums match, False otherwise
        """
        pass

    def post_process_directory(self, directory: Resource, dir_id: str) -> None:
        """Post-process a directory after children are uploaded.
        
        This can be overridden by subclasses for repository-specific operations.
        
        Args:
            directory: Directory resource
            dir_id: Directory ID
        """
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.http_client.close()