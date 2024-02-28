import jwt
from flask import current_app
from functools import wraps
from flask import request, jsonify
from .models import User

def generate_token(user_id):
    
    company_name = User.query.filter_by(id=user_id).first().company_name
    
    payload = {
        'user_id': user_id,
        'company_name': company_name
    }
    
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload  # Or return True/False based on your requirement
    except jwt.ExpiredSignatureError:
        # Handle the expired token case
        return False
    except jwt.InvalidTokenError:
        # Handle the invalid token case
        return False
