# Dataverse Uploader - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI / Python API                          │
│                     (dataverse_uploader.cli)                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Configuration Layer                            │
│                  (UploaderConfig / Pydantic)                     │
│  - Environment variables  - .env files  - Validation            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Abstract Uploader Layer                        │
│                  (AbstractUploader ABC)                          │
│  - Template method pattern                                       │
│  - Resource processing workflow                                  │
│  - Statistics tracking                                           │
└────┬──────────────────┬──────────────────┬───────────────────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌──────────┐    ┌──────────────┐    ┌─────────────┐
│Dataverse │    │ SEAD/Clowder │    │   Custom    │
│ Uploader │    │   Uploader   │    │  Uploaders  │
└────┬─────┘    └──────┬───────┘    └──────┬──────┘
     │                 │                    │
     └─────────────────┴────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Resource Abstraction                          │
│                     (Resource ABC)                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │    File    │  │ Published  │  │    Bag     │               │
│  │  Resource  │  │  Resource  │  │  Resource  │               │
│  └────────────┘  └────────────┘  └────────────┘               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Utility Layer                               │
│  ┌───────────┐  ┌──────────┐  ┌────────┐  ┌────────────┐      │
│  │   HTTP    │  │ Hashing  │  │Metadata│  │  Progress  │      │
│  │  Client   │  │ Utilities│  │ Parser │  │  Tracking  │      │
│  └───────────┘  └──────────┘  └────────┘  └────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. CLI Layer (`cli.py`)
- **Purpose**: User interface via command line
- **Technologies**: Typer, Rich
- **Responsibilities**:
  - Parse command-line arguments
  - Display progress and results
  - Error handling and user feedback

### 2. Configuration Layer (`core/config.py`)
- **Purpose**: Centralized configuration management
- **Technologies**: Pydantic Settings
- **Responsibilities**:
  - Load config from env vars, .env files, or arguments
  - Validate configuration values
  - Type-safe configuration access

### 3. Abstract Uploader (`core/abstract_uploader.py`)
- **Purpose**: Template for all uploader implementations
- **Pattern**: Template Method, Strategy
- **Responsibilities**:
  - Define upload workflow
  - Track statistics
  - Process resources recursively
  - Provide extension points for specific implementations

### 4. Repository-Specific Uploaders
#### Dataverse Uploader (`uploaders/dataverse.py`)
- **Responsibilities**:
  - Dataverse API interaction
  - Direct S3 upload support
  - Multipart upload handling
  - Dataset lock management
  - File registration

#### SEAD Uploader (`uploaders/sead.py`)
- **Responsibilities**:
  - SEAD/Clowder API interaction
  - OAuth authentication
  - Collection/dataset creation
  - Metadata mapping

### 5. Resource Abstraction (`resources/`)
- **Purpose**: Unified interface for different resource types
- **Pattern**: Abstract Factory
- **Components**:
  - `Resource` (ABC): Base interface
  - `FileResource`: Local filesystem files
  - `PublishedResource`: Remote published content
  - `BagResource`: BagIt bag support
  - `ResourceFactory`: Factory for creating resources

### 6. Utility Layer (`utils/`)
#### HTTP Client (`http_client.py`)
- **Purpose**: Robust HTTP communication
- **Features**:
  - Connection pooling
  - Automatic retries with exponential backoff
  - Timeout handling
  - Streaming support

#### Other Utilities
- **Hashing**: File integrity verification
- **Metadata**: OAI-ORE, JSON-LD processing
- **Progress**: Upload progress tracking

## Data Flow

### Upload Process Flow

```
1. CLI Entry
   ↓
2. Load Configuration
   ↓
3. Create Uploader Instance
   ↓
4. Validate Configuration
   ↓
5. Load Dataset Metadata
   ↓
6. For each path:
   ├── Create Resource
   ├── Check if exists
   ├── If directory:
   │   ├── Create directory (virtual)
   │   └── Recurse into children
   └── If file:
       ├── Check checksum (if verify enabled)
       ├── Upload file (direct or traditional)
       └── Track statistics
   ↓
7. Post-process (e.g., register batch)
   ↓
8. Display summary
```

### File Upload Flow (Direct S3)

