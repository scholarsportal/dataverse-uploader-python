"""Example: Programmatic upload to Dataverse."""

from pathlib import Path

from dataverse_uploader.core.config import UploaderConfig
from dataverse_uploader.uploaders.dataverse import DataverseUploader


def main():
    """Upload files programmatically."""
    
    # Configuration
    config = UploaderConfig(
        server_url="https://demo.dataverse.org",
        api_key="YOUR_API_KEY_HERE",
        dataset_pid="doi:10.5072/FK2/EXAMPLE",
        verify_checksums=True,
        recurse_directories=True,
        max_files=100,
        verbose=True,
    )
    
    # Files to upload
    upload_paths = [
        "data/experiment1.csv",
        "data/results/",
        "documentation/README.md",
    ]
    
    # Upload with context manager
    with DataverseUploader(config) as uploader:
        uploader.process_requests(upload_paths)
        
        # Print statistics
        print("\n" + "=" * 60)
        print("Upload Complete!")
        print("=" * 60)
        print(f"Files uploaded: {uploader.uploaded_files}")
        print(f"Files skipped: {uploader.skipped_files}")
        print(f"Files failed: {uploader.failed_files}")
        print(f"Total bytes: {uploader.uploaded_bytes:,}")
        print("=" * 60)


if __name__ == "__main__":
    main()
