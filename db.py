import sqlite3

def create_tables():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create 'admin' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_name TEXT NOT NULL,
            admin_password TEXT NOT NULL
        )
    ''')

    # Create 'customer' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_password TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')

    # Create 'delivery_boys' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_boys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_boy TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            shop_name TEXT NOT NULL,        
            )
    ''')

    # Create 'delivery_orders' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            delivery_boy TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    # Create 'orders' table
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
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            shop_name TEXT NOT NULL,
        )
    ''')

    # Create 'products' table
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
            image3 TEXT,
            shop_name TEXT,
            owner_name TEXT
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        product_brand TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        review TEXT
    )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            shop_name TEXT,
            password TEXT
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_brand TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            review TEXT
        )
        ''')
    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
