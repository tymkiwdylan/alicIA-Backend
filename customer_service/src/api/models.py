from . import db 

class Agent(db.Model):
    id = db.Column(db.String(256), primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    business_phone_number = db.Column(db.String(256), unique=True, nullable=False)
    number_id = db.Column(db.String(256), unique=True)
    description = db.Column(db.String(512))
    tone = db.Column(db.String(256))
    company_name = db.Column(db.String(128))
    waba_id = db.Column(db.String(256), unique=True, nullable=False)  # WhatsApp Business Account ID
    facebook_page_id = db.Column(db.String(256), unique=True)  # Facebook Page ID linked to WABA
    access_token = db.Column(db.String(512), nullable=False)  # Access token for API calls
    token_expiry = db.Column(db.DateTime)  # Expiry date/time of the access token
    conversations = db.relationship('Conversation')

    def jsonify(self):
        conversations = [conversation.jsonify() for conversation in self.conversations]

        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_phone_number': self.business_phone_number,
            'number_id': self.number_id,
            'description': self.description,
            'tone': self.tone,
            'company_name': self.company_name,
            'waba_id': self.waba_id,
            'facebook_page_id': self.facebook_page_id,
            'access_token': self.access_token,
            'token_expiry': self.token_expiry.isoformat() if self.token_expiry else None,
            'conversations': conversations
        }
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    agent_id = db.Column(db.String(256), db.ForeignKey('agent.id'))
    thread_id = db.Column(db.String(256), unique = True)
    phone_number = db.Column(db.String(256))
    messages = db.relationship('Message')
    
    def jsonify(self):
        
        messages = [message.jsonify() for message in self.messages]
        
        return {
            'id': self.id,
            'messages': messages,
            'agent_id': self.agent_id,
            'phone_number': self.phone_number,
            'thread_id': self.thread_id
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