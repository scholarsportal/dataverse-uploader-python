# Dataverse Uploader (Python)

A Python implementation of the DVUploader command-line bulk uploader for Dataverse repositories. This tool provides efficient bulk file uploads with features like checksum verification, resume capability, and direct S3 uploads.

## Features

- **Bulk uploads**: Upload hundreds or thousands of files efficiently
- **Direct upload**: Direct-to-S3 uploads when enabled on the server
- **Checksum verification**: MD5, SHA-1, SHA-256, SHA-512 support
- **Resume capability**: Skip already uploaded files automatically
- **Recursive directory processing**: Upload entire directory trees
- **Connection pooling**: Efficient HTTP connection management
- **Retry logic**: Automatic retry with exponential backoff
- **Progress tracking**: Real-time upload statistics
- **Flexible configuration**: Environment variables, CLI arguments, or config files

## Architecture

### Package Structure

```
dataverse_uploader/
├── core/
│   ├── abstract_uploader.py    # Base uploader with core logic
│   ├── config.py                # Configuration management (Pydantic)
│   └── exceptions.py            # Custom exception hierarchy
├── resources/
│   ├── base.py                  # Abstract Resource interface
│   ├── file_resource.py         # Local file/directory handling
│   ├── published_resource.py    # Published content (BagIt)
│   └── resource_factory.py      # Resource creation patterns
├── uploaders/
│   ├── dataverse.py             # Dataverse-specific implementation
│   └── sead.py                  # SEAD/Clowder implementation
├── utils/
│   ├── http_client.py           # HTTP session with pooling & retries
│   ├── hashing.py               # File integrity utilities
│   ├── metadata.py              # Metadata processing
│   └── progress.py              # Progress tracking
└── cli.py                       # Command-line interface
```

### Design Patterns

**Abstract Factory Pattern**: `Resource` abstraction allows uniform handling of local files, remote files, and BagIt bags.

**Strategy Pattern**: `AbstractUploader` defines the upload algorithm; specific implementations (`DataverseUploader`, `SEADUploader`) provide repository-specific strategies.

**Template Method Pattern**: `AbstractUploader.process_requests()` defines the workflow; subclasses implement specific steps like `upload_file()` and `create_directory()`.

**Configuration as Code**: Pydantic models for type-safe configuration with validation.

## Installation

### From Source

```bash
git clone https://github.com/your-org/dataverse-uploader-python.git
cd dataverse-uploader-python
pip install -e .
```

### Using pip (when published)

```bash
pip install dataverse-uploader
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

Basic upload:

```bash
dv-upload my_data.csv \
  --server https://dataverse.example.org \
  --key YOUR_API_KEY \
  --dataset doi:10.5072/FK2/ABCDEF
```

Upload directory recursively:

```bash
dv-upload research_data/ \
  --server https://dataverse.example.org \
  --key YOUR_API_KEY \
  --dataset doi:10.5072/FK2/ABCDEF \
  --recurse
```

With checksum verification:

```bash
dv-upload data/ \
  -s https://dataverse.example.org \
  -k YOUR_API_KEY \
  -d doi:10.5072/FK2/ABCDEF \
  --verify \
  --recurse
```

List files without uploading:

```bash
dv-upload data/ \
  -s https://dataverse.example.org \
  -k YOUR_API_KEY \
  -d doi:10.5072/FK2/ABCDEF \
  --list-only \
  --recurse
```

### Environment Variables

Create a `.env` file:

```bash
DV_SERVER_URL=https://dataverse.example.org
DV_API_KEY=your-api-key-here
DV_DATASET_PID=doi:10.5072/FK2/ABCDEF
```

Then simply:

```bash
dv-upload data/ --recurse
```

### Python API

```python
from pathlib import Path
from dataverse_uploader.core.config import UploaderConfig
from dataverse_uploader.uploaders.dataverse import DataverseUploader

# Configure uploader
config = UploaderConfig(
    server_url="https://dataverse.example.org",
    api_key="your-api-key",
    dataset_pid="doi:10.5072/FK2/ABCDEF",
    verify_checksums=True,
    recurse_directories=True,
)

# Upload files
with DataverseUploader(config) as uploader:
    uploader.process_requests(["data/file1.csv", "data/dir1/"])
    
    print(f"Uploaded: {uploader.uploaded_files} files")
    print(f"Skipped: {uploader.skipped_files} files")
    print(f"Total bytes: {uploader.uploaded_bytes:,}")
