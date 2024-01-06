from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'  # Use appropriate database
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change to a random secret

    db.init_app(app)

    from .routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
