import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv
from flask_migrate import Migrate  # Import Flask-Migrate

load_dotenv()

db = SQLAlchemy()
sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://alicia:alicia@34.95.254.138/auth" # Use appropriate database
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change to a random secret
    
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    CORS(app)
    
    # Import models here to ensure they are known to Flask-Migrate before running migrations
    from .models import User

    # The create_db function is not needed anymore since Flask-Migrate handles database initialization
    # from .models import User

    from .routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
