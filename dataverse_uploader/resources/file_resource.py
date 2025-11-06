"""File resource implementation for local filesystem files."""

import hashlib
import mimetypes
from io import BufferedReader
from pathlib import Path
from typing import IO, Iterator, Optional

from dataverse_uploader.core.exceptions import ResourceError
from dataverse_uploader.resources.base import Resource, ResourceMetadata


class FileResource(Resource):
    """Resource implementation for local filesystem files and directories."""

    def __init__(self, path: Path | str, base_path: Optional[Path | str] = None):
        """Initialize a file resource.
        
        Args:
            path: Path to the file or directory
            base_path: Base path for calculating relative paths
        """
        super().__init__()
        self._path = Path(path).resolve()
        self._base_path = Path(base_path).resolve() if base_path else self._path.parent
        
        if not self._path.exists():
            raise ResourceError(f"Path does not exist: {self._path}")
        
        self._hash_cache: dict[str, str] = {}

    def get_name(self) -> str:
        """Get the file or directory name."""
        return self._path.name

    def is_directory(self) -> bool:
        """Check if this is a directory."""
        return self._path.is_dir()

    def get_path(self) -> str:
        """Get the relative path from the base path."""
        try:
            rel_path = self._path.relative_to(self._base_path)
            return str(rel_path)
        except ValueError:
            # Path is not relative to base_path
            return str(self._path)

    def get_absolute_path(self) -> str:
        """Get the absolute filesystem path."""
        return str(self._path)

    def length(self) -> int:
        """Get the file size in bytes."""
        if self.is_directory():
            raise ResourceError("Cannot get size of directory")
        return self._path.stat().st_size

    def get_input_stream(self, offset: int = 0, length: Optional[int] = None) -> IO[bytes]:
        """Open the file for reading.
        
        Args:
            offset: Starting byte position
            length: Number of bytes to read (None for all)
            
        Returns:
            File handle opened in binary read mode
        """
        if self.is_directory():
            raise ResourceError("Cannot open directory as stream")
        
        file_handle = open(self._path, "rb")
        
        if offset > 0:
            file_handle.seek(offset)
        
        if length is not None:
            # Wrap in a limited reader
            return LimitedReader(file_handle, length)
        
        return file_handle

    def list_resources(self) -> Iterator["FileResource"]:
        """List child resources if this is a directory.
        
        Yields:
            FileResource objects for each child
        """
        if not self.is_directory():
            return
        
        for child_path in sorted(self._path.iterdir()):
            # Skip hidden files and directories
            if child_path.name.startswith("."):
                continue
            yield FileResource(child_path, self._base_path)

    def get_hash(self, algorithm: str) -> str:
        """Calculate cryptographic hash of the file.
        
        Args:
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
            
        Returns:
            Hexadecimal hash string
        """
        if self.is_directory():
            raise ResourceError("Cannot hash directory")
        
        algo_lower = algorithm.lower().replace("-", "")
        
        # Return cached value if available
        if algo_lower in self._hash_cache:
            return self._hash_cache[algo_lower]
        
        # Calculate hash
        try:
            hasher = hashlib.new(algo_lower)
        except ValueError:
            raise ResourceError(f"Unsupported hash algorithm: {algorithm}")
        
        with open(self._path, "rb") as f:
            # Read in chunks to handle large files
            chunk_size = 8192
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        hash_value = hasher.hexdigest()
        self._hash_cache[algo_lower] = hash_value
        return hash_value

    def get_mimetype(self) -> str:
        """Determine the MIME type of the file.
        
        Returns:
            MIME type string or 'application/octet-stream' if unknown
        """
        if self.is_directory():
            return "inode/directory"
        
        mimetype, _ = mimetypes.guess_type(str(self._path))
        return mimetype or "application/octet-stream"

    def get_creation_time(self) -> float:
        """Get file creation timestamp."""
        return self._path.stat().st_ctime

    def get_modification_time(self) -> float:
        """Get file modification timestamp."""
        return self._path.stat().st_mtime


class LimitedReader(BufferedReader):
    """Wrapper that limits the number of bytes that can be read."""

    def __init__(self, file_handle: IO[bytes], limit: int):
        """Initialize limited reader.
        
        Args:
            file_handle: Underlying file handle
            limit: Maximum number of bytes to read
        """
        self._file = file_handle
        self._limit = limit
        self._position = 0

    def read(self, size: int = -1) -> bytes:
        """Read up to size bytes, respecting the limit."""
        if self._position >= self._limit:
            return b""
        
        if size < 0:
            size = self._limit - self._position
        else:
            size = min(size, self._limit - self._position)
        
        data = self._file.read(size)
        self._position += len(data)
        return data

    def close(self) -> None:
        """Close the underlying file."""
        self._file.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
