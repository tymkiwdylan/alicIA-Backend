import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') # Use appropriate database
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change to a random secret
    # CORS(app)
    
    from .models import User
    db.init_app(app)
    create_db(app)
    CORS(app)
    from .routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app

def create_db(app):
    if not(os.path.exists('instance/auth.db')):
        with app.app_context():
            db.create_all()