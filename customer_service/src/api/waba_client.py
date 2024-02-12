from flask import jsonify, request
from requests import Session

# Assuming environment variables are used for configuration
CLIENT_ID = '7233224293422160'
CLIENT_SECRET = '05f9540bb3b54afac94d2440f4a844e5'

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
