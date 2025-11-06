"""Abstract base class for resource handling."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO, Iterator, Optional

from pydantic import BaseModel


class ResourceMetadata(BaseModel):
    """Metadata associated with a resource."""

    title: Optional[str] = None
    description: Optional[str] = None
    mimetype: Optional[str] = None
    creation_date: Optional[str] = None
    size: Optional[int] = None
    additional: dict = {}

    class Config:
        extra = "allow"


class Resource(ABC):
    """Abstract base class for all resource types.
    
    This mirrors the Java Resource interface, providing a uniform
    way to handle local files, directories, and published content.
    """

    def __init__(self):
        """Initialize the resource."""
        self._metadata: Optional[ResourceMetadata] = None

    @abstractmethod
    def get_name(self) -> str:
        """Get the resource name."""
        pass

    @abstractmethod
    def is_directory(self) -> bool:
        """Check if this resource is a directory."""
        pass

    @abstractmethod
    def get_path(self) -> str:
        """Get the relative path of the resource."""
        pass

    @abstractmethod
    def get_absolute_path(self) -> str:
        """Get the absolute path of the resource."""
        pass

    @abstractmethod
    def length(self) -> int:
        """Get the size of the resource in bytes."""
        pass

    @abstractmethod
    def get_input_stream(self, offset: int = 0, length: Optional[int] = None) -> IO[bytes]:
        """Get an input stream for reading the resource.
        
        Args:
            offset: Starting byte offset
            length: Number of bytes to read (None for all remaining)
            
        Returns:
            File-like object for reading bytes
        """
        pass

    @abstractmethod
    def list_resources(self) -> Iterator["Resource"]:
        """List child resources (for directories).
        
        Yields:
            Child resources
        """
        pass

    @abstractmethod
    def get_hash(self, algorithm: str) -> str:
        """Calculate hash of the resource.
        
        Args:
            algorithm: Hash algorithm (md5, sha1, sha256, etc.)
            
        Returns:
            Hexadecimal hash string
        """
        pass

    @abstractmethod
    def get_mimetype(self) -> str:
        """Get the MIME type of the resource."""
        pass

    def get_metadata(self) -> Optional[ResourceMetadata]:
        """Get metadata associated with this resource."""
        return self._metadata

    def set_metadata(self, metadata: ResourceMetadata) -> None:
        """Set metadata for this resource."""
        self._metadata = metadata

    def __iter__(self) -> Iterator["Resource"]:
        """Make resource iterable over its children."""
        return self.list_resources()

    def __str__(self) -> str:
        """String representation of the resource."""
        return f"{self.__class__.__name__}(path={self.get_path()})"

    def __repr__(self) -> str:
        """Developer representation of the resource."""
        return (
            f"{self.__class__.__name__}(name={self.get_name()}, "
            f"is_dir={self.is_directory()}, size={self.length()})"
        )
