from flask import Flask
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from openai import OpenAI

db = SQLAlchemy()
jwt = JWTManager()
openai_client = OpenAI() #Add api key


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agents.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'secret'
    from .models import Agent
    from .routes import routes
    app.register_blueprint(routes)
    
    jwt.init_app(app)
    db.init_app(app)
    create_db(app)
    
    
    return app

def create_db(app):
    if not(os.path.exists('instance/agents.db')):
        with app.app_context():
            db.create_all()