from . import db 

class Agent(db.Model):
    id = db.Column(db.String(256), primary_key = True)
    user_id = db.Column(db.Integer, unique = True, nullable = False)
    description = db.Column(db.String(512))
    tone = db.Column(db.String(256))
    company_name = db.Column(db.String(128))
    conversations = db.relationship('Conversation')
    
    
class Conversation(db.Model):
    id = db.Column(db.String(256), primary_key = True)
    agent_id = db.Column(db.String(256), db.ForeignKey('agent.id'))