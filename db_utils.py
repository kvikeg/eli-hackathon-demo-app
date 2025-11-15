import sqlite3

# Database setup
def init_database():
    """Create and populate sample database"""
    conn = sqlite3.connect('sales_demo.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT,
            region TEXT,
            signup_date DATE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date DATE,
            total_amount REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        # Insert sample data
        products = [
            (1, 'Laptop Pro', 'Electronics', 1299.99),
            (2, 'Wireless Mouse', 'Electronics', 29.99),
            (3, 'Office Chair', 'Furniture', 399.99),
            (4, 'Desk Lamp', 'Furniture', 49.99),
            (5, 'USB-C Cable', 'Accessories', 19.99),
            (6, 'Monitor 27"', 'Electronics', 349.99),
            (7, 'Keyboard Mechanical', 'Electronics', 129.99),
            (8, 'Standing Desk', 'Furniture', 599.99),
            (9, 'Webcam HD', 'Electronics', 89.99),
            (10, 'Headphones', 'Electronics', 199.99)
        ]
        cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', products)
        
        customers = [
            (1, 'Acme Corp', 'North', '2023-01-15'),
            (2, 'TechStart Inc', 'West', '2023-02-20'),
            (3, 'Global Solutions', 'East', '2023-03-10'),
            (4, 'Innovation Labs', 'South', '2023-04-05'),
            (5, 'Digital Dynamics', 'North', '2023-05-12'),
            (6, 'Future Systems', 'West', '2023-06-18'),
            (7, 'Smart Enterprises', 'East', '2023-07-22'),
            (8, 'NextGen Co', 'South', '2023-08-30')
        ]
        cursor.executemany('INSERT INTO customers VALUES (?,?,?,?)', customers)
        
        orders = [
            (1, 1, 1, 5, '2024-01-15', 6499.95),
            (2, 2, 6, 3, '2024-01-20', 1049.97),
            (3, 3, 3, 10, '2024-02-05', 3999.90),
            (4, 1, 2, 20, '2024-02-10', 599.80),
            (5, 4, 8, 2, '2024-03-01', 1199.98),
            (6, 5, 1, 3, '2024-03-15', 3899.97),
            (7, 2, 7, 5, '2024-04-10', 649.95),
            (8, 6, 4, 8, '2024-04-20', 399.92),
            (9, 3, 10, 6, '2024-05-05', 1199.94),
            (10, 7, 6, 4, '2024-05-15', 1399.96),
            (11, 1, 9, 10, '2024-06-01', 899.90),
            (12, 8, 1, 2, '2024-06-10', 2599.98),
            (13, 4, 3, 5, '2024-07-05', 1999.95),
            (14, 5, 5, 50, '2024-07-20', 999.50),
            (15, 2, 8, 3, '2024-08-01', 1799.97),
            (16, 6, 2, 15, '2024-08-15', 449.85),
            (17, 3, 7, 8, '2024-09-10', 1039.92),
            (18, 7, 10, 4, '2024-09-25', 799.96),
            (19, 1, 6, 6, '2024-10-05', 2099.94),
            (20, 8, 4, 12, '2024-10-20', 599.88)
        ]
        cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?,?)', orders)
        
        conn.commit()
    
    return conn

def get_schema(conn):
    """Get database schema as text"""
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    schema_text = "Database Schema:\n\n"
    
    for table in tables:
        table_name = table[0]
        schema_text += f"Table: {table_name}\n"
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            schema_text += f"  - {col[1]} ({col[2]})\n"
        schema_text += "\n"
    
    return schema_text
