"""Custom exceptions for the Dataverse uploader."""


class UploaderException(Exception):
    """Base exception for all uploader-related errors."""

    pass


class AuthenticationError(UploaderException):
    """Raised when authentication fails."""

    pass


class UploadError(UploaderException):
    """Raised when file upload fails."""

    pass


class ResourceError(UploaderException):
    """Raised when there's an issue with resource handling."""

    pass


class MetadataError(UploaderException):
    """Raised when metadata processing fails."""

    pass


class ValidationError(UploaderException):
    """Raised when data validation fails."""

    pass


class HashMismatchError(UploaderException):
    """Raised when file hash verification fails."""

    pass


class DatasetLockedError(UploaderException):
    """Raised when attempting to upload to a locked dataset."""

    pass


class NetworkError(UploaderException):
    """Raised when network communication fails."""

    pass
