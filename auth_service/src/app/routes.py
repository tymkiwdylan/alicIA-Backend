from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .models import User
from .services import generate_token, verify_token

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    # Get data from request
    data = request.get_json()

    # Validate data
    email = data.get('email')
    password = data.get('password')
    company_name = data.get('company_name')

    if not email or not password or not company_name:
        return jsonify({'message': 'Missing data'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 409

    # Create new user
    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        company_name=company_name
    )

    # Add new user to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    # Get data from request
    data = request.get_json()

    # Validate data
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Generate token
    token = generate_token(user.id)

    return jsonify({'token': token.decode('UTF-8')}), 200

@auth.route('/validate', methods=['POST'])
def validate():
    # Get the token from request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Optional: strip 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]

    # Verify the token
    if verify_token(token):
        return jsonify({'message': 'Token is valid'}), 200
    else:
        return jsonify({'message': 'Token is invalid or expired'}), 401
