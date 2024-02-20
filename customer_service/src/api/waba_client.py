from flask import jsonify, request
import io
import requests
from requests import Session

# Assuming environment variables are used for configuration
CLIENT_ID = '7233224293422160'
CLIENT_SECRET = '05f9540bb3b54afac94d2440f4a844e5'
VERIFY_TOKEN = 'verify'

def get_facebook_access_token(session, code=None):
    url = 'https://graph.facebook.com/v19.0/oauth/access_token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    if code:  # If code is provided, it's for getting the user access token
        params['code'] = code
        params['grant_type'] = 'authorization_code'

    response = session.get(url, params=params)
    response.raise_for_status()  # Raises HTTPError for bad responses
    return response.json()['access_token']

def get_waba_details(session, access_token, user_access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'input_token': user_access_token}
    response = session.get('https://graph.facebook.com/v19.0/debug_token', params=params, headers=headers)
    response.raise_for_status()
    waba_id = response.json()['data']['granular_scopes'][0]['target_ids'][0]
    
    params = {'access_token': user_access_token}
    response = session.get(f'https://graph.facebook.com/v19.0/{waba_id}/phone_numbers', params=params)
    response.raise_for_status()
    phone_data = response.json()['data'][0]
    return phone_data['display_phone_number'], phone_data['id'], waba_id

def add_system_user(session, waba_id):
    url = f'https://graph.facebook.com/v19.0/{waba_id}/assigned_users'
    params = {
        'user': '122101535918215802',
        'tasks': "['MANAGE']",
        'access_token': 'EABmylESXFFABO97rZAt3x81n0XFtIfUJZAuZAy3iFdCW8fYSkYjRq1pSelwGdZB16bVZCVShRpqORGRl0n0cn32evcQQCn3lincGuF5tFNG8ZBm9EO7gtkB0fTXGDIBR51owolKgAwq71mXYsrTXWK5KS777bAQ9XcfZCE1Kw7CAdP1ESXknvuQANgr5JZBNnpOo' #TODO: Make this a system variable
    }
    
    response = session.post(url, json=params)
    response.raise_for_status()
    return response.json()['success']

def register_waba(session, access_token, waba_id, pin):
    url = f'https://graph.facebook.com/v19.0/{waba_id}/register'
    params = {
        'messaging_product': 'whatsapp',
        'pin': pin,
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = session.post(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()['success']
    
    

def handle_whatsapp_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    value = body["entry"][0]["changes"][0]["value"]
    phone_number = value["metadata"]["display_phone_number"]
    from_number = value["messages"][0]["from"]
    if message["type"] == "text":
        message_body = message["text"]["body"]
    # elif message["type"] == "audio": TODO: Implement token for the waba audio
    #     audio_id = message["audio"]["id"]
    #     message_body = handle_audio_message(audio_id)
    
    return message_body, phone_number, from_number


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



def verify(request):
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400