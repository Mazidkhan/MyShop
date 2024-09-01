from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import sqlite3
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production!
app.config['UPLOAD_FOLDER'] = 'static/images'  # Folder where uploaded files will be saved
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        admin_name = request.form['admin_name']
        admin_password = request.form['admin_password']

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE admin_name = ? AND admin_password = ?', (admin_name, admin_password)).fetchone()
        conn.close()

        if admin:
            session['admin_name'] = admin['admin_name']
            return render_template('admin_base.html')
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('admin'))
    if 'admin_name' not in session:
        return render_template('admin_login.html')
    else:
        return render_template('admin_base.html')

@app.route('/delivery', methods=['GET', 'POST'])
def delivery():
    if request.method == 'POST':
        delivery_boy = request.form['delivery_boy']
        delivery_password = request.form['delivery_password']

        conn = get_db_connection()
        delivery = conn.execute('SELECT * FROM delivery_boys WHERE delivery_boy = ? AND password = ?', (delivery_boy, delivery_password)).fetchone()
        conn.close()

        if delivery:
            session['delivery_name'] = delivery['delivery_boy']
            return render_template('delivery_base.html')
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('delivery'))
    if 'delivery_name' not in session:
        return render_template('delivery_login.html')
    else:
        return render_template('delivery_base.html')

@app.route('/delivery/queues')
def delivery_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_orders where delivery_boy = ?',(session['delivery_name'],))
    deliveries = cursor.fetchall()
    return render_template('delivery_queues.html', deliveries=deliveries)

