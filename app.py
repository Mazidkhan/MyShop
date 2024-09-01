from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify


def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Change this in production!
    app.config['UPLOAD_FOLDER'] = 'static/images'  # Folder where uploaded files will be saved
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

    from routes.customer import customer_bp
    from routes.admin import admin_bp
    from routes.delivery import delivery_bp

    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(delivery_bp, url_prefix='/delivery')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)