import logging
import time
import json
import secrets
from openai import OpenAI
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from tinydb import TinyDB
from tinydb import Query
import requests

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize OpenAI API key
openai_client = OpenAI(api_key="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")

# Twilio Configuration
account_sid = 'ACc83e06b70d7d64abe223fe0149926f4b'
auth_token = '17185508f9a021a42846035f0932f781'
client = Client(account_sid, auth_token)

# Initialize the in-memory database
db = TinyDB('db.json')
query = Query()

assistant_id = "asst_YlRCLTZpyV7YnAOorUqrcyQT"

def search_item(args):
    query = args['query']
    response = requests.get("http://127.0.0.1:7000/search", params={'query': query})
    
    return response.json()['data']

def inventory_overview(args):
    response = requests.get('http://127.0.0.1:7000/overview')
    
    return response.json()['data']

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

def get_chatgpt_response(prompt, phone_number):
    logging.debug(f"Received prompt: {prompt}")

    # Fetch the thread_id for this number
    thread_list = db.search(query.phone_number == phone_number)
    thread_id = thread_list[0]['thread_id'] if len(thread_list) > 0 else None
    
    if thread_id is None:
        thread = openai_client.beta.threads.create()
        thread_id = thread.id
        db.insert({"phone_number": phone_number, 'thread_id': thread_id})
        
    message = openai_client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=prompt
    )
    
    run = openai_client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    )
    
    while True:
        run = openai_client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run.id
        )
        
        if run.status == "completed":
            messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            return text
        if run.status == "requires_action":
            tool_call_id = run.required_action.submit_tool_outputs.tool_calls[0]
            function_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
            function_arguments = json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
            function_response = globals()[function_name](function_arguments)
            
            run = openai_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
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
        
            
    
@app.route('/sms', methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body')
    phone_number = request.form.get('From')
    session_id = session.get('session_id', None)
    
    if not session_id:
        session_id = secrets.token_hex(16)
        session['session_id'] = session_id

    logging.debug(f"Incoming message from {phone_number}: {incoming_msg}")

    if incoming_msg:
        answer = get_chatgpt_response(incoming_msg, phone_number)
        sendMessage(answer, phone_number[9:])
    else:
        sendMessage("Message cannot be empty!", phone_number[9:])

    resp = MessagingResponse()
    resp.message("")
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=9000)
    
    