```

## Configuration Options

| Option | CLI Flag | Environment Variable | Default | Description |
|--------|----------|---------------------|---------|-------------|
| Server URL | `--server` | `DV_SERVER_URL` | - | Dataverse server URL |
| API Key | `--key` | `DV_API_KEY` | - | Authentication API key |
| Dataset PID | `--dataset` | `DV_DATASET_PID` | - | Dataset DOI |
| Verify Checksums | `--verify` | `DV_VERIFY_CHECKSUMS` | `false` | Verify file integrity |
| Recurse | `--recurse` | `DV_RECURSE_DIRECTORIES` | `false` | Process subdirectories |
| Direct Upload | `--traditional` | `DV_DIRECT_UPLOAD` | `true` | Use S3 direct upload |
| Skip Files | `--skip N` | `DV_SKIP_FILES` | `0` | Number of files to skip |
| Max Files | `--limit N` | `DV_MAX_FILES` | `None` | Maximum files to upload |
| Fixity Algorithm | `--fixity` | `DV_FIXITY_ALGORITHM` | `MD5` | Hash algorithm |
| Timeout | - | `DV_TIMEOUT_SECONDS` | `1200` | Request timeout (seconds) |
| HTTP Concurrency | - | `DV_HTTP_CONCURRENCY` | `4` | Concurrent connections |

## Architecture Comparison: Java → Python

### Core Concepts Preserved

| Java | Python | Notes |
|------|--------|-------|
| `AbstractUploader` | `AbstractUploader` | Template method pattern |
| `Resource` interface | `Resource` ABC | Abstract base class |
| `FileResource` | `FileResource` | Concrete implementation |
| `DVUploader` | `DataverseUploader` | Dataverse-specific logic |
| Apache HttpClient | `httpx` | Modern async-capable client |
| Maven `pom.xml` | `pyproject.toml` | Build configuration |
| Properties files | Pydantic Settings | Type-safe configuration |

### Python Advantages

1. **Type Safety**: Pydantic models provide runtime validation
2. **Async Ready**: Built on httpx for future async support
3. **Better Error Handling**: Rich exception hierarchy
4. **Modern Tooling**: Black, Ruff, MyPy for code quality
5. **Rich CLI**: Beautiful terminal output with progress bars
6. **Simpler Deployment**: No JVM required

### Key Differences

- **Configuration**: Pydantic Settings vs Java Properties
- **HTTP Client**: httpx vs Apache HttpComponents
- **JSON**: orjson (fast) vs org.json
- **CLI**: Typer vs custom argument parsing
- **Packaging**: Python wheel vs Maven JAR

## Development

### Setup Development Environment

```bash
git clone https://github.com/your-org/dataverse-uploader-python.git
cd dataverse-uploader-python
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov=dataverse_uploader --cov-report=html
```

### Code Quality

```bash
# Format code
black dataverse_uploader tests

# Lint
ruff check dataverse_uploader tests

# Type check
mypy dataverse_uploader
```

## Extending the Uploader

### Adding a New Repository Type

1. Create a new uploader class in `uploaders/`:

```python
from dataverse_uploader.core.abstract_uploader import AbstractUploader

class MyRepoUploader(AbstractUploader):
    def validate_configuration(self) -> None:
        # Validate config
        pass
    
    def upload_file(self, file, parent_path) -> Optional[str]:
        # Upload implementation
        pass
    
    # Implement other abstract methods...
```

2. Register in CLI or use programmatically

### Adding New Resource Types

Extend `Resource` base class:

```python
from dataverse_uploader.resources.base import Resource

class URLResource(Resource):
    def __init__(self, url: str):
        self.url = url
    
    def get_input_stream(self):
        # Stream from URL
        pass
    
    # Implement other methods...
```

## Troubleshooting

### Connection Errors

```bash
# Trust all certificates (testing only!)
dv-upload data/ ... --trust-all
```

### Large Files

```bash
# Increase timeout
export DV_TIMEOUT_SECONDS=3600
dv-upload large_file.zip ...
```

### Dataset Locked

The uploader automatically waits for locks to clear. Adjust wait time:

```bash
export DV_MAX_WAIT_LOCK_SECONDS=300
```

## License

Apache License 2.0

## Credits

Python implementation inspired by the original Java DVUploader developed by:
- Texas Digital Library
- Global Dataverse Community Consortium
- University of Michigan
- NCSA/SEAD Project

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code passes quality checks
5. Submit a pull request

## Support

- Issues: https://github.com/your-org/dataverse-uploader-python/issues
- Wiki: https://github.com/your-org/dataverse-uploader-python/wiki
- Dataverse Community: https://dataverse.org
