import sqlite3

conn = sqlite3.connect('ecommerce.db')

cursor = conn.cursor()

# Create the 'products' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_brand TEXT NOT NULL,
        product_category TEXT NOT NULL,
        price REAL NOT NULL,
        discount REAL,
        stock INTEGER NOT NULL,
        image1 TEXT,
        image2 TEXT,
        image3 TEXT
    )
''')

# Create the 'admin' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        admin_name TEXT PRIMARY KEY,
        admin_password TEXT NOT NULL
    )
''')

# Create the 'customer' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        address TEXT NOT NULL
    )
''')

# Create the 'orders' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_brand TEXT NOT NULL,
        product_category TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total_price REAL NOT NULL,
        date TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Tables created successfully!")
