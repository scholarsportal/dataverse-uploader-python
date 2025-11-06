"""
Generate large files of various types for testing the Dataverse uploader.

This script creates files of different sizes and formats in a data/ directory
to test upload performance, chunking, and handling of large files.
"""

import csv
import json
import os
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


class LargeFileGenerator:
    """Generator for creating large test files."""
    
    def __init__(self, output_dir: str = "data"):
        """Initialize the generator.
        
        Args:
            output_dir: Directory where files will be created
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_random_text(self, length: int) -> str:
        """Generate random text of specified length.
        
        Args:
            length: Number of characters to generate
            
        Returns:
            Random text string
        """
        chars = string.ascii_letters + string.digits + string.punctuation + ' \n'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_large_text_file(self, filename: str, size_mb: int) -> Path:
        """Create a large text file.
        
        Args:
            filename: Name of the file to create
            size_mb: Target size in megabytes
            
        Returns:
            Path to created file
        """
        filepath = self.output_dir / filename
        target_bytes = size_mb * 1024 * 1024
        chunk_size = 1024 * 1024  # 1 MB chunks
        
        print(f"Creating {filename} ({size_mb} MB)...")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            bytes_written = 0
            while bytes_written < target_bytes:
                chunk = self.generate_random_text(chunk_size)
                f.write(chunk)
                bytes_written += len(chunk.encode('utf-8'))
                
                # Progress indicator
                progress = (bytes_written / target_bytes) * 100
                if bytes_written % (10 * 1024 * 1024) == 0:  # Every 10 MB
                    print(f"  Progress: {progress:.1f}%")
        
        actual_size = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ Created {filename}: {actual_size:.2f} MB\n")
        return filepath
    
    def create_large_csv_file(self, filename: str, num_rows: int, num_columns: int = 10) -> Path:
        """Create a large CSV file with synthetic data.
        
        Args:
            filename: Name of the CSV file
            num_rows: Number of data rows to generate
            num_columns: Number of columns in the CSV
            
        Returns:
            Path to created file
        """
        filepath = self.output_dir / filename
        
        print(f"Creating {filename} ({num_rows:,} rows x {num_columns} columns)...")
        
        # Generate column headers
        headers = [f'column_{i}' for i in range(num_columns)]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            # Generate rows in batches
            batch_size = 10000
            for batch_start in range(0, num_rows, batch_size):
                batch_end = min(batch_start + batch_size, num_rows)
                rows = []
                
                for row_num in range(batch_start, batch_end):
                    row = [
                        row_num,  # First column is row number
                        f"text_{random.randint(1000, 9999)}",  # Text data
                        random.random() * 1000,  # Float
                        random.randint(0, 1000000),  # Integer
                        datetime.now() + timedelta(days=random.randint(-365, 365)),  # Date
                    ] + [
                        random.choice(['A', 'B', 'C', 'D', 'E']) 
                        for _ in range(num_columns - 5)
                    ]
                    rows.append(row)
                
                writer.writerows(rows)
                
                # Progress indicator
                progress = (batch_end / num_rows) * 100
                if batch_end % (100000) == 0 or batch_end == num_rows:
                    print(f"  Progress: {progress:.1f}%")
        
        actual_size = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ Created {filename}: {actual_size:.2f} MB, {num_rows:,} rows\n")
        return filepath
    
    def create_large_json_file(self, filename: str, num_records: int) -> Path:
        """Create a large JSON file with synthetic data.
        
        Args:
            filename: Name of the JSON file
            num_records: Number of records to generate
            
        Returns:
            Path to created file
        """
        filepath = self.output_dir / filename
        
        print(f"Creating {filename} ({num_records:,} records)...")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('[\n')
            
            batch_size = 1000
            for batch_start in range(0, num_records, batch_size):
                batch_end = min(batch_start + batch_size, num_records)
                records = []
                
                for i in range(batch_start, batch_end):
                    record = {
                        'id': i,
                        'timestamp': (datetime.now() + timedelta(seconds=i)).isoformat(),
                        'user': f"user_{random.randint(1, 10000)}",
                        'value': random.random() * 1000,
                        'status': random.choice(['active', 'inactive', 'pending']),
                        'metadata': {
                            'key1': random.randint(1, 100),
                            'key2': f"value_{random.randint(1, 1000)}",
                            'key3': [random.random() for _ in range(5)]
                        },
                        'description': self.generate_random_text(100)
                    }
                    records.append(record)
                
                # Write batch
                for idx, record in enumerate(records):
                    is_last_in_batch = (idx == len(records) - 1)
                    is_last_overall = (batch_end >= num_records)
                    
                    json.dump(record, f, indent=2)
                    
                    if not (is_last_in_batch and is_last_overall):
                        f.write(',\n')
                
                # Progress indicator
                progress = (batch_end / num_records) * 100
                if batch_end % (10000) == 0 or batch_end == num_records:
                    print(f"  Progress: {progress:.1f}%")
            
            f.write('\n]')
        
        actual_size = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ Created {filename}: {actual_size:.2f} MB, {num_records:,} records\n")
        return filepath
    
    def create_binary_file(self, filename: str, size_mb: int) -> Path:
        """Create a binary file with random data.
        
        Args:
            filename: Name of the file
            size_mb: Target size in megabytes
            
        Returns:
            Path to created file
        """
        filepath = self.output_dir / filename
        target_bytes = size_mb * 1024 * 1024
        chunk_size = 1024 * 1024  # 1 MB chunks
        
        print(f"Creating {filename} ({size_mb} MB binary)...")
        
        with open(filepath, 'wb') as f:
            bytes_written = 0
            while bytes_written < target_bytes:
                remaining = min(chunk_size, target_bytes - bytes_written)
                chunk = os.urandom(remaining)
                f.write(chunk)
                bytes_written += len(chunk)
                
                # Progress indicator
                progress = (bytes_written / target_bytes) * 100
                if bytes_written % (10 * 1024 * 1024) == 0:  # Every 10 MB
                    print(f"  Progress: {progress:.1f}%")
        
        actual_size = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ Created {filename}: {actual_size:.2f} MB\n")
        return filepath
    
    def create_nested_directory_structure(self, base_name: str, depth: int, files_per_dir: int, file_size_kb: int) -> Path:
        """Create a nested directory structure with files.
        
        Args:
            base_name: Name of the base directory
            depth: How many levels deep to nest
            files_per_dir: Number of files in each directory
            file_size_kb: Size of each file in KB
            
        Returns:
            Path to base directory
        """
        base_path = self.output_dir / base_name
        base_path.mkdir(exist_ok=True)
        
        print(f"Creating nested directory structure: {base_name}")
        print(f"  Depth: {depth}, Files per dir: {files_per_dir}, File size: {file_size_kb} KB\n")
        
        def create_level(current_path: Path, current_depth: int):
            # Create files at this level
            for i in range(files_per_dir):
                file_path = current_path / f"file_{current_depth}_{i}.txt"
                content = self.generate_random_text(file_size_kb * 1024)
                file_path.write_text(content, encoding='utf-8')
            
            # Create subdirectory if not at max depth
            if current_depth < depth:
                subdir = current_path / f"level_{current_depth + 1}"
                subdir.mkdir(exist_ok=True)
                create_level(subdir, current_depth + 1)
        
        create_level(base_path, 1)
        
        # Count total files
        total_files = sum(1 for _ in base_path.rglob('*.txt'))
        total_size = sum(f.stat().st_size for f in base_path.rglob('*.txt')) / (1024 * 1024)
        
        print(f"✓ Created directory structure: {total_files} files, {total_size:.2f} MB total\n")
        return base_path
    
    def create_log_file(self, filename: str, num_lines: int) -> Path:
        """Create a log file with synthetic log entries.
        
        Args:
            filename: Name of the log file
            num_lines: Number of log lines to generate
            
        Returns:
            Path to created file
        """
        filepath = self.output_dir / filename
        
        print(f"Creating {filename} ({num_lines:,} log lines)...")
        
        log_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
        services = ['auth', 'api', 'database', 'cache', 'worker']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for i in range(num_lines):
                timestamp = datetime.now() + timedelta(seconds=i)
                level = random.choice(log_levels)
                service = random.choice(services)
                message = f"Operation {i} completed with status {random.randint(200, 500)}"
                
                log_line = (
                    f"[{timestamp.isoformat()}] {level:8s} {service:10s} | "
                    f"{message} - request_id={random.randint(10000, 99999)}\n"
                )
                f.write(log_line)
                
                # Progress indicator
                if (i + 1) % 100000 == 0 or (i + 1) == num_lines:
                    progress = ((i + 1) / num_lines) * 100
                    print(f"  Progress: {progress:.1f}%")
        
        actual_size = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ Created {filename}: {actual_size:.2f} MB, {num_lines:,} lines\n")
        return filepath


def main():
    """Main function to generate test files."""
    
    print("=" * 80)
    print("Large File Generator for Dataverse Uploader Testing")
    print("=" * 80)
    print()
    
    generator = LargeFileGenerator(output_dir="data")
    
    print("This script will create various large files for testing.")
    print("Files will be created in the 'data/' directory.")
    print()
    
    # Menu of file generation options
    print("Select files to generate:")
    print()
    print("Size Categories:")
    print("  1. Small files (1-10 MB) - Quick tests")
    print("  2. Medium files (10-100 MB) - Standard tests")
    print("  3. Large files (100-500 MB) - Stress tests")
    print("  4. Extra large files (500+ MB) - Maximum stress")
    print("  5. All sizes - Complete test suite")
    print("  6. Custom - Specify your own")
    print()
    print("  0. Quick demo (small files only)")
    print()
    
    choice = input("Enter choice (0-6): ").strip()
    
    print()
    print("=" * 80)
    print("Generating files...")
    print("=" * 80)
    print()
    
    if choice == "0":
        # Quick demo - small files
        generator.create_large_csv_file("demo_data.csv", num_rows=10000, num_columns=10)
        generator.create_large_json_file("demo_logs.json", num_records=5000)
        generator.create_large_text_file("demo_text.txt", size_mb=5)
        
    elif choice == "1":
        # Small files (1-10 MB)
        generator.create_large_csv_file("small_data.csv", num_rows=50000, num_columns=8)
        generator.create_large_json_file("small_logs.json", num_records=10000)
        generator.create_large_text_file("small_document.txt", size_mb=5)
        generator.create_binary_file("small_binary.bin", size_mb=3)
        generator.create_log_file("small_server.log", num_lines=100000)
        
    elif choice == "2":
        # Medium files (10-100 MB)
        generator.create_large_csv_file("medium_data.csv", num_rows=500000, num_columns=12)
        generator.create_large_json_file("medium_logs.json", num_records=100000)
        generator.create_large_text_file("medium_document.txt", size_mb=50)
        generator.create_binary_file("medium_binary.bin", size_mb=30)
        generator.create_log_file("medium_server.log", num_lines=1000000)
        
    elif choice == "3":
        # Large files (100-500 MB)
        generator.create_large_csv_file("large_data.csv", num_rows=2000000, num_columns=15)
        generator.create_large_json_file("large_logs.json", num_records=500000)
        generator.create_large_text_file("large_document.txt", size_mb=200)
        generator.create_binary_file("large_binary.bin", size_mb=150)
        generator.create_log_file("large_server.log", num_lines=5000000)
        
    elif choice == "4":
        # Extra large files (500+ MB)
        generator.create_large_csv_file("xlarge_data.csv", num_rows=5000000, num_columns=20)
        generator.create_large_json_file("xlarge_logs.json", num_records=1000000)
        generator.create_large_text_file("xlarge_document.txt", size_mb=500)
        generator.create_binary_file("xlarge_binary.bin", size_mb=600)
        generator.create_log_file("xlarge_server.log", num_lines=10000000)
        
    elif choice == "5":
        # All sizes
        print("Generating complete test suite (this may take a while)...\n")
        
        # Small
        generator.create_large_csv_file("small_data.csv", num_rows=50000, num_columns=8)
        generator.create_large_text_file("small_document.txt", size_mb=5)
        
        # Medium
        generator.create_large_csv_file("medium_data.csv", num_rows=500000, num_columns=12)
        generator.create_large_json_file("medium_logs.json", num_records=100000)
        
        # Large
        generator.create_large_csv_file("large_data.csv", num_rows=2000000, num_columns=15)
        generator.create_binary_file("large_binary.bin", size_mb=150)
        
        # Extra large
        generator.create_large_text_file("xlarge_document.txt", size_mb=500)
        generator.create_log_file("xlarge_server.log", num_lines=5000000)
        
        # Nested structure
        generator.create_nested_directory_structure(
            "nested_files", 
            depth=3, 
            files_per_dir=5, 
            file_size_kb=500
        )
        
    elif choice == "6":
        # Custom
        print("Custom file generation:")
        print()
        
        file_type = input("File type (csv/json/text/binary/log): ").strip().lower()
        
        if file_type == "csv":
            filename = input("Filename (default: custom_data.csv): ").strip() or "custom_data.csv"
            rows = int(input("Number of rows: ").strip())
            cols = int(input("Number of columns (default: 10): ").strip() or "10")
            generator.create_large_csv_file(filename, num_rows=rows, num_columns=cols)
            
        elif file_type == "json":
            filename = input("Filename (default: custom_data.json): ").strip() or "custom_data.json"
            records = int(input("Number of records: ").strip())
            generator.create_large_json_file(filename, num_records=records)
            
        elif file_type == "text":
            filename = input("Filename (default: custom_text.txt): ").strip() or "custom_text.txt"
            size_mb = int(input("Size in MB: ").strip())
            generator.create_large_text_file(filename, size_mb=size_mb)
            
        elif file_type == "binary":
            filename = input("Filename (default: custom_binary.bin): ").strip() or "custom_binary.bin"
            size_mb = int(input("Size in MB: ").strip())
            generator.create_binary_file(filename, size_mb=size_mb)
            
        elif file_type == "log":
            filename = input("Filename (default: custom_server.log): ").strip() or "custom_server.log"
            lines = int(input("Number of lines: ").strip())
            generator.create_log_file(filename, num_lines=lines)
            
        else:
            print(f"Unknown file type: {file_type}")
            return
    
    else:
        print(f"Invalid choice: {choice}")
        return
    
    print()
    print("=" * 80)
    print("✓ File generation complete!")
    print("=" * 80)
    print()
    
    # Summary
    data_path = Path("data")
    if data_path.exists():
        all_files = list(data_path.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]
        total_size = sum(f.stat().st_size for f in files_only) / (1024 * 1024)
        
        print(f"Total files created: {len(files_only)}")
        print(f"Total size: {total_size:.2f} MB")
        print(f"Location: {data_path.absolute()}")
        print()
        
        print("Files created:")
        for f in sorted(files_only):
            rel_path = f.relative_to(data_path)
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {rel_path} ({size_mb:.2f} MB)")
    
    print()
    print("You can now test the uploader with these files:")
    print("  dv-upload data/ --recurse --verify")
    print()


if __name__ == "__main__":
    main()