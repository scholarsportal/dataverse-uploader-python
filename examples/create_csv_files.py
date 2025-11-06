"""
Script to create multiple CSV files with sample data.
Supports command-line argument to specify how many files to generate.
"""
import csv
import random
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def create_employee_csv(file_num: int, output_dir: Path) -> None:
    """Create an employees CSV file with employee data"""
    filename = output_dir / f'employees_{file_num:04d}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['employee_id', 'name', 'department', 'salary', 'hire_date'])
        
        # Generate random employees
        departments = ['Engineering', 'Marketing', 'HR', 'Sales', 'Finance', 'Operations']
        first_names = ['Alice', 'Bob', 'Carol', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 
                       'Iris', 'Jack', 'Kelly', 'Liam', 'Mary', 'Nathan', 'Olivia', 'Peter']
        last_names = ['Johnson', 'Smith', 'Davis', 'Wilson', 'Martinez', 'Brown', 'Lee', 
                      'Garcia', 'Miller', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'White']
        
        num_employees = random.randint(5, 15)
        base_id = file_num * 1000
        
        for i in range(num_employees):
            emp_id = base_id + i + 1
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            department = random.choice(departments)
            salary = random.randint(50000, 150000)
            
            # Random hire date in the last 5 years
            days_ago = random.randint(0, 1825)
            hire_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            writer.writerow([emp_id, name, department, salary, hire_date])


def create_product_csv(file_num: int, output_dir: Path) -> None:
    """Create a products CSV file with product inventory data"""
    filename = output_dir / f'products_{file_num:04d}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'product_name', 'category', 'price', 'stock_quantity'])
        
        categories = ['Electronics', 'Furniture', 'Stationery', 'Clothing', 'Food', 'Sports']
        products = {
            'Electronics': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam'],
            'Furniture': ['Desk Chair', 'Desk Lamp', 'Filing Cabinet', 'Bookshelf', 'Standing Desk'],
            'Stationery': ['Notebook', 'Pen Set', 'Stapler', 'Tape', 'Highlighters', 'Folders'],
            'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Hat', 'Socks'],
            'Food': ['Coffee', 'Tea', 'Snacks', 'Energy Bar', 'Water Bottle'],
            'Sports': ['Basketball', 'Soccer Ball', 'Yoga Mat', 'Dumbbells', 'Jump Rope']
        }
        
        num_products = random.randint(8, 20)
        base_id = file_num * 100
        
        for i in range(num_products):
            product_id = f'P{base_id + i + 1:05d}'
            category = random.choice(categories)
            product_name = random.choice(products[category])
            price = round(random.uniform(5.99, 999.99), 2)
            stock = random.randint(0, 500)
            
            writer.writerow([product_id, product_name, category, price, stock])


def create_sales_csv(file_num: int, output_dir: Path) -> None:
    """Create a sales CSV file with sales transaction data"""
    filename = output_dir / f'sales_{file_num:04d}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['transaction_id', 'date', 'product_id', 'quantity', 'total_amount'])
        
        base_date = datetime(2024, 1, 1)
        num_transactions = random.randint(10, 30)
        base_txn_id = file_num * 1000
        
        for i in range(num_transactions):
            txn_id = f'T{base_txn_id + i + 1:06d}'
            date = base_date + timedelta(days=random.randint(0, 300))
            product_id = f'P{random.randint(1, 999):05d}'
            quantity = random.randint(1, 10)
            price = random.uniform(5.99, 1299.99)
            total = round(quantity * price, 2)
            
            writer.writerow([txn_id, date.strftime('%Y-%m-%d'), product_id, quantity, total])


def create_customer_csv(file_num: int, output_dir: Path) -> None:
    """Create a customers CSV file with customer data"""
    filename = output_dir / f'customers_{file_num:04d}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['customer_id', 'name', 'email', 'city', 'country', 'signup_date'])
        
        first_names = ['John', 'Maria', 'Wei', 'Sarah', 'Ahmed', 'Lisa', 'Raj', 'Sophie',
                       'Carlos', 'Yuki', 'Emma', 'Hassan', 'Olga', 'Kim', 'Pierre']
        last_names = ['Anderson', 'Garcia', 'Chen', 'Miller', 'Hassan', 'Schmidt', 'Patel',
                     'Dubois', 'Rodriguez', 'Tanaka', 'Wilson', 'Ali', 'Petrov', 'Park', 'Blanc']
        
        cities = [
            ('New York', 'USA'), ('Madrid', 'Spain'), ('Beijing', 'China'), ('London', 'UK'),
            ('Dubai', 'UAE'), ('Berlin', 'Germany'), ('Mumbai', 'India'), ('Paris', 'France'),
            ('Tokyo', 'Japan'), ('Sydney', 'Australia'), ('Toronto', 'Canada'), ('Rome', 'Italy'),
            ('Seoul', 'South Korea'), ('Moscow', 'Russia'), ('Mexico City', 'Mexico')
        ]
        
        num_customers = random.randint(8, 15)
        base_id = file_num * 100
        
        for i in range(num_customers):
            customer_id = f'C{base_id + i + 1:05d}'
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            email = f"{name.lower().replace(' ', '.')}@email.com"
            city, country = random.choice(cities)
            
            # Random signup date in the last 2 years
            days_ago = random.randint(0, 730)
            signup_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            writer.writerow([customer_id, name, email, city, country, signup_date])


