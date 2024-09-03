from flask import Flask, render_template
from routes.customer import customer_bp
from routes.admin import admin_bp
from routes.delivery import delivery_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production!
app.config['UPLOAD_FOLDER'] = 'static/images'  # Folder where uploaded files will be saved
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(delivery_bp, url_prefix='/delivery')

@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
