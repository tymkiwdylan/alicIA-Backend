from flask import jsonify, request
import io
import requests
from requests.auth import HTTPBasicAuth
from .models import Agent, Conversation, Message
from . import client, openai_client, functions, db

def get_media_url(media_id, whatsapp_token):
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }
    url = f"https://graph.facebook.com/v16.0/{media_id}/"
    response = requests.get(url, headers=headers)
    print(f"media id response: {response.json()}")
    return response.json()["url"]


# download the media file from the media url
def download_media_file(media_url, whatsapp_token):
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
    }
    response = requests.get(media_url, headers=headers)
    print(f"first 10 digits of the media file: {response.content[:10]}")
    return response.content


# # convert ogg audio bytes to audio data which speechrecognition library can process
# def convert_audio_bytes(audio_bytes):
#     ogg_audio = pydub.AudioSegment.from_ogg(io.BytesIO(audio_bytes))
#     ogg_audio = ogg_audio.set_sample_width(4)
#     wav_bytes = ogg_audio.export(format="wav").read()
#     audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="int32")
#     sample_width = audio_data.dtype.itemsize
#     print(f"audio sample_rate:{sample_rate}, sample_width:{sample_width}")
#     audio = sr.AudioData(audio_data, sample_rate, sample_width)
#     return audio


# # run speech recognition on the audio data
# def recognize_audio(audio_bytes):
#     recognizer = sr.Recognizer()
#     audio_text = recognizer.recognize_google(audio_bytes, language='es-US')
#     return audio_text


# # handle audio messages
# def handle_audio_message(audio_id):
#     audio_url = get_media_url(audio_id)
#     audio_bytes = download_media_file(audio_url)
#     audio_data = convert_audio_bytes(audio_bytes)
#     audio_text = recognize_audio(audio_data)
#     message = (
#         "Please summarize the following message in its original language "
#         f"as a list of bullet-points: {audio_text}"
#     )
#     return message

def create_subaccount(friendly_name, user_id):
    
    try:
        account = client.api.v2010.accounts.create(friendly_name=friendly_name)
        
        print("ACCOUNT SID", account)
        
        agent = Agent.query.filter_by(user_id=user_id).first()
        
        agent.twilio_sid = account.sid
        agent.twilio_auth_token = account.auth_token
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False
    

def create_waba_sender(waba_id):
    agent = Agent.query.filter_by(waba_id=waba_id).first()
     
    url = "https://messaging.twilio.com/v2/Channels/Senders"
    
    headers = {
    "Content-Type": "application/json",
    }
    print(agent.business_phone_number)
    payload = {
    "sender_id": "whatsapp:"+agent.business_phone_number,
    "configuration": {
        "waba_id": waba_id,
        },
    "webhook": {
        "callback_url": "https://api.nortedev.net/customer-agent/sms",
        "callback_method": "POST",
        }
    }
    
    print(agent.twilio_sid, agent.twilio_auth_token)
    
    auth = HTTPBasicAuth(agent.twilio_sid, agent.twilio_auth_token)
    
    response = requests.post(url, auth=auth, json=payload, headers=headers)
    
    print("TWILIO RESPONSE:", response.text)
    
    if response.status_code != 200:
        return False
    
    return True
    
    