from flask import Blueprint, render_template, request, session, flash, redirect, url_for, current_app, jsonify
import sqlite3
import os

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin/')

def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename(filename):
    from werkzeug.utils import secure_filename
    return secure_filename(filename)

def in_process_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM orders WHERE status = ? and owner_name = ?', ('Received',session['admin_name']))
    count = cursor.fetchone()[0]
    return count

@admin_bp.route('/assign_order', methods=['POST'])
def assign_order():
    data = request.json
    order_id = data['orderId']
    delivery_boy = data['deliveryBoy']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_name, phone, address FROM orders WHERE id = ?", (order_id,))
    customer_details = cursor.fetchone()

    if customer_details:
        customer_name, phone, address = customer_details
        cursor.execute("""
            INSERT INTO delivery_orders (order_id, delivery_boy, customer_name, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, delivery_boy, customer_name, phone, address))

        cursor.execute("UPDATE orders SET status = 'In Process' WHERE id = ?", (order_id,))
        conn.commit()
    conn.close()
    return '', 200

@admin_bp.route('/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        admin_name = request.form['admin_name']
        admin_password = request.form['admin_password']
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM merchants WHERE owner_name = ? AND password = ?', (admin_name, admin_password)).fetchone()
        conn.close()

        if admin:
            session['admin_shop'] = admin['shop_name']
            session['admin_name'] = admin['owner_name']
            return render_template('admin/admin_base.html')
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('admin.admin'))
    if 'admin_name' not in session:
        return render_template('admin/admin_login.html')
    else:
        return render_template('admin/admin_base.html')

@admin_bp.route('/add_delivery_boy', methods=['POST'])
def add_delivery_boy():
    data = request.json
    boy = data.get('boy')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')
    conn = get_db_connection()
    admin=session['admin_name']
    print(f'Admin:{admin}')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO delivery_boys (owner_name, shop_name, delivery_boy, phone, email, password) VALUES (?, ?, ?, ?, ?, ?)',
                   (session['admin_name'],session['admin_shop'],boy, phone, email, password))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@admin_bp.route('/update_product', methods=['PUT'])
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
    UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
    if image1:
        image1.save(os.path.join(UPLOAD_FOLDER, image1.filename))
    if image2:
        image2.save(os.path.join(UPLOAD_FOLDER, image2.filename))
    if image3:
        image3.save(os.path.join(UPLOAD_FOLDER, image3.filename))

    conn.close()
    return redirect(url_for('admin.admin'))

@admin_bp.route('/product/<int:product_id>', methods=['GET'])
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

@admin_bp.route('/delete_product/<int:product_id>', methods=['DELETE'])
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
            if image_filename and os.path.isfile(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

        flash('Product deleted successfully!')
    else:
        flash('Product not found!')

    conn.close()
    return '', 204  # No Content

@admin_bp.route('/products', methods=['GET', 'POST'])
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
            image1.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image1_filename))

        if image2 and allowed_file(image2.filename):
            image2_filename = secure_filename(image2.filename)
            image2.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image2_filename))

        if image3 and allowed_file(image3.filename):
            image3_filename = secure_filename(image3.filename)
            image3.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image3_filename))

        # Connect to the database
        cursor = conn.cursor()

        # Insert data into the database
        cursor.execute('''
            INSERT INTO products (product_name, product_brand, product_category, price, discount, stock, image1, image2, image3, shop_name, owner_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_name, product_brand, product_category, price, discount, stock, image1_filename, image2_filename,
              image3_filename, session['admin_shop'], session['admin_name']))

        conn.commit()

        return redirect(url_for('admin.products'))

    if 'admin_name' in session:
        products = conn.execute('SELECT * FROM products where owner_name = ?',(session['admin_name'],)).fetchall()
        conn.close()
        return render_template('admin/admin_products.html', products=products, count=in_process_count(), delivery_orders_count=delivery_orders_count())

    return redirect(url_for('admin.admin'))

@admin_bp.route('/orders')
def orders():
    if 'admin_name' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders where owner_name = ?',(session['admin_name'],))
        orders = cursor.fetchall()
        return render_template('admin/admin_orders.html',orders=orders, count=in_process_count(), delivery_orders_count=delivery_orders_count())
    return redirect(url_for('admin.admin'))


@admin_bp.route('/filter_orders')
def filter_orders():
    status = request.args.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()

    if status and status != "all":
        cursor.execute('SELECT * FROM orders WHERE status = ?', (status,))
    else:
        cursor.execute('SELECT * FROM orders')

    orders = cursor.fetchall()
    conn.close()

    orders_data = [dict(row) for row in orders]

    return jsonify(orders=orders_data)


@admin_bp.route('/customers')
def customers():
    if 'admin_name' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customer')
        customers = cursor.fetchall()
        return render_template('admin/admin_customers.html',customers=customers, count=in_process_count())
    return redirect(url_for('admin.admin'))

@admin_bp.route('/logout')
def logout():
    session.pop('admin_name', None)
    return redirect(url_for('admin.admin'))

@admin_bp.route('/register', methods=['POST'])
def register():
    owner_name = request.form['owner_name']
    phone = request.form['phone']
    address = request.form['address']
    city = request.form['city']
    location = request.form['location']
    shop_name = request.form['shop_name']
    password = request.form['password']

    conn = get_db_connection()
    conn.execute('INSERT INTO merchants (owner_name, phone, address, city, location, shop_name, password) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (owner_name, phone, address, city, location, shop_name, password))
    conn.commit()
    conn.close()
    session['admin_shop'] = shop_name
    session['admin_name'] = owner_name
    return render_template('admin/admin_base.html')

def delivery_orders_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM delivery_orders WHERE status != "delivered" and delivery_boy in (select delivery_boy from delivery_boys where owner_name=?)',(session['admin_name'],))
    count = cursor.fetchone()[0]
    conn.close()

    return count

@admin_bp.route('/deliveries')
def deliveries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_orders WHERE status != "delivered" and delivery_boy in (select delivery_boy from delivery_boys where owner_name=?)',(session['admin_name'],))
    deliveries = cursor.fetchall()
    return render_template('admin/admin_deliveries.html',deliveries=deliveries, count=in_process_count(), delivery_orders_count=delivery_orders_count())

@admin_bp.route('/delivery_boys')
def delivery_boys():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_boys where owner_name=?',(session['admin_name'],))
    delivery_boys = cursor.fetchall()
    return render_template('admin/admin_delivery_boys.html',delivery_boys=delivery_boys, count=in_process_count(), delivery_orders_count=delivery_orders_count())

@admin_bp.route('/get_order_ids', methods=['GET'])
def get_order_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE status = 'Received'")
    order_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(order_ids=order_ids)
