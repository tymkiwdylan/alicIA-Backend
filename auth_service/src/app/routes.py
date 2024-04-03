import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from . import db, sg
from .models import User
import jwt
import stripe
from .services import generate_token, verify_token, send_email

stripe.api_key = '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'
stripe_webhook_secret = 'whsec_Q7CMLhNjqCHwYdZfa15fxOGl4bqkyk6D'

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

    # Create new user in the database
    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        company_name=company_name
    )
    db.session.add(new_user)
    db.session.flush()  # Flush to assign new_user an ID without committing

    # Create a Stripe Customer
    try:
        stripe_customer = stripe.Customer.create(
            email=email,
            name=company_name,  # Optional: adjust as per your model
            description=f"Customer for {company_name} with email {email}",
        )
        # Save Stripe Customer ID in your database
        new_user.stripe_customer_id = stripe_customer.id
        db.session.commit()
    except stripe.error.StripeError as e:
        # Handle Stripe errors e.g., API connection errors
        db.session.rollback()
        return jsonify({'message': 'Stripe Customer creation failed', 'error': str(e)}), 500

    return jsonify({'message': 'User registered successfully', 'data': new_user.jsonify(), 'stripe_customer_id': stripe_customer.id}), 201

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

    return jsonify({'token': token}), 200

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
    payload = verify_token(token)
    if payload != False:
        payload['active'] = User.query.get(payload['user_id']).active
        return jsonify({'message': 'Token is valid', 'data': payload }), 200
    else:
        return jsonify({'message': 'Token is invalid or expired'}), 401
    
@auth.route('/is-active', methods=['GET'])
def is_active():
    # Get the user_id from the query string and then fetch the user and return their active status
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if not user.active:
        return jsonify({'message': 'User is not active'}), 400
    
    return jsonify({'message': 'User is active'}), 200


@auth.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    user_id = request.get_json().get('user_id')
    
    # Fetch the user from the database to get their Stripe Customer ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.stripe_customer_id:
        return jsonify({'message': 'Stripe customer ID missing for user'}), 400

    try:
        # Create a new checkout session using the existing Stripe Customer ID
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,  # Use the stored Stripe Customer ID
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1P1RkNJE3OWBK5PLm0whlfRY', # Use the recurring price ID from Stripe
                'quantity': 1,
            }],
            mode='subscription',
            allow_promotion_codes=True,
            success_url='https://alicia.nortedev.net/chatbot',  # Adjust as needed
            cancel_url=f'https://alicia.nortedev.net/auth-settings',  # Adjust as needed
            metadata={'user_id': user_id}  # Add user ID to the metadata
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400



@auth.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_secret)

        # Proceed only if the event is checkout.session.completed
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Extract user_id from session metadata
            user_id = session.get('metadata', {}).get('user_id')
            print("USER ID:" + user_id)
            # Retrieve the subscription ID from the session (if needed) and verify its status
            # This step assumes you want to further verify the subscription status
            subscription_id = session.get('subscription')
            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                if subscription and subscription.status == 'active':
                    user = User.query.get(user_id)
                    if user:
                        # Activate the user
                        user.active = True
                        user.stripe_subscription_id = subscription_id
                        db.session.commit()
                        return jsonify({'status': 'success'}), 200
                    else:
                        # Handle non-existent user
                        return jsonify({'error': 'User does not exist'}), 400
                else:
                    # Handle unsuccessful subscription
                    return jsonify({'error': 'Subscription not active'}), 400
            else:
                # Handle missing subscription ID
                return jsonify({'error': 'Missing subscription ID'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    # Authenticate the user (this is pseudo-code, adapt based on your auth system)
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]
        
    payload = verify_token(token)
    if not payload:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.stripe_subscription_id:
        return jsonify({'message': 'No active subscription found'}), 404

    try:
        # Cancel the subscription on Stripe
        stripe.Subscription.delete(user.stripe_subscription_id)

        # Update user's status in your database
        user.active = False
        db.session.commit()

        return jsonify({'message': 'Subscription cancelled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth.route('/change-password', methods=['POST'])
def change_password():
    # Authenticate the user (this is pseudo-code, adapt based on your auth system)
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]
    
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get data from request
    data = request.get_json()

    # Validate data
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'message': 'Old and new password are required'}), 400

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'message': 'Invalid old password'}), 400

    # Update user's password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200

@auth.route('/change-email', methods=['POST'])
def change_email():
    # Authenticate the user (this is pseudo-code, adapt based on your auth system)
    token = request.headers.get('Authorization')
    if token.startswith('Bearer '):
        token = token[7:]
    
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'message': 'Unauthorized'}), 401

    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get data from request
    data = request.get_json()

    # Validate data
    new_email = data.get('new_email')

    if not new_email:
        return jsonify({'message': 'New email is required'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        return jsonify({'message': 'User already exists with the new email'}), 409

    # Update user's email
    user.email = new_email
    db.session.commit()

    return jsonify({'message': 'Email updated successfully'}), 200

@auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    user  = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    reset_token = jwt.encode({'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                             current_app.config['SECRET_KEY'], algorithm='HS256')
    
    user.reset_token = reset_token
    
    db.session.commit()
    
    reset_url = f"https://alicia.nortedev.net/reset-password?token={reset_token}"
    
    msg = f"Click acá para restablecer tu contraseña: {reset_url}"
    
    subject = "Restablecer contraseña: alcIA"

    response = send_email(subject, msg, email)
    
    if response:
        return jsonify({'message': 'Email sent successfully'}), 200
    
    return jsonify({'message': 'Email could not be sent'}), 500


@auth.route('/reset-password', methods= ['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token and new password are required'}), 400
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        email = payload.get('email')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()
        
        return jsonify({'message': 'Password reset successfully'}), 200
    
    except:
        return jsonify({'message': 'Token invalida o expirada'}), 400
    