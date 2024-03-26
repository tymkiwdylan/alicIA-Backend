from . import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    company_name = db.Column(db.String(256))
    stripe_customer_id = db.Column(db.String(256))
    stripe_subscription_id = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=False)
    
    def jsonify(self):
        return {
            'id': self.id,
            'email': self.email,
            'company_name': self.company_name
        }
