from flask import Flask
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .models import User
import os

mongo = PyMongo()
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['MONGO_URI'] = 'mongodb+srv://tymkiwdylan:fire2134@stock.moe8n7g.mongodb.net/stock?retryWrites=true&w=majority&appName=AtlasApp'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'secret'
    from .routes import routes
    from .auth import auth
    app.register_blueprint(routes)
    app.register_blueprint(auth)
    
    mongo.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    
    create_db(app)
    
    
    return app

def create_db(app):
    if not(os.path.exists('instance/users.db')):
        with app.app_context():
            db.create_all()