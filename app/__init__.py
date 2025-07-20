from flask import Flask


def create_app():
    app = Flask(__name__)
    from .routes import inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    return app
