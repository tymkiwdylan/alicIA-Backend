from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from openai import OpenAI
import importlib
import pkgutil
from pathlib import Path 
from twilio.rest import Client
from flask_migrate import Migrate  

def load_tools_from_directory(directory):
    tools = {}

    # Convert string directory to Path object if necessary
    if isinstance(directory, str):
        directory = Path(directory)

    # Ensure the directory is a package by checking for __init__.py
    if not (directory / '__init__.py').exists():
        raise ValueError(f"{directory} is not a package. Missing '__init__.py'.")

    # Import the package
    package = importlib.import_module(directory.name)

    # Iterate through the modules in the package
    for _, module_name, _ in pkgutil.iter_modules([directory]):
        module = importlib.import_module(f"{directory.name}.{module_name}")

        # Iterate over attributes of the module and find classes
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            # Check if the attribute is a class and defined in this module (not imported)
            if isinstance(attribute, type) and attribute.__module__ == module.__name__:
                tools[attribute_name] = attribute

    return tools

db = SQLAlchemy()
openai_client = OpenAI(api_key="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") #Add api key
functions = load_tools_from_directory('functions')

account_sid = 'ACc83e06b70d7d64abe223fe0149926f4b'
auth_token = '17185508f9a021a42846035f0932f781'
client = Client(account_sid, auth_token)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://alicia:alicia@34.95.254.138/customer" 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'secret'
    from .models import Agent, Conversation, Message
    from .routes import routes
    app.register_blueprint(routes)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app
      