from . import db 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80))
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120))

    def __repr__(self):
        return f'<User {self.username}>'
