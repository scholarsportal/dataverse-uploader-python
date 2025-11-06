"""Abstract base class for repository uploaders with progress tracking."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    FileSizeColumn,
    TransferSpeedColumn,
)

from dataverse_uploader.core.config import UploaderConfig
from dataverse_uploader.core.exceptions import UploaderException
from dataverse_uploader.resources.base import Resource
from dataverse_uploader.resources.file_resource import FileResource
from dataverse_uploader.utils.http_client import HTTPClient

logger = logging.getLogger(__name__)
console = Console()


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
        
        # Progress tracking
        self.progress: Optional[Progress] = None
        self.upload_task: Optional[int] = None
        
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

    def _count_files_to_process(self, paths: list[str | Path]) -> int:
        """Count total files that will be processed.
        
        Args:
            paths: List of paths to process
            
        Returns:
            Total number of files
        """
        total = 0
        for path_str in paths:
            path = Path(path_str)
            if not path.exists():
                continue
            
            if path.is_file():
                total += 1
            elif path.is_dir() and self.config.recurse_directories:
                for item in path.rglob("*"):
                    if item.is_file() and not item.name.startswith("."):
                        total += 1
        return total

    def process_requests(self, paths: list[str | Path]) -> None:
        """Process upload requests for the given paths.
        
        Args:
            paths: List of file or directory paths to upload
        """
        console.print("\n[bold cyan]═" * 70)
        console.print(f"[bold cyan]Starting Upload Process")
        console.print(f"[cyan]Server:[/cyan] {self.config.server_url}")
        console.print(f"[cyan]Dataset:[/cyan] {self.config.dataset_pid}")
        if self.config.list_only:
            console.print("[yellow]LIST ONLY MODE - No files will be uploaded[/yellow]")
        console.print("[bold cyan]═" * 70 + "\n")
        
        # Track failed uploads for retry
        self.failed_uploads: list[tuple[Resource, str]] = []
        
        try:
            # Validate configuration
            self.validate_configuration()
            
            # Count total files
            total_files_to_process = self._count_files_to_process(paths)
            
            # Create progress bar
            if not self.config.list_only:
                self.progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TextColumn("•"),
                    FileSizeColumn(),
                    TextColumn("•"),
                    TransferSpeedColumn(),
                    TextColumn("•"),
                    TimeRemainingColumn(),
                    console=console,
                )
                
                with self.progress:
                    self.upload_task = self.progress.add_task(
                        "Uploading files...",
                        total=total_files_to_process
                    )
                    
                    # Process each path
                    for path_str in paths:
                        path = Path(path_str)
                        if not path.exists():
                            logger.warning(f"Path does not exist: {path}")
                            continue
                        
                        resource = FileResource(path)
                        self._process_resource(resource, parent_path="/")
                    
                    # Complete the progress bar
                    if self.upload_task is not None:
                        self.progress.update(self.upload_task, completed=total_files_to_process)
            else:
                # List only mode - no progress bar
                for path_str in paths:
                    path = Path(path_str)
                    if not path.exists():
                        logger.warning(f"Path does not exist: {path}")
                        continue
                    
                    resource = FileResource(path)
                    self._process_resource(resource, parent_path="/")
            
            # Retry failed uploads with delays
            if self.failed_uploads and not self.config.list_only:
                console.print()  # Add blank line
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
            
            console.print("[bold yellow]" + "═" * 70)
            console.print(f"[bold yellow]Retry Attempt {attempt}/{max_retry_attempts} for {len(self.failed_uploads)} failed file(s)")
            console.print(f"[yellow]Waiting {retry_delay} seconds for Dataverse to finish processing...")
            console.print("[bold yellow]" + "═" * 70 + "\n")
            
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
                console.print(f"[yellow]Retrying:[/yellow] {resource.get_name()}")
                
                # Check if it now exists (may have been processed)
                existing_id = self.get_existing_resource_id(resource, parent_path)
                if existing_id:
                    console.print(f"[green]✓[/green] File now exists (was being processed): {resource.get_name()}")
                    self.skipped_files += 1
                    self.failed_files -= 1  # It wasn't really failed, just processing
                    continue
                
                # Try uploading again
                file_id = self.upload_file(resource, parent_path)
                
                if file_id:
                    self.uploaded_files += 1
                    self.uploaded_bytes += resource.length()
                    self.failed_files -= 1
                    console.print(f"[green]✓[/green] Successfully uploaded on retry: {resource.get_name()}")
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
            console.print(f"\n[bold red]⚠[/bold red] {len(self.failed_uploads)} file(s) still failed after {max_retry_attempts} retry attempts")
            for resource, _ in self.failed_uploads:
                console.print(f"  [red]✗[/red] {resource.get_name()}")

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
        if not self.config.list_only:
            console.print(f"[cyan]📁 Processing directory:[/cyan] {directory.get_path()}")
        else:
            console.print(f"[dim]Would process directory: {directory.get_path()}[/dim]")
        
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
        # Format file size
        file_size = file.length()
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        if not self.config.list_only:
            console.print(f"[cyan]📄 Processing:[/cyan] {file.get_name()} [dim]({size_str})[/dim]")
        else:
            console.print(f"[dim]Would upload: {file.get_path()} ({size_str})[/dim]")
        
        # Check if file exists in repository
        existing_id = self.get_existing_resource_id(file, parent_path)
        
        if existing_id:
            if self.config.verify_checksums:
                # Verify checksum matches
                if self.verify_checksum(file, existing_id):
                    console.print(f"  [green]✓ Skipped:[/green] File exists with matching checksum")
                    self.skipped_files += 1
                    if self.progress and self.upload_task is not None:
                        self.progress.advance(self.upload_task)
                    return existing_id
                else:
                    console.print(f"  [yellow]⚠ Warning:[/yellow] File exists but checksum differs")
                    if not self.config.force_new:
                        self.skipped_files += 1
                        if self.progress and self.upload_task is not None:
                            self.progress.advance(self.upload_task)
                        return existing_id
            else:
                console.print(f"  [green]✓ Skipped:[/green] File already exists")
                self.skipped_files += 1
                if self.progress and self.upload_task is not None:
                    self.progress.advance(self.upload_task)
                return existing_id
        
        if self.config.list_only:
            return None
        
        # Upload the file
        file_id = self.upload_file(file, parent_path)
        
        if file_id:
            self.uploaded_files += 1
            self.uploaded_bytes += file.length()
            console.print(f"  [green]✓ Uploaded successfully[/green]")
            if self.progress and self.upload_task is not None:
                self.progress.advance(self.upload_task, advance=1)
        else:
            # Track failed upload for retry
            self.failed_files += 1
            console.print(f"  [red]✗ Upload failed[/red]")
            if hasattr(self, 'failed_uploads'):
                self.failed_uploads.append((file, parent_path))
            if self.progress and self.upload_task is not None:
                self.progress.advance(self.upload_task)
        
        return file_id

    def _print_summary(self):
        """Print upload summary statistics."""
        console.print("\n[bold green]" + "═" * 70)
        console.print("[bold green]Upload Summary")
        console.print("═" * 70)
        
        console.print(f"[cyan]Total files processed:[/cyan] {self.total_files}")
        console.print(f"[green]Files uploaded:[/green] {self.uploaded_files}")
        console.print(f"[yellow]Files skipped:[/yellow] {self.skipped_files}")
        
        if self.failed_files > 0:
            console.print(f"[red]Files failed:[/red] {self.failed_files}")
        
        # Format uploaded bytes
        uploaded_mb = self.uploaded_bytes / (1024 * 1024)
        if uploaded_mb < 1:
            uploaded_kb = self.uploaded_bytes / 1024
            console.print(f"[cyan]Total bytes uploaded:[/cyan] {uploaded_kb:.1f} KB")
        else:
            console.print(f"[cyan]Total bytes uploaded:[/cyan] {uploaded_mb:.1f} MB")
        
        console.print("[bold green]" + "═" * 70 + "\n")

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