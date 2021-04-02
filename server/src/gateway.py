from flask_sqlalchemy import SQLAlchemy
import requests, os
import json, time, hashlib
from datetime import datetime, timedelta
from urllib.parse import urlencode

def validate_PF_API_token(headers):
    pf_token = headers.get('X-POWER-FORWARD-TOKEN')
    ## Search neon_token in database of accepted tokens
    if pf_token == None:
        return False, "Invalid Power Forward Token."
    else:
        return pf_token=='SweetToken', "Token received"

def send_to_discord(payload):
    '''
    Function to send a message to discord.
    Payloads should be a dictionary where
    `username` and `content` must be defined.
    '''
    ## relay message to discord channel via webook
    url = os.environ.get('DISCORD_WEBHOOK')
    if url:
        print('FOUND WEWBHOOK')
        print(url)

    response = requests.post(url, json=payload, params={'wait': True})
    return response.status_code

def analytics(req):
    '''
    Analytics collector that gets sent directly to our discord channel.
    '''
    ## get around mulitple proxies
    if req.headers.getlist("X-Forwarded-For"):
       ip = req.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = req.remote_addr
    ip_address = ip
    url = req.url
    device = req.headers.get('User-Agent')
    current_time = datetime.now()
    content_dict = {    "Visit Time":  current_time,
                        "Requester IP": ip_address,
                        "URL Visited": url,
                        "User Agent": device }
    content_str = "GOT A VISITOR!"
    for k, v in content_dict.items():
        content_str = content_str + "\n  > {k}: {v}".format(k=k, v=v)

    payload = {
        'username': "Power Forward App Analytics :)",
        'content': content_str
    }
    return send_to_discord(payload)