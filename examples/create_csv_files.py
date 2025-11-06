"""
Script to create 5 different CSV files with sample data
"""
import csv
import random
from datetime import datetime, timedelta

def create_employees_csv():
    """Create employees.csv with employee data"""
    with open('employees.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['employee_id', 'name', 'department', 'salary', 'hire_date'])
        
        employees = [
            [1001, 'Alice Johnson', 'Engineering', 85000, '2020-03-15'],
            [1002, 'Bob Smith', 'Marketing', 65000, '2019-07-22'],
            [1003, 'Carol Davis', 'HR', 70000, '2021-01-10'],
            [1004, 'David Wilson', 'Engineering', 92000, '2018-11-05'],
            [1005, 'Eve Martinez', 'Sales', 78000, '2022-02-28'],
            [1006, 'Frank Brown', 'Finance', 88000, '2019-09-12'],
            [1007, 'Grace Lee', 'Engineering', 95000, '2020-06-18'],
        ]
        writer.writerows(employees)
    print("✓ Created employees.csv")

def create_products_csv():
    """Create products.csv with product inventory data"""
    with open('products.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'product_name', 'category', 'price', 'stock_quantity'])
        
        products = [
            ['P001', 'Laptop', 'Electronics', 1299.99, 45],
            ['P002', 'Mouse', 'Electronics', 29.99, 150],
            ['P003', 'Desk Chair', 'Furniture', 249.99, 30],
            ['P004', 'Monitor', 'Electronics', 399.99, 60],
            ['P005', 'Keyboard', 'Electronics', 79.99, 120],
            ['P006', 'Desk Lamp', 'Furniture', 45.99, 80],
            ['P007', 'Notebook', 'Stationery', 5.99, 500],
            ['P008', 'Pen Set', 'Stationery', 12.99, 200],
        ]
        writer.writerows(products)
    print("✓ Created products.csv")

def create_sales_csv():
    """Create sales.csv with sales transaction data"""
    with open('sales.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['transaction_id', 'date', 'product_id', 'quantity', 'total_amount'])
        
        base_date = datetime(2024, 1, 1)
        sales = []
        for i in range(1, 16):
            date = base_date + timedelta(days=random.randint(0, 300))
            product_id = f'P{random.randint(1, 8):03d}'
            quantity = random.randint(1, 10)
            price = random.uniform(5.99, 1299.99)
            total = round(quantity * price, 2)
            sales.append([f'T{i:04d}', date.strftime('%Y-%m-%d'), product_id, quantity, total])
        
        writer.writerows(sales)
    print("✓ Created sales.csv")

def create_customers_csv():
    """Create customers.csv with customer data"""
    with open('customers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['customer_id', 'name', 'email', 'city', 'country', 'signup_date'])
        
        customers = [
            ['C001', 'John Anderson', 'john.anderson@email.com', 'New York', 'USA', '2023-01-15'],
            ['C002', 'Maria Garcia', 'maria.garcia@email.com', 'Madrid', 'Spain', '2023-02-20'],
            ['C003', 'Wei Chen', 'wei.chen@email.com', 'Beijing', 'China', '2023-03-10'],
            ['C004', 'Sarah Miller', 'sarah.miller@email.com', 'London', 'UK', '2023-04-05'],
            ['C005', 'Ahmed Hassan', 'ahmed.hassan@email.com', 'Dubai', 'UAE', '2023-05-12'],
            ['C006', 'Lisa Schmidt', 'lisa.schmidt@email.com', 'Berlin', 'Germany', '2023-06-18'],
            ['C007', 'Raj Patel', 'raj.patel@email.com', 'Mumbai', 'India', '2023-07-22'],
            ['C008', 'Sophie Dubois', 'sophie.dubois@email.com', 'Paris', 'France', '2023-08-30'],
        ]
        writer.writerows(customers)
    print("✓ Created customers.csv")

def create_weather_csv():
    """Create weather.csv with weather data"""
    with open('weather.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'city', 'temperature_c', 'humidity_percent', 'condition'])
        
        conditions = ['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy', 'Windy']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami']
        
        base_date = datetime(2024, 10, 1)
        weather = []
        for day in range(10):
            date = base_date + timedelta(days=day)
            for city in cities:
                temp = random.randint(15, 32)
                humidity = random.randint(40, 90)
                condition = random.choice(conditions)
                weather.append([date.strftime('%Y-%m-%d'), city, temp, humidity, condition])
        
        writer.writerows(weather)
    print("✓ Created weather.csv")

def main():
    """Create all CSV files"""
    print("Creating CSV files...\n")
    
    create_employees_csv()
    create_products_csv()
    create_sales_csv()
    create_customers_csv()
    create_weather_csv()
    
    print("\n✅ All 5 CSV files created successfully!")
    print("\nFiles created:")
    print("  1. employees.csv - Employee records")
    print("  2. products.csv - Product inventory")
    print("  3. sales.csv - Sales transactions")
    print("  4. customers.csv - Customer data")
    print("  5. weather.csv - Weather observations")

if __name__ == "__main__":
    main()