def update_status_in_table(table_name, order_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    if table_name == 'orders':
        cursor.execute(f"UPDATE {table_name} SET status = ? WHERE id = ?", (new_status, order_id))
    else:
        cursor.execute(f"UPDATE {table_name} SET status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

@app.route('/update-order-status/<order_id>', methods=['POST'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')

    # Update status in both tables
    update_status_in_table('orders', order_id, new_status)
    update_status_in_table('delivery_orders', order_id, new_status)

    return jsonify({"message": "Order status updated successfully!"}), 200

@app.route('/get-order-details/<order_id>', methods=['GET'])
def get_order_details(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT product_name, product_brand, quantity, price FROM orders WHERE id = ?', (order_id,))
    orders = cursor.fetchall()
    conn.close()
    order_details = [dict(row) for row in orders]

    return jsonify(order_details)

@app.route('/delivery/logout')
def delivery_logout():
    session.pop('delivery_name', None)
    return redirect(url_for('delivery'))


@app.route('/admin/update_product', methods=['PUT'])
def update_product():
    product_id = request.form.get('id')
    name = request.form.get('name')
    brand = request.form.get('brand')
    category = request.form.get('category')
    price = request.form.get('price')
    discount = request.form.get('discount')
    stock = request.form.get('stock')
    image1 = request.files.get('image1')
    image2 = request.files.get('image2')
    image3 = request.files.get('image3')

    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # Update record in the database
    cursor.execute('''
        UPDATE products
        SET product_name = ?, product_brand = ?, product_category = ?, price = ?, discount = ?, stock = ?,
            image1 = ?, image2 = ?, image3 = ?
        WHERE id = ?
    ''', (name, brand, category, price, discount, stock,
          image1.filename if image1 else None,
          image2.filename if image2 else None,
          image3.filename if image3 else None,
          product_id))

    conn.commit()

    # Save uploaded images
    if image1:
        image1.save(os.path.join(UPLOAD_FOLDER, image1.filename))
    if image2:
        image2.save(os.path.join(UPLOAD_FOLDER, image2.filename))
    if image3:
        image3.save(os.path.join(UPLOAD_FOLDER, image3.filename))

    conn.close()
    return redirect(url_for('products'))

@app.route('/admin/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    if product:
        return {
            'id': product[0],
            'product_name': product[1],
            'product_brand': product[2],
            'product_category': product[3],
            'price': product[4],
            'discount': product[5],
            'stock': product[6],
            'image1': product[7],
            'image2': product[8],
            'image3': product[9]
        }
    else:
        return {'error': 'Product not found'}, 404

@app.route('/admin/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    # Connect to SQLite database
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # Fetch the product to get the image filenames
    cursor.execute('SELECT image1, image2, image3 FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()

    if product:
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()

        # Remove the associated image files
        for image_filename in product:
            if image_filename and os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], image_filename)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        flash('Product deleted successfully!')
    else:
        flash('Product not found!')

    conn.close()
    return '', 204  # No Content

@app.route('/admin/products', methods=['GET', 'POST'])
def products():
    conn = get_db_connection()
    if request.method == 'POST':
        product_name = request.form['name']
        product_brand = request.form['brand']
        product_category = request.form['category']
        price = request.form['price']
        discount = request.form['discount']
        stock = request.form['stock']

        # Handle file uploads
        image1 = request.files['image1']
        image2 = request.files['image2']
        image3 = request.files['image3']

        image1_filename = ''
        image2_filename = ''
        image3_filename = ''

        # Save images if they are provided
        if image1 and allowed_file(image1.filename):
            image1_filename = secure_filename(image1.filename)
            image1.save(os.path.join(app.config['UPLOAD_FOLDER'], image1_filename))

        if image2 and allowed_file(image2.filename):
            image2_filename = secure_filename(image2.filename)
            image2.save(os.path.join(app.config['UPLOAD_FOLDER'], image2_filename))

        if image3 and allowed_file(image3.filename):
            image3_filename = secure_filename(image3.filename)
            image3.save(os.path.join(app.config['UPLOAD_FOLDER'], image3_filename))

        # Connect to the database
        cursor = conn.cursor()

        # Insert data into the database
        cursor.execute('''
            INSERT INTO products (product_name, product_brand, product_category, price, discount, stock, image1, image2, image3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_name, product_brand, product_category, price, discount, stock, image1_filename, image2_filename,
              image3_filename))

        conn.commit()

        return redirect(url_for('products'))

    if 'admin_name' in session:
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()
        return render_template('admin_products.html', products=products)

    return redirect(url_for('admin'))


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def secure_filename(filename):
    from werkzeug.utils import secure_filename
    return secure_filename(filename)


@app.route('/submit_cart', methods=['POST'])
def submit_cart():
    customer_name = session.get('customer_name')
    customer_phone = session.get('customer_phone')
    customer_address = session.get('customer_address')
    cart = session.get('cart', [])
    if not customer_name or not cart:
        flash('No cart items or customer information available.', 'error')
        return redirect(url_for('carts'))

    conn = get_db_connection()
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        # Generate a unique cart ID (UUID)
        cart_id = str(uuid.uuid4())

        # Insert all items in the cart with the same cart_id
        for item in cart:
            cursor.execute('''
                INSERT INTO orders (id, customer_name, product_name, product_brand, product_category, quantity, price, total_price, date, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cart_id,  # Use the same unique cart_id for all items in the cart
                customer_name,
                item['product_name'],
                item['product_brand'],
                item['product_category'],
                item['quantity'],
                item['price'],
                item['quantity'] * item['price'],
                current_date,
                customer_phone,
                customer_address
            ))

        conn.commit()
        session.pop('cart', None)  # Clear the cart session
        flash('Order placed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {e}', 'error')
    finally:
        conn.close()

    return redirect(url_for('carts'))

@app.route('/get_order_ids', methods=['GET'])
def get_order_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE status = 'Received'")
    order_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(order_ids=order_ids)

@app.route('/assign_order', methods=['POST'])
def assign_order():
    data = request.json
    order_id = data['orderId']
    delivery_boy = data['deliveryBoy']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch customer details from the orders table
    cursor.execute("SELECT customer_name, phone, address FROM orders WHERE id = ?", (order_id,))
    customer_details = cursor.fetchone()

    if customer_details:
        customer_name, phone, address = customer_details

        # Insert into delivery_orders table
        cursor.execute("""
            INSERT INTO delivery_orders (order_id, delivery_boy, customer_name, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, delivery_boy, customer_name, phone, address))

        # Update the status of the order in the orders table to 'In Process'
        cursor.execute("UPDATE orders SET status = 'In Process' WHERE id = ?", (order_id,))

        conn.commit()

    conn.close()

    return '', 200


@app.route('/delete_from_cart/<int:index>', methods=['POST'])
def delete_from_cart(index):
    cart_items = session.get('cart', [])

    if 0 <= index < len(cart_items):
        # Remove the item at the specified index
        del cart_items[index]
        session['cart'] = cart_items  # Update the cart in the session
        session.modified = True  # Mark the session as modified

    return redirect(url_for('carts'))


@app.route('/admin/orders')
def orders():
    if 'admin_name' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders')
        orders = cursor.fetchall()
        return render_template('admin_orders.html',orders=orders)
    return redirect(url_for('admin'))

@app.route('/admin/customers')
def customers():
    if 'admin_name' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customer')
        customers = cursor.fetchall()
        return render_template('admin_customers.html',customers=customers)
    return redirect(url_for('admin'))

@app.route('/admin/logout')
def logout():
    session.pop('admin_name', None)
    return redirect(url_for('admin'))

@app.route('/admin/deliveries')
def deliveries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_orders')
    deliveries = cursor.fetchall()
    return render_template('admin_deliveries.html',deliveries=deliveries)

@app.route('/customer/deliveries')
def customer_delivery():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_orders')
    deliveries = cursor.fetchall()
    return render_template('customer_deliveries.html', deliveries=deliveries)

@app.route('/customer/logout')
def customer_logout():
    session.pop('customer_name', None)
    return redirect(url_for('customer'))

@app.route('/customer/products')
def customer_products():
    page = int(request.args.get('page', 1))
    per_page = 6  # Number of products per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()
    # Get total number of products
    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]

    # Fetch products for the current page
    cursor.execute(
        'SELECT image1, product_name, product_brand, product_category, price, discount, id FROM products LIMIT ? OFFSET ?',
        (per_page, offset))
    products = cursor.fetchall()

    conn.close()

    total_pages = (total_products + per_page - 1) // per_page  # Calculate total pages
    return render_template('customer_products.html', products=products, page=page, total_pages=total_pages,count=customer_orders_count(),cartcount=get_cart_count())


def get_product_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_cart_count():
    if 'cart' in session:
        return len(session['cart'])
    else:
        return 0

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    product = get_product_by_id(product_id)  # Implement this function to get product details
    if not product:
        return jsonify({'message': 'Product not found!'}), 404

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    for item in cart:
        if item['product_id'] == product[0]:
            item['quantity'] += 1  # Increase quantity if product already in cart
            session.modified = True
            return jsonify({'message': 'Product quantity updated in cart!'})

    # Add new product to cart if not already present
    session['cart'].append({
        'product_id': product[0],
        'product_name': product[1],
        'product_brand': product[2],
        'product_category': product[3],
        'price': product[4],
        'discount': product[5],
        'image1': product[7],
        'quantity': 1
    })

    session.modified = True
    return jsonify({'message': 'Product added to cart!'})
@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    index = request.json.get('index')
    new_quantity = request.json.get('quantity')

    if 'cart' not in session:
        return jsonify({'message': 'Cart is empty!'}), 400

    cart = session['cart']
    if index < 0 or index >= len(cart):
        return jsonify({'message': 'Invalid index!'}), 400

    cart[index]['quantity'] = int(new_quantity)
    session.modified = True
    return jsonify({'message': 'Quantity updated!'})

@app.route('/customer/carts')
def carts():
    cart_items = session.get('cart', [])
    grand_total = 0
    for index, item in enumerate(cart_items):
        quantity = request.form.get('quantity',1, type=int)
        price = item['price']
        discount = item['discount']
        total_price = (price * (1 - discount / 100)) * quantity
        grand_total = grand_total + total_price

    return render_template('customer_carts.html', cart_items=cart_items, enumerate=enumerate,grand_total=grand_total,count=customer_orders_count(),cartcount=get_cart_count())

def customer_orders_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM orders WHERE customer_name = ?', (session['customer_name'],))
    count = cursor.fetchone()[0]
    return count

@app.route('/customer/orders')
def customer_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE customer_name = ?', (session['customer_name'],))
    orders = cursor.fetchall()
    return render_template('customer_orders.html',orders=orders,count=customer_orders_count(),cartcount=get_cart_count())

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        if 'login_submit' in request.form:
            username = request.form['username']
            password = request.form['password']
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM customer WHERE customer_name = ? AND customer_password = ?',
                                (username, password)).fetchone()
            conn.close()
            if user:
                session['customer_name'] = user['customer_name']
                session['customer_phone'] = user['phone']
                session['customer_address'] = user['address']
                print(f'Count:{customer_orders_count()}')
                return render_template('customer_base.html',count=customer_orders_count())
            else:
                return 'Invalid credentials'
        elif 'register_submit' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            conn = get_db_connection()
            conn.execute('INSERT INTO customer (customer_name, customer_password, email, phone, address) VALUES (?, ?, ?, ?, ?)',
                         (username, password, email, phone, address))
            conn.commit()
            conn.close()
            return render_template('customer_base.html',count=customer_orders_count())
    return render_template('customer_login_register.html')


if __name__ == '__main__':
    app.run(debug=True)
