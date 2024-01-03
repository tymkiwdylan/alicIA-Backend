
import logging
import time
import json
from twilio.twiml.messaging_response import MessagingResponse
from tinydb import TinyDB
from tinydb import Query
from .models import Agent, Conversation, Message
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

def call_function(function_name, **kwargs):
    function = functions.get(function_name, None)
    print(function_name)
    
    if function is None:
        return {'Error': "Function does not exist"}
    
    result = function.execute(**kwargs)
    
    return result['data']


def sendMessage(body_mess, phone_number):
    try:
        MAX_MESSAGE_LENGTH = 550 

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
            
            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=final_chunk,
                to='whatsapp:' + phone_number
            )
            
            time.sleep(1)  # Optional: To avoid rate-limiting

    except Exception as e:
        logging.error(f"Failed to send message. Error: {str(e)}")

def get_chatgpt_response(prompt, phone_number, business_number):

    # Fetch the thread_id for this number
    agent = Agent.query.filter_by(business_phone_number=business_number).first()
    
    if agent is None:
        return 'This agent has not being set up yet'
    
    # Get conversation
    
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
            tool_call_id = run.required_action.submit_tool_outputs.tool_calls[0]
            function_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
            function_arguments = json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            function_response = call_function(function_name, **function_arguments)
            
            print(function_response)
            
            run = openai_client.beta.threads.runs.submit_tool_outputs(
            thread_id=conversation.thread_id,
            run_id=run.id,
            tool_outputs= [
                    {
                    "tool_call_id": tool_call_id.id,
                    "output": function_response,
                    }
                ],
            )
        if run.status == "expired":
            return "Timeout Error"
        if run.status == "cancelled":
            return "Request cancelled"
        if run.status == "failed":
            return "Request Failed to Complete"
        