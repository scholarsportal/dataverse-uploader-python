# Large File Generator - Documentation

## Overview

The **Large File Generator** is a Python script designed to create test files of various sizes and formats for testing the Dataverse Uploader. It generates realistic data files that can be used to test upload performance, chunking, error handling, and large file management.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [File Types](#file-types)
- [Size Categories](#size-categories)
- [Custom Generation](#custom-generation)
- [Advanced Usage](#advanced-usage)
- [Testing Scenarios](#testing-scenarios)
- [Performance Notes](#performance-notes)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Features

### Core Capabilities

- ✅ **Multiple File Types**: CSV, JSON, text, binary, and log files
- ✅ **Flexible Sizing**: From 1 MB to 1+ GB files
- ✅ **Realistic Data**: Synthetic but representative data patterns
- ✅ **Progress Tracking**: Real-time progress indicators
- ✅ **Memory Efficient**: Streams large files without loading into memory
- ✅ **Nested Structures**: Creates complex directory hierarchies
- ✅ **Interactive Menu**: User-friendly command-line interface
- ✅ **Summary Reports**: Detailed generation statistics

### Supported File Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| CSV | `.csv` | Tabular data, datasets |
| JSON | `.json` | Structured data, API responses |
| Text | `.txt` | Documents, logs, plain text |
| Binary | `.bin` | Binary data, images, media |
| Log | `.log` | Server logs, application logs |

## Installation

### Prerequisites

- Python 3.9 or higher
- No external dependencies (uses only Python standard library)

### Setup

1. **Download the script**:
   ```bash
   cd examples
   # Copy generate_large_files.py to this directory
   ```

2. **Make it executable** (optional, Unix/Linux):
   ```bash
   chmod +x generate_large_files.py
   ```

3. **Verify installation**:
   ```bash
   python generate_large_files.py
   ```

## Quick Start

### Generate Demo Files (Fastest)

```bash
python generate_large_files.py
# Select option 0 (Quick demo)
```

This creates three small files (~15 MB total) in the `data/` directory:
- `demo_data.csv` - 10,000 rows
- `demo_logs.json` - 5,000 records  
- `demo_text.txt` - 5 MB

### Upload Demo Files

```bash
cd ..
dv-upload data/ --recurse --verify --list-only
```

## Usage Guide

### Interactive Mode

Run the script and follow the prompts:

```bash
python generate_large_files.py
```

**Menu Options:**

```
Select files to generate:

Size Categories:
  1. Small files (1-10 MB) - Quick tests
  2. Medium files (10-100 MB) - Standard tests
  3. Large files (100-500 MB) - Stress tests
  4. Extra large files (500+ MB) - Maximum stress
  5. All sizes - Complete test suite
  6. Custom - Specify your own

  0. Quick demo (small files only)

Enter choice (0-6):
```

### Command Flow

1. **Launch script**
   ```bash
   python generate_large_files.py
   ```

2. **Select option** (0-6)

3. **Wait for generation**
   - Progress indicators show completion percentage
   - Files are created in `data/` directory

4. **Review summary**
   - Total files created
   - Total size
   - List of all files

## File Types

### 1. CSV Files

**Purpose**: Test tabular data uploads, Dataverse's tabular file ingestion.

**Characteristics**:
- Configurable rows and columns
- Mixed data types (integers, floats, text, dates)
- Proper CSV formatting with headers
- Comma-separated values

**Generation Parameters**:
```python
create_large_csv_file(
    filename="data.csv",
    num_rows=100000,      # Number of data rows
    num_columns=10        # Number of columns
)
```

**Sample Output**:
```csv
column_0,column_1,column_2,column_3,column_4,...
0,text_1234,456.789,12345,2024-03-15 10:23:45,...
1,text_5678,789.012,67890,2024-06-20 14:56:12,...
```

**Use Cases**:
- Testing Dataverse tabular ingestion
- Verifying CSV → TAB conversion
- Testing with different row counts
- Performance benchmarking

### 2. JSON Files

**Purpose**: Test structured data uploads, API response formats.

**Characteristics**:
- Valid JSON array of objects
- Nested structures
- Mixed data types
- Pretty-printed formatting

**Generation Parameters**:
```python
create_large_json_file(
    filename="logs.json",
    num_records=10000     # Number of JSON objects
)
```

**Sample Output**:
```json
[
  {
    "id": 0,
    "timestamp": "2024-11-06T10:30:45.123456",
    "user": "user_1234",
    "value": 456.789,
    "status": "active",
    "metadata": {
      "key1": 42,
      "key2": "value_789",
      "key3": [0.123, 0.456, 0.789, 0.012, 0.345]
    },
    "description": "Random text data..."
  },
  ...
]
```

**Use Cases**:
- Testing JSON file uploads
- API response simulation
- Nested data structures
- Metadata testing

### 3. Text Files

**Purpose**: Test plain text uploads, document processing.

**Characteristics**:
- Random text content
- Mixed characters (letters, numbers, punctuation)
- Natural line breaks
- UTF-8 encoding

**Generation Parameters**:
```python
create_large_text_file(
    filename="document.txt",
    size_mb=50            # Target size in megabytes
)
```

**Use Cases**:
- Testing large document uploads
- Text file processing
- Encoding verification
- Chunked upload testing

### 4. Binary Files

**Purpose**: Test non-text file uploads, binary data handling.

**Characteristics**:
- Random binary data
- No text encoding
- Exact byte size control
- OS-level random data

**Generation Parameters**:
```python
create_binary_file(
    filename="data.bin",
    size_mb=100           # Target size in megabytes
)
```

**Use Cases**:
- Testing binary file uploads
- Simulating images/media
- Checksum verification
- Direct upload testing

### 5. Log Files

**Purpose**: Test server log uploads, line-based file processing.

**Characteristics**:
- Structured log format
- Timestamp for each line
- Log levels (DEBUG, INFO, WARN, ERROR, CRITICAL)
- Service names and request IDs

**Generation Parameters**:
```python
create_log_file(
    filename="server.log",
    num_lines=100000      # Number of log lines
)
```

**Sample Output**:
```
[2024-11-06T10:30:45.123456] INFO     api        | Operation 0 completed with status 200 - request_id=12345
[2024-11-06T10:30:46.234567] DEBUG    database   | Operation 1 completed with status 201 - request_id=23456
[2024-11-06T10:30:47.345678] ERROR    cache      | Operation 2 completed with status 500 - request_id=34567
```

**Use Cases**:
- Testing log file ingestion
- Line-by-line processing
- Large text file uploads
- Timestamp handling

### 6. Nested Directory Structures

**Purpose**: Test recursive directory uploads, folder hierarchy preservation.

**Characteristics**:
- Multiple directory levels
- Files at each level
- Configurable depth and density
- Automatic structure creation

**Generation Parameters**:
```python
create_nested_directory_structure(
    base_name="nested_files",
    depth=3,              # Number of nested levels
    files_per_dir=5,      # Files in each directory
    file_size_kb=500      # Size of each file
)
```

**Sample Structure**:
```
data/nested_files/
├── file_1_0.txt
├── file_1_1.txt
├── file_1_2.txt
├── level_2/
│   ├── file_2_0.txt
│   ├── file_2_1.txt
│   └── level_3/
│       ├── file_3_0.txt
│       └── file_3_1.txt
```

**Use Cases**:
- Testing `--recurse` flag
- Directory structure preservation
- Path handling
- Batch uploads

## Size Categories

### Option 0: Quick Demo (~15 MB)

**Purpose**: Fast verification that uploader works.

**Files Generated**:
- `demo_data.csv` - 10,000 rows → ~2 MB
- `demo_logs.json` - 5,000 records → ~8 MB
- `demo_text.txt` - 5 MB

**Generation Time**: ~10 seconds

**Use Case**: 
```bash
# Quick smoke test
python generate_large_files.py  # Select 0
dv-upload data/ --recurse --verify
```

### Option 1: Small Files (1-10 MB, ~30 MB total)

**Purpose**: Quick tests, development iteration.

**Files Generated**:
- `small_data.csv` - 50,000 rows → ~10 MB
- `small_logs.json` - 10,000 records → ~5 MB
- `small_document.txt` - 5 MB
- `small_binary.bin` - 3 MB
- `small_server.log` - 100,000 lines → ~8 MB

**Generation Time**: ~30 seconds

**Use Cases**:
- Feature development
- Quick testing cycles
- CI/CD pipeline tests
- Basic functionality verification

### Option 2: Medium Files (10-100 MB, ~250 MB total)

**Purpose**: Standard testing, realistic file sizes.

**Files Generated**:
- `medium_data.csv` - 500,000 rows → ~50 MB
- `medium_logs.json` - 100,000 records → ~40 MB
- `medium_document.txt` - 50 MB
- `medium_binary.bin` - 30 MB
- `medium_server.log` - 1,000,000 lines → ~75 MB

**Generation Time**: ~3-5 minutes

**Use Cases**:
- Standard testing
- Performance benchmarking
- Chunked upload verification
- Direct vs traditional upload comparison

### Option 3: Large Files (100-500 MB, ~1 GB total)

**Purpose**: Stress testing, performance evaluation.

**Files Generated**:
- `large_data.csv` - 2,000,000 rows → ~200 MB
- `large_logs.json` - 500,000 records → ~180 MB
- `large_document.txt` - 200 MB
- `large_binary.bin` - 150 MB
- `large_server.log` - 5,000,000 lines → ~350 MB

**Generation Time**: ~10-15 minutes

**Use Cases**:
- Stress testing
- Multipart upload testing
- Timeout handling
- Memory management verification
- S3 direct upload testing

### Option 4: Extra Large Files (500+ MB, ~2 GB total)

**Purpose**: Maximum stress testing, edge case handling.

**Files Generated**:
- `xlarge_data.csv` - 5,000,000 rows → ~500 MB
- `xlarge_logs.json` - 1,000,000 records → ~400 MB
- `xlarge_document.txt` - 500 MB
- `xlarge_binary.bin` - 600 MB
- `xlarge_server.log` - 10,000,000 lines → ~700 MB

**Generation Time**: ~20-30 minutes

**Use Cases**:
- Maximum capacity testing
- Long-running upload tests
- Network resilience testing
- Dataset lock handling
- Server performance limits

### Option 5: All Sizes (Complete Test Suite, ~3 GB total)

**Purpose**: Comprehensive testing across all file sizes.

**Files Generated**:
- Small: `small_data.csv`, `small_document.txt`
- Medium: `medium_data.csv`, `medium_logs.json`
- Large: `large_data.csv`, `large_binary.bin`
- Extra Large: `xlarge_document.txt`, `xlarge_server.log`
- Nested: `nested_files/` directory structure

**Generation Time**: ~30-45 minutes

**Use Cases**:
- Pre-release testing
- Full regression testing
- Performance benchmarking suite
- Documentation examples

## Custom Generation

### Option 6: Custom Files

**Purpose**: Generate files with specific parameters for targeted testing.

### CSV Custom Generation

```bash
python generate_large_files.py
# Select: 6
# File type: csv
# Filename: custom_data.csv
# Number of rows: 1000000
# Number of columns: 20
```

**Use Cases**:
- Test specific row counts
- Test wide tables (many columns)
- Replicate production data patterns
- Edge case testing

### JSON Custom Generation

```bash
python generate_large_files.py
# Select: 6
# File type: json
# Filename: custom_api_response.json
# Number of records: 50000
```

**Use Cases**:
- API response simulation
- Specific record count testing
- JSON structure validation

### Text Custom Generation

```bash
python generate_large_files.py
# Select: 6
# File type: text
# Filename: custom_document.txt
# Size in MB: 250
```

**Use Cases**:
- Specific size requirements
- Documentation file testing
- Text processing benchmarks

### Binary Custom Generation

```bash
python generate_large_files.py
# Select: 6
# File type: binary
# Filename: custom_image.bin
# Size in MB: 500
```

**Use Cases**:
- Simulate image/video files
- Test binary data handling
- Checksum verification

### Log Custom Generation

```bash
python generate_large_files.py
# Select: 6
# File type: log
# Filename: custom_application.log
# Number of lines: 5000000
```

**Use Cases**:
- Application log simulation
- Line-based processing
- Timestamp handling

## Advanced Usage

### Programmatic Usage

You can import and use the generator in your own scripts:

```python
from generate_large_files import LargeFileGenerator

# Create generator
generator = LargeFileGenerator(output_dir="test_data")

# Generate specific files
generator.create_large_csv_file("dataset.csv", num_rows=100000, num_columns=15)
generator.create_large_json_file("api_logs.json", num_records=50000)
generator.create_large_text_file("document.txt", size_mb=100)

# Create nested structure
generator.create_nested_directory_structure(
    base_name="complex_structure",
    depth=5,
    files_per_dir=10,
    file_size_kb=1024
)
```

### Batch Generation Script

Create multiple file sets programmatically:

```python
from generate_large_files import LargeFileGenerator

generator = LargeFileGenerator(output_dir="batch_data")

# Generate multiple datasets
for i in range(5):
    generator.create_large_csv_file(
        f"dataset_{i}.csv",
        num_rows=100000 * (i + 1),
        num_columns=10
    )

# Generate time-series data
for day in range(7):
    generator.create_log_file(
        f"logs_day_{day}.log",
        num_lines=100000
    )
```

### Integration with Testing

```python
import pytest
from generate_large_files import LargeFileGenerator
from dataverse_uploader.uploaders.dataverse import DataverseUploader

@pytest.fixture
def test_files(tmp_path):
    """Generate test files for each test."""
    generator = LargeFileGenerator(output_dir=str(tmp_path))
    generator.create_large_csv_file("test.csv", num_rows=1000, num_columns=5)
    return tmp_path

def test_csv_upload(test_files, uploader):
    """Test CSV file upload."""
    csv_file = test_files / "test.csv"
    assert csv_file.exists()
    
    result = uploader.upload_file(csv_file, "/")
    assert result is not None
```

## Testing Scenarios

### Scenario 1: Quick Functionality Test

**Goal**: Verify basic upload works

```bash
# Generate small files
python generate_large_files.py  # Select 0

# Test list mode
dv-upload data/ --list-only --recurse

# Upload
dv-upload data/ --recurse

# Verify
dv-upload data/ --recurse --verify  # Should skip all
```

**Expected Result**: All files uploaded successfully, second run skips everything.

### Scenario 2: Checksum Verification

**Goal**: Test MD5 hash verification

```bash
# Generate medium files
python generate_large_files.py  # Select 2

# Upload with verification
dv-upload data/ --recurse --verify

# Try uploading again
dv-upload data/ --recurse --verify
```

**Expected Result**: 
- First upload: Files uploaded with checksum calculation
- Second upload: All files skipped (checksum matches)

### Scenario 3: Direct vs Traditional Upload

**Goal**: Compare upload methods

```bash
# Generate large files
python generate_large_files.py  # Select 3

# Test direct upload (S3)
time dv-upload data/large_binary.bin --verify

# Delete file from dataset
# ...

# Test traditional upload
time dv-upload data/large_binary.bin --verify --traditional
```

**Expected Result**: Compare upload times and methods.

### Scenario 4: Multipart Upload

**Goal**: Test chunked uploads for large files

```bash
# Generate extra large files
python generate_large_files.py  # Select 4

# Upload with default chunk size
dv-upload data/xlarge_binary.bin --verify

# Monitor logs for multipart behavior
```

**Expected Result**: File uploaded in multiple parts (check logs).

### Scenario 5: Recursive Directory Upload

**Goal**: Test directory structure preservation

```bash
# Generate nested structure
python generate_large_files.py  # Select 5

# Upload nested directory
dv-upload data/nested_files/ --recurse

# Verify structure preserved in Dataverse
```

**Expected Result**: Directory hierarchy maintained in Dataverse.

### Scenario 6: Resume After Failure

**Goal**: Test upload resume capability

```bash
# Generate all sizes
python generate_large_files.py  # Select 5

# Start upload (interrupt after a few files)
dv-upload data/ --recurse --verify
# Press Ctrl+C

# Resume upload
dv-upload data/ --recurse --verify
```

**Expected Result**: Already-uploaded files skipped, new files uploaded.

### Scenario 7: Dataset Lock Handling

**Goal**: Test behavior when dataset is locked

```bash
# Generate medium files
python generate_large_files.py  # Select 2

# Start first upload (don't wait for completion)
dv-upload data/ --recurse &

# Start second upload immediately
dv-upload data/ --recurse
```

**Expected Result**: Second upload waits for lock or handles gracefully.

### Scenario 8: Network Resilience

**Goal**: Test retry logic and error handling

```bash
# Generate large files
python generate_large_files.py  # Select 3

# Upload with network issues
# (Simulate by disconnecting/reconnecting network during upload)
dv-upload data/ --recurse --verify
```

**Expected Result**: Automatic retries succeed after network restores.

## Performance Notes

### Generation Times (Approximate)

| Option | Total Size | Generation Time | Files Created |
|--------|------------|-----------------|---------------|
| 0 (Demo) | ~15 MB | 10 seconds | 3 |
| 1 (Small) | ~30 MB | 30 seconds | 5 |
| 2 (Medium) | ~250 MB | 3-5 minutes | 5 |
| 3 (Large) | ~1 GB | 10-15 minutes | 5 |
| 4 (XL) | ~2 GB | 20-30 minutes | 5 |
| 5 (All) | ~3 GB | 30-45 minutes | 10+ |

### Memory Usage

- **CSV/JSON Generation**: ~50-100 MB RAM (batch processing)
- **Text Generation**: ~20 MB RAM (streaming)
- **Binary Generation**: ~10 MB RAM (streaming)
- **Log Generation**: ~30 MB RAM (batch processing)

### Disk Space Requirements

Always ensure sufficient disk space:

```bash
# Check available space
df -h .

# For "All Sizes" option: Need at least 4 GB free
# For custom large files: Add 20% overhead
```

### Optimization Tips

1. **Use SSD**: Faster write speeds improve generation time
2. **Close Other Apps**: Reduce I/O contention
3. **Batch Mode**: Generate overnight for large datasets
4. **Custom Sizes**: Start small, increase as needed

## Troubleshooting

### Problem: Generation is Too Slow

**Symptoms**: 
- Takes much longer than expected
- Progress stalls

**Solutions**:
```bash
# Check disk space
df -h .

# Check disk I/O
iostat -x 1

# Try smaller batch size (edit script):
batch_size = 1000  # Reduce from 10000

# Use faster disk (SSD if available)
```

### Problem: Out of Memory Error

**Symptoms**:
```
MemoryError: Unable to allocate array
```

**Solutions**:
```bash
# Reduce batch size in script
# For CSV: batch_size = 1000
# For JSON: batch_size = 500

# Close other applications
# Generate smaller files first
```

### Problem: Permission Denied

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: 'data/'
```

**Solutions**:
```bash
# Create directory manually
mkdir data

# Check permissions
ls -la data/

# Change permissions (Unix/Linux)
chmod 755 data/
```

### Problem: Invalid Choice Error

**Symptoms**:
```
Invalid choice: x
```

**Solutions**:
```bash
# Ensure you enter a number 0-6
# No letters or special characters
# Press Enter after typing number
```

### Problem: Files Not Created

**Symptoms**:
- Script completes but no files in `data/`

**Solutions**:
```bash
# Check current directory
pwd

# Look for data directory
ls -la | grep data

# Check script output for errors
python generate_large_files.py 2>&1 | tee output.log
```

### Problem: Python Not Found

**Symptoms**:
```
'python' is not recognized as an internal or external command
```

**Solutions**:
```bash
# Try python3
python3 generate_large_files.py

# Or use full path
/usr/bin/python3 generate_large_files.py

# Windows: Use py
py generate_large_files.py
```

## Examples

### Example 1: Quick Test Before Deployment

```bash
# Generate demo files
python generate_large_files.py
# Select: 0

# Verify uploader works
dv-upload data/ --list-only --recurse

# Clean deployment test
dv-upload data/ --recurse --verify

# Cleanup
rm -rf data/
```

### Example 2: Performance Benchmark

```bash
# Generate large files
python generate_large_files.py
# Select: 3

# Benchmark direct upload
time dv-upload data/ --recurse --verify > upload_direct.log 2>&1

# Delete files from Dataverse

# Benchmark traditional upload
time dv-upload data/ --recurse --verify --traditional > upload_trad.log 2>&1

# Compare results
diff upload_direct.log upload_trad.log
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Upload

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Generate test files
        run: |
          cd examples
          python generate_large_files.py <<EOF
          1
          EOF
      
      - name: Test upload
        env:
          DV_SERVER_URL: ${{ secrets.DV_SERVER_URL }}
          DV_API_KEY: ${{ secrets.DV_API_KEY }}
          DV_DATASET_PID: ${{ secrets.DV_DATASET_PID }}
        run: |
          dv-upload data/ --recurse --verify --list-only
```

### Example 4: Documentation Testing

```bash
# Generate all file types for documentation
python generate_large_files.py
# Select: 5

# Upload and capture output
dv-upload data/ --recurse --verify | tee upload_output.txt

# Extract statistics for documentation
grep "Files uploaded:" upload_output.txt
grep "Total bytes:" upload_output.txt
```

### Example 5: Regression Testing

```bash
#!/bin/bash
# regression_test.sh

echo "Generating test files..."
python examples/generate_large_files.py <<EOF
2
EOF

echo "Testing upload..."
dv-upload data/ --recurse --verify

if [ $? -eq 0 ]; then
    echo "✓ Upload successful"
    
    echo "Testing duplicate detection..."
    dv-upload data/ --recurse --verify | grep "Files skipped: 5"
    
    if [ $? -eq 0 ]; then
        echo "✓ Duplicate detection works"
    else
        echo "✗ Duplicate detection failed"
        exit 1
    fi
else
    echo "✗ Upload failed"
    exit 1
fi

echo "Cleaning up..."
rm -rf data/

echo "✓ All tests passed!"
```

### Example 6: Custom Dataset Generation

```python
# custom_dataset.py
from generate_large_files import LargeFileGenerator

# Create specialized dataset
generator = LargeFileGenerator(output_dir="custom_data")

# Generate time-series data
print("Generating time-series data...")
for month in range(1, 13):
    filename = f"sales_2024_{month:02d}.csv"
    generator.create_large_csv_file(
        filename,
        num_rows=30000 * month,  # More data each month
        num_columns=8
    )

# Generate metadata
print("\nGenerating metadata files...")
generator.create_large_json_file("metadata.json", num_records=12)

# Generate documentation
print("\nGenerating documentation...")
generator.create_large_text_file("README.txt", size_mb=1)

print("\n✓ Custom dataset generated!")
print("Upload with: dv-upload custom_data/ --recurse --verify")
```

### Example 7: Parallel Generation

```bash
# Generate multiple datasets in parallel
python generate_large_files.py &  # Select 1
DATASET1_PID=$!

python generate_large_files.py &  # Select 2
DATASET2_PID=$!

# Wait for completion
wait $DATASET1_PID
wait $DATASET2_PID

echo "All datasets generated!"
```

## Best Practices

### 1. Start Small

Always start with Option 0 (demo) to verify everything works:
```bash
python generate_large_files.py  # Select 0
dv-upload data/ --recurse --list-only
```

### 2. Clean Up After Testing

Remove generated files after testing:
```bash
rm -rf data/
```

Or selectively remove:
```bash
# Keep CSVs, remove others
rm data/*.json data/*.txt data/*.bin data/*.log
```

### 3. Use Version Control Wisely

Add to `.gitignore`:
```gitignore
# Generated test files
data/
examples/data/
*.csv
*.json
*.bin
*.log
test_data/
custom_data/
```

### 4. Document Test Scenarios

Create a test plan:
```markdown
## Test Plan

### Scenario 1: Small Files
- Generate: Option 1
- Upload: `dv-upload data/ --recurse`
- Expected: 5 files uploaded, ~30 MB

### Scenario 2: Large Files
- Generate: Option 3
- Upload: `dv-upload data/ --recurse --verify`
- Expected: 5 files uploaded, ~1 GB, checksums verified
```

### 5. Monitor Resource Usage

During generation:
```bash
# Monitor in another terminal
watch -n 1 'du -sh data/ && df -h .'
```

### 6. Automate Repetitive Tests

Create shell scripts for common scenarios:
```bash
#!/bin/bash
# test_upload.sh

echo "Generating files..."
python examples/generate_large_files.py <<EOF
1
EOF

echo "Uploading files..."
dv-upload data/ --recurse --verify

echo "Verifying duplicate detection..."
dv-upload data/ --recurse --verify

echo "Cleaning up..."
rm -rf data/

echo "✓ Test complete!"
```

## Summary

The Large File Generator is a powerful tool for:

- ✅ **Testing**: Generate realistic test data quickly
- ✅ **Benchmarking**: Measure upload performance
- ✅ **Development**: Iterate on features with real data
- ✅ **CI/CD**: Automate testing in pipelines
- ✅ **Documentation**: Create examples and tutorials
- ✅ **Debugging**: Reproduce issues with specific file types/sizes

**Quick Reference**:
```bash
# Demo
python generate_large_files.py  # Select 0

# Small
python generate_large_files.py  # Select 1

# Medium  
python generate_large_files.py  # Select 2

# Large
python generate_large_files.py  # Select 3

# Upload generated files
dv-upload data/ --recurse --verify
```

For more information, see:
- [README.md](../README.md) - Main documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [examples/](../examples/) - Usage examples

---

**Questions or Issues?**

- GitHub Issues: [Report an issue](https://github.com/your-org/dataverse-uploader-python/issues)
- Documentation: [View docs](https://github.com/your-org/dataverse-uploader-python/wiki)
- Community: [Dataverse Community](https://dataverse.org)