```
1. Request upload URLs from Dataverse
   ↓
2. Receive S3 presigned URL + storage identifier
   ↓
3. Upload file directly to S3
   ↓
4. Calculate file checksum
   ↓
5. Register file with Dataverse
   ├── Send storage identifier
   ├── Send checksum
   └── Send metadata
   ↓
6. Return file ID
```

## Key Design Patterns

### 1. Abstract Factory (Resources)
**Intent**: Create families of related objects (files, directories, bags) without specifying concrete classes.

```python
class ResourceFactory:
    @staticmethod
    def create(path: Path) -> Resource:
        if path.is_file():
            return FileResource(path)
        elif path.is_dir():
            return DirectoryResource(path)
        # ... other types
```

### 2. Template Method (Uploader)
**Intent**: Define skeleton of algorithm; subclasses override specific steps.

```python
class AbstractUploader(ABC):
    def process_requests(self, paths):
        # Template method - defines workflow
        self.validate_configuration()
        for path in paths:
            resource = self.create_resource(path)
            self.upload_resource(resource)  # Hook method
    
    @abstractmethod
    def upload_file(self, file):
        # Hook method - implemented by subclasses
        pass
```

### 3. Strategy (Repository-Specific Logic)
**Intent**: Define family of algorithms (Dataverse, SEAD) and make them interchangeable.

```python
# Client code
if repo_type == "dataverse":
    uploader = DataverseUploader(config)
elif repo_type == "sead":
    uploader = SEADUploader(config)

uploader.upload(files)  # Same interface, different strategy
```

### 4. Adapter (Resource Types)
**Intent**: Convert interface of class into another interface clients expect.

```python
class BagResource(Resource):
    """Adapts BagIt format to Resource interface"""
    def __init__(self, bag_path):
        self.bag = bagit.Bag(bag_path)
    
    def get_input_stream(self):
        # Adapt BagIt interface to Resource interface
        return self.bag.get_file(self.path)
```

## Error Handling Strategy

```
Exception Hierarchy:
└── UploaderException (base)
    ├── AuthenticationError
    ├── UploadError
    ├── ResourceError
    ├── MetadataError
    ├── ValidationError
    ├── HashMismatchError
    ├── DatasetLockedError
    └── NetworkError
```

**Error Handling Approach**:
1. **Network errors**: Automatic retry with exponential backoff
2. **Authentication errors**: Immediate failure with clear message
3. **Validation errors**: Early detection before upload starts
4. **Upload errors**: Log and continue with remaining files
5. **Critical errors**: Stop processing and report

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies (HTTP, filesystem)
- Focus on business logic

### Integration Tests
- Test interaction between components
- Use test doubles for external services
- Verify configuration loading

### End-to-End Tests
- Test against demo Dataverse instance
- Verify actual uploads and checksums
- Test error recovery

## Performance Considerations

### Connection Pooling
- Maintain pool of HTTP connections
- Reuse connections for multiple uploads
- Configurable pool size

### Concurrent Uploads
- Support multipart uploads with parallel parts
- Configurable concurrency level
- Thread-safe resource sharing

### Memory Management
- Stream large files (don't load entirely in memory)
- Chunked reading for hash calculation
- Limited reader for partial uploads

### Caching
- Cache calculated hashes
- Cache dataset metadata
- Avoid redundant API calls

## Security Considerations

1. **API Key Storage**:
   - Never log API keys
   - Support environment variables
   - Mask in error messages

2. **SSL/TLS**:
   - Verify certificates by default
   - Option to disable (testing only)
   - Use modern TLS versions

3. **Input Validation**:
   - Validate all configuration
   - Sanitize file paths
   - Check file sizes

4. **Checksum Verification**:
   - Calculate before upload
   - Verify after upload
   - Multiple algorithm support

## Extensibility Points

### Adding New Repository Types
1. Extend `AbstractUploader`
2. Implement abstract methods
3. Add repository-specific logic
4. Register in CLI or use programmatically

### Adding New Resource Types
1. Extend `Resource` ABC
2. Implement required methods
3. Add to `ResourceFactory` if needed
4. Use in uploader

### Custom Metadata Processing
1. Extend `MetadataProcessor`
2. Add custom mapping logic
3. Configure in uploader

### Custom Authentication
1. Extend `Authenticator` base
2. Implement authentication flow
3. Use in HTTP client
