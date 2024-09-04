from itertools import count

from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify, flash
import sqlite3

delivery_bp = Blueprint('delivery', __name__, template_folder='../templates/delivery')

def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

def update_status_in_table(table_name, order_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    if table_name == 'orders':
        cursor.execute(f"UPDATE {table_name} SET status = ? WHERE id = ?", (new_status, order_id))
    else:
        cursor.execute(f"UPDATE {table_name} SET status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

@delivery_bp.route('/update-order-status/<order_id>', methods=['POST'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')
    update_status_in_table('orders', order_id, new_status)
    update_status_in_table('delivery_orders', order_id, new_status)
    return jsonify({"message": "Order status updated successfully!"}), 200

@delivery_bp.route('/', methods=['GET', 'POST'])
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
            return redirect(url_for('delivery.delivery'))
    if 'delivery_name' not in session:
        return render_template('delivery_login.html')
    else:
        return render_template('delivery_base.html')

@delivery_bp.route('/queues')
def delivery_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_orders where delivery_boy = ?',(session['delivery_name'],))
    deliveries = cursor.fetchall()
    return render_template('delivery_queues.html', deliveries=deliveries, count=curret_delivery_count())

def curret_delivery_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM delivery_orders WHERE delivery_boy = ? AND status != ?',
                   (session['delivery_name'], 'delivered'))
    count = cursor.fetchone()[0]
    conn.close()
    return count

@delivery_bp.route('/current_queues')
def delivery_current_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM delivery_orders WHERE delivery_boy = ? AND status != ?',(session['delivery_name'], 'delivered'))
    deliveries = cursor.fetchall()
    return render_template('delivery_current_queues.html', deliveries=deliveries, count=curret_delivery_count())

@delivery_bp.route('/get-order-details/<order_id>', methods=['GET'])
def get_order_details(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT product_name, product_brand, quantity, price FROM orders WHERE id = ?', (order_id,))
    orders = cursor.fetchall()
    conn.close()
    order_details = [dict(row) for row in orders]

    return jsonify(order_details)

@delivery_bp.route('/delivery/logout')
def delivery_logout():
    session.pop('delivery_name', None)
    return redirect(url_for('delivery.delivery'))


@delivery_bp.route('/base')
def base():
    return render_template('delivery_base.html')