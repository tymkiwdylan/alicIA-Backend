
import logging
import time
import json
import requests
from twilio.twiml.messaging_response import MessagingResponse
from tinydb import TinyDB
from tinydb import Query
from .models import Agent, Conversation, Message
from twilio.rest import Client
from . import client, openai_client, functions, db


def register_functions():
    function_settings = []
    
    for _ , tool_class in functions.items():
        function_settings.append(
            {
                'type': 'function',
                'function': tool_class.settings
                }
            )
    
    return function_settings

def call_functions(company_name, required_functions):
    
    tool_outputs = []
    
    for required_function in required_functions:
        output = {'tool_call_id': required_function.id,
                  'output': ''}
        function_name = required_function.function.name
        args = json.loads(required_function.function.arguments)
        
        function = functions.get(function_name, None)
        
        if function is None:
            return {'Error': "Function does not exist"}
        
        result = function.execute(company_name, **args)
        logging.debug(f'This is the actual response: {result}')
        
        output['output'] = json.dumps(result)
        
        tool_outputs.append(output)
    
    logging.debug(f'Now this is what we send to the api: {tool_outputs}')
    return tool_outputs
    


def sendMessage(body_mess, phone_number, business_number):
    try:
        MAX_MESSAGE_LENGTH = 550
        agent = Agent.query.filter_by(business_phone_number=business_number).first()
        message_client =  Client(agent.twilio_sid, agent.twilio_auth_token)

        # Split the message into lines and words
        lines = body_mess.split('\n')
        chunks = []
        current_chunk = ""

        for line in lines:
            words = line.split()
            for word in words:
                if len(current_chunk) + len(word) + 1 > MAX_MESSAGE_LENGTH:
                    # Save the current chunk and start a new one
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                current_chunk += word + " "

            # Add a newline character at the end of each line
            current_chunk += "\n"

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            part_number = f"[{i+1}/{total_chunks}]"
            final_chunk = f"{chunk} {part_number}"
            
            logging.debug(f"Sending message chunk: {final_chunk} to {phone_number}")
            print(f"Sending message chunk: {final_chunk} from {business_number}")
            message = message_client.messages.create(
                from_='whatsapp:' + business_number,
                body=final_chunk,
                to='whatsapp:' + phone_number
            )
            
            time.sleep(1)  # Optional: To avoid rate-limiting

    except Exception as e:
        logging.error(f"Failed to send message. Error: {str(e)}")
        

def sendWhatsAppMessage(body_msg, recipient_phone_number, agent):
    url = f"https://graph.facebook.com/v13.0/{agent.number_id}/messages"
    headers = {
        "Authorization": f"Bearer {agent.access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "text",
        "text": {"body": body_msg}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send WhatsApp message. Error: {response.text}")

def get_chatgpt_response(prompt, phone_number, business_number):

    # Fetch the thread_id for this number
    agent = Agent.query.filter_by(business_phone_number=business_number).first()
    
    try: 
        response = requests.get(f'http://auth:5000/is-active', params={'user_id': agent.user_id})
    except Exception as e:
        return "Agente inactivo"
        
    if not response.ok:
        return "Agente inactivo"

    
    # Get conversation
    
    company_name = Agent.query.get(agent.id).company_name
    
    conversation = Conversation.query.filter_by(phone_number=phone_number).first()
    
    if conversation is None:
        thread = openai_client.beta.threads.create()
        new_convo = Conversation(agent_id = agent.id,
                                 thread_id = thread.id,
                                 phone_number = phone_number
                                 )
        db.session.add(new_convo)
        db.session.commit()
        conversation = new_convo
        
        
        
    message = openai_client.beta.threads.messages.create(
    thread_id=conversation.thread_id,
    role="user",
    content=prompt
    )
    
    new_message = Message(conversation_id=conversation.id,
                          role = 'user',
                          content = message.content[0].text.value)
    
    
    db.session.add(new_message)
    db.session.commit()
        
    run = openai_client.beta.threads.runs.create(
    thread_id=conversation.thread_id,
    assistant_id=agent.id,
    )
    
    
    while True:
        time.sleep(1)
        run = openai_client.beta.threads.runs.retrieve(
        thread_id=conversation.thread_id,
        run_id=run.id
        )
        
        if run.status == "completed":
            messages = openai_client.beta.threads.messages.list(thread_id=conversation.thread_id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            
            new_message = Message(conversation_id=conversation.id,
                          role = 'assistant',
                          content = text)
            
            db.session.add(new_message)
            db.session.commit()
            
            return text
        if run.status == "requires_action":
            
            logging.debug(f'Functions to Call {run.required_action.submit_tool_outputs.tool_calls}')
            
            try:
            
                tool_outputs = call_functions(company_name, run.required_action.submit_tool_outputs.tool_calls)
                
                run = openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=conversation.thread_id,
                run_id=run.id,
                tool_outputs= tool_outputs,
                )
                
            except:
                
                run = openai_client.beta.threads.runs.cancel(
                thread_id=conversation.thread_id,
                run_id=run.id
                )
            
        if run.status == "expired":
            return "Timeout Error"
        if run.status == "cancelled":
            return "Request cancelled"
        if run.status == "failed":
            return "Request Failed to Complete"
        