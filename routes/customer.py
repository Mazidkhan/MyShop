from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify, flash
import sqlite3
import uuid
import os
from datetime import datetime

customer_bp = Blueprint('customer', __name__, template_folder='../templates/customer')

def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_cart_count():
    if 'cart' in session:
        return len(session['cart'])
    else:
        return 0

def get_product_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def customer_orders_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM orders WHERE customer_name = ?', (session['customer_name'],))
    count = cursor.fetchone()[0]
    return count

@customer_bp.route('/submit_cart', methods=['POST'])
def submit_cart():
    customer_name = session.get('customer_name')
    customer_phone = session.get('customer_phone')
    customer_address = session.get('customer_address')
    cart = session.get('cart', [])
    if not customer_name or not cart:
        flash('No cart items or customer information available.', 'error')
        return redirect(url_for('customer.carts'))

    conn = get_db_connection()
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        # Generate a unique cart ID (UUID)

        # Insert all items in the cart with the same cart_id
        for item in cart:
            cursor.execute('''
                INSERT INTO orders (customer_name, product_name, product_brand, product_category, quantity, price, total_price, date, phone, address, owner_name, shop_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer_name,
                item['product_name'],
                item['product_brand'],
                item['product_category'],
                item['quantity'],
                item['price'],
                item['quantity'] * item['price'],
                current_date,
                customer_phone,
                customer_address,
                item['owner_name'],
                item['shop_name']
            ))

        conn.commit()
        session.pop('cart', None)  # Clear the cart session
        flash('Order placed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {e}', 'error')
    finally:
        conn.close()

    return redirect(url_for('customer.carts'))

@customer_bp.route('/add_to_cart', methods=['POST'])
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

    session['cart'].append({
        'product_id': product['id'],
        'product_name': product['product_name'],
        'product_brand': product['product_brand'],
        'product_category': product['product_category'],
        'price': product['price'],
        'discount': product['discount'],
        'image1': product['image1'],
        'quantity': 1,
        'shop_name': product['shop_name'],
        'owner_name': product['owner_name']
    })

    session.modified = True
    return jsonify({'message': 'Product added to cart!'})

@customer_bp.route('/update_quantity', methods=['POST'])
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

@customer_bp.route('/delete_from_cart/<int:index>', methods=['POST'])
def delete_from_cart(index):
    cart_items = session.get('cart', [])

    if 0 <= index < len(cart_items):
        # Remove the item at the specified index
        del cart_items[index]
        session['cart'] = cart_items  # Update the cart in the session
        session.modified = True  # Mark the session as modified

    return redirect(url_for('customer.carts'))

@customer_bp.route('/deliveries')
def customer_delivery():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Revised SQL query to handle both scenarios: orders not yet assigned and those assigned but not delivered
    cursor.execute('''
        SELECT orders.id AS order_id, orders.status AS order_status, 
               delivery_orders.delivery_boy, delivery_boys.phone, 
               delivery_boys.email
        FROM orders
        LEFT JOIN delivery_orders ON orders.id = delivery_orders.order_id
        LEFT JOIN delivery_boys ON delivery_orders.delivery_boy = delivery_boys.delivery_boy
        WHERE orders.customer_name = ? AND 
              (orders.status != ? OR delivery_orders.status != ?)
    ''', (session['customer_name'], 'delivered', 'delivered'))

    deliveries = cursor.fetchall()

    return render_template('/customer/customer_deliveries.html',
                           deliveries=deliveries,
                           cartcount=get_cart_count(),
                           count=customer_orders_count())


@customer_bp.route('/logout')
def customer_logout():
    session.pop('customer_name', None)
    return redirect(url_for('customer.customer'))


@customer_bp.route('/products')
def customer_products():
    page = int(request.args.get('page', 1))
    per_page = 12  # Number of products per page
    offset = (page - 1) * per_page
    search = request.args.get('search', '')
    selected_location = request.args.get('location', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build the query with optional filters, joining with the merchants table for location
    query = '''
        SELECT p.image1, p.product_name, p.product_brand, p.product_category, p.price, p.discount, p.id, p.shop_name, p.owner_name
        FROM products p
        JOIN merchants m ON p.shop_name = m.shop_name AND p.owner_name = m.owner_name
        WHERE 1=1
    '''
    params = []

    if search:
        query += ' AND (p.product_name LIKE ? OR p.product_brand LIKE ? OR p.product_category LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    if selected_location:
        query += ' AND m.location = ?'
        params.append(selected_location)

    # Get total number of filtered products
    cursor.execute(f'SELECT COUNT(*) FROM ({query})', params)
    total_products = cursor.fetchone()[0]

    # Fetch products for the current page
    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    cursor.execute(query, params)
    products = cursor.fetchall()

    # Fetch distinct locations from merchants for the dropdown
    cursor.execute('SELECT DISTINCT location FROM merchants')
    locations = cursor.fetchall()

    conn.close()

    total_pages = (total_products + per_page - 1) // per_page  # Calculate total pages
    return render_template(
        'customer/customer_products.html',
        products=products,
        page=page,
        total_pages=total_pages,
        locations=[loc[0] for loc in locations],
        selected_location=selected_location,
        count=customer_orders_count(),
        cartcount=get_cart_count()
    )

@customer_bp.route('/profile')
def customer_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('select * from customer where customer_name=?',(session['customer_name'],))
    customer=cursor.fetchall()

    return render_template('/customer/customer_profile.html',customer=customer,count=customer_orders_count(),cartcount=get_cart_count())

@customer_bp.route('/submit_review/<int:product_id>/<string:name>/<string:brand>', methods=['POST'])
def submit_review(product_id,name,brand):
    review = request.form['review']
    customer_name = session['customer_name']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO product_reviews (id, product_name, product_brand, customer_name, review) VALUES (?, ?, ?, ?, ?)",
        (product_id, name, brand, customer_name, review)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('customer.product_description', product_id=product_id))


@customer_bp.route('/products/description/<int:product_id>')
def product_description(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products where id = ?',(product_id,))
    products = cursor.fetchall()
    cursor.execute('SELECT * FROM product_reviews where id = ?',(product_id,))
    reviews = cursor.fetchall()
    return render_template('product_description.html', products=products,count=customer_orders_count(),cartcount=get_cart_count(),reviews=reviews)
    conn.close()

@customer_bp.route('/carts')
def carts():
    cart_items = session.get('cart', [])
    grand_total = 0
    for index, item in enumerate(cart_items):
        quantity = request.form.get('quantity',1, type=int)
        price = item['price']
        discount = item['discount']
        total_price = (price * (1 - discount / 100)) * quantity
        grand_total = grand_total + total_price
    return render_template('/customer/customer_carts.html', cart_items=cart_items, enumerate=enumerate,grand_total=grand_total,count=customer_orders_count(),cartcount=get_cart_count())

@customer_bp.route('/orders')
def customer_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM orders
        WHERE customer_name = ?
        ORDER BY CASE WHEN status != 'delivered' THEN 0 ELSE 1 END
    ''', (session['customer_name'],))

    orders = cursor.fetchall()
    return render_template('/customer/customer_orders.html',orders=orders,count=customer_orders_count(),cartcount=get_cart_count())

@customer_bp.route('/', methods=['GET', 'POST'])
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
                return render_template('/customer/customer_base.html',count=customer_orders_count())
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
            return render_template('/customer/customer_base.html')
    return render_template('/customer/customer_login_register.html')
