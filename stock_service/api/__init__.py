from flask import Flask
from flask_pymongo import PyMongo
import os

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['MONGO_URI'] = 'mongodb+srv://tymkiwdylan:fire2134@stock.moe8n7g.mongodb.net/stock?retryWrites=true&w=majority&appName=AtlasApp'
    
    from .routes import routes
    app.register_blueprint(routes)
    
    mongo.init_app(app)
    
    return app