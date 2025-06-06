from . import db 

class Agent(db.Model):
    id = db.Column(db.String(256), primary_key = True)
    user_id = db.Column(db.Integer, unique = True, nullable = False)
    description = db.Column(db.String(512))
    custom_instructions = db.Column(db.Text)
    tone = db.Column(db.Text)
    company_name = db.Column(db.String(128))
    conversations = db.relationship('Conversation')
    
    def jsonify(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'company_name': self.company_name,
            'tone': self.tone,
            'custom_instructions': self.custom_instructions
        }
    
    
class Conversation(db.Model):
    id = db.Column(db.String(256), primary_key = True)
    agent_id = db.Column(db.String(256), db.ForeignKey('agent.id'))
    messages = db.relationship('Message')
    
    def jsonify(self):
        messages = [message.jsonify() for message in self.messages]
        return {
            'id' : self.id,
            'agent_id': self.agent_id,
            'messages': messages
        }
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    role = db.Column(db.String(40))
    conversation_id = db.Column(db.String(256), db.ForeignKey('conversation.id'))
    content = db.Column(db.Text)
    
    def jsonify(self):
        
        return {
            'id' : self.id,
            'role': self.role,
            'conversation_id': self.conversation_id,
            'content' : self.content
        }