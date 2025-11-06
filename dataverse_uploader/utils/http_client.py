"""HTTP client utilities with connection pooling and retry logic."""

import logging
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from dataverse_uploader.core.config import UploaderConfig
from dataverse_uploader.core.exceptions import AuthenticationError, NetworkError

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client with connection pooling and retry logic."""

    def __init__(self, config: UploaderConfig):
        """Initialize the HTTP client.
        
        Args:
            config: Uploader configuration
        """
        self.config = config
        self.api_key = config.api_key
        
        # Create httpx client with connection pooling
        limits = httpx.Limits(
            max_keepalive_connections=config.http_concurrency,
            max_connections=config.http_concurrency * 2,
        )
        
        timeout = httpx.Timeout(
            timeout=config.timeout_seconds,
            connect=30.0,
            read=config.timeout_seconds,
        )
        
        verify = not config.trust_all_certs
        
        self._client = httpx.Client(
            limits=limits,
            timeout=timeout,
            verify=verify,
            follow_redirects=True,
        )
        
        # Set default headers
        self._client.headers.update({
            "User-Agent": "dataverse-uploader-python/1.3.0",
        })

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _add_auth_header(self, headers: Optional[dict[str, str]] = None) -> dict[str, str]:
        """Add authentication header if API key is available.
        
        Args:
            headers: Existing headers dictionary
            
        Returns:
            Headers with authentication added
        """
        headers = headers or {}
        if self.api_key:
            headers["X-Dataverse-key"] = self.api_key
        return headers

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
    )
    def get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        """Send GET request with retry logic.
        
        Args:
            url: Request URL
            params: Query parameters
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            NetworkError: If request fails after retries
        """
        try:
            headers = self._add_auth_header(headers)
            response = self._client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed - check API key")
            raise NetworkError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(f"Network error: {str(e)}")

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
    )
    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        """Send POST request with retry logic.
        
        Args:
            url: Request URL
            data: Form data
            json: JSON payload
            files: Files to upload
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            NetworkError: If request fails after retries
        """
        try:
            headers = self._add_auth_header(headers)
            response = self._client.post(
                url, data=data, json=json, files=files, headers=headers
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed - check API key")
            raise NetworkError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(f"Network error: {str(e)}")

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
    )
    def put(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[dict] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        """Send PUT request with retry logic.
        
        Args:
            url: Request URL
            data: Request body
            json: JSON payload
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            NetworkError: If request fails after retries
        """
        try:
            headers = self._add_auth_header(headers)
            response = self._client.put(url, data=data, json=json, headers=headers)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed - check API key")
            raise NetworkError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(f"Network error: {str(e)}")

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
    )
    def delete(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        """Send DELETE request with retry logic.
        
        Args:
            url: Request URL
            headers: Additional headers
            
        Returns:
            HTTP response
            
        Raises:
            NetworkError: If request fails after retries
        """
        try:
            headers = self._add_auth_header(headers)
            response = self._client.delete(url, headers=headers)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed - check API key")
            raise NetworkError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(f"Network error: {str(e)}")

    def stream_get(self, url: str, headers: Optional[dict[str, str]] = None):
        """Stream GET request (for large downloads).
        
        Args:
            url: Request URL
            headers: Additional headers
            
        Yields:
            Response chunks
        """
        headers = self._add_auth_header(headers)
        with self._client.stream("GET", url, headers=headers) as response:
            response.raise_for_status()
            yield from response.iter_bytes(chunk_size=8192)

    def upload_multipart(
        self,
        url: str,
        file_stream: Any,
        chunk_size: int = 5 * 1024 * 1024,
    ) -> httpx.Response:
        """Upload file using multipart upload.
        
        Args:
            url: Pre-signed upload URL
            file_stream: File-like object
            chunk_size: Size of each chunk
            
        Returns:
            HTTP response
        """
        response = self._client.put(
            url,
            content=file_stream,
            headers={"Content-Type": "application/octet-stream"},
        )
        response.raise_for_status()
        return response