def create_weather_csv(file_num: int, output_dir: Path) -> None:
    """Create a weather CSV file with weather data"""
    filename = output_dir / f'weather_{file_num:04d}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'city', 'temperature_c', 'humidity_percent', 'condition'])
        
        conditions = ['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy', 'Windy', 'Stormy', 'Foggy']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami', 'Seattle', 
                  'Boston', 'Denver', 'Phoenix', 'Atlanta']
        
        # Random date in the last year
        days_ago = random.randint(0, 365)
        base_date = datetime.now() - timedelta(days=days_ago)
        
        # Generate 10-30 days of weather data
        num_days = random.randint(10, 30)
        
        for day in range(num_days):
            date = base_date + timedelta(days=day)
            city = random.choice(cities)
            temp = random.randint(15, 32)
            humidity = random.randint(40, 90)
            condition = random.choice(conditions)
            
            writer.writerow([date.strftime('%Y-%m-%d'), city, temp, humidity, condition])


def main():
    """Main function to create CSV files"""
    parser = argparse.ArgumentParser(
        description='Generate multiple CSV files with sample data for testing bulk uploads.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_csv_files.py                  # Generate 5 files (default)
  python create_csv_files.py --count 100      # Generate 100 files
  python create_csv_files.py -n 600           # Generate 600 files
  python create_csv_files.py -n 50 -o data/   # Generate 50 files in 'data/' directory
        """
    )
    
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=5,
        help='Number of CSV files to generate (default: 5)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='data',
        help='Output directory for generated files (default: data/)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducible data generation'
    )
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    num_files = args.count
    
    if num_files <= 0:
        print("Error: Number of files must be greater than 0")
        sys.exit(1)
    
    print(f"\n{'=' * 70}")
    print(f"Generating {num_files} sets of CSV files in '{output_dir}'")
    print(f"{'=' * 70}\n")
    
    # File type generators
    generators = [
        ('employees', create_employee_csv),
        ('products', create_product_csv),
        ('sales', create_sales_csv),
        ('customers', create_customer_csv),
        ('weather', create_weather_csv),
    ]
    
    total_files = num_files * len(generators)
    files_created = 0
    
    # Create files with progress logging
    for i in range(1, num_files + 1):
        for file_type, generator_func in generators:
            generator_func(i, output_dir)
            files_created += 1
            
            # Log progress at regular intervals
            if files_created % 10 == 0 or files_created == total_files:
                progress_pct = (files_created / total_files) * 100
                print(f"Progress: {files_created}/{total_files} files ({progress_pct:.1f}%)")
    
    print(f"\n{'=' * 70}")
    print(f"✅ Successfully generated {total_files} CSV files!")
    print(f"{'=' * 70}")
    
    print("\nFiles created:")
    print(f"  • {num_files} employee files")
    print(f"  • {num_files} product files")
    print(f"  • {num_files} sales files")
    print(f"  • {num_files} customer files")
    print(f"  • {num_files} weather files")
    
    print(f"\nOutput directory: {output_dir.absolute()}")
    
    # Show example filenames
    print("\nExample filenames:")
    print(f"  employees_0001.csv, employees_0002.csv, ...")
    print(f"  products_0001.csv, products_0002.csv, ...")
    print(f"  sales_0001.csv, sales_0002.csv, ...")
    print(f"  customers_0001.csv, customers_0002.csv, ...")
    print(f"  weather_0001.csv, weather_0002.csv, ...")
    
    # Calculate total size estimate
    avg_file_size_kb = 2  # Rough estimate
    total_size_mb = (total_files * avg_file_size_kb) / 1024
    print(f"\nEstimated total size: ~{total_size_mb:.1f} MB")


if __name__ == "__main__":
    main()