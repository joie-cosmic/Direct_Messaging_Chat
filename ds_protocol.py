# a5.py
#
# ICS 32
# Assignment 5: Direct Messaging Chat
# Author: Joy Zhou
# Email: yunxinz6@uci.edu
# ID number: 32927020
# Description: GUI for direct messaging application
import json
import time
from collections import namedtuple

DataTuple = namedtuple('DataTuple', ['type', 'message', 'token'])


def extract_json(json_msg: str) -> DataTuple:
    '''
    Call the json.loads function on a json string and convert it
    to a DataTuple object
    '''
    try:
        json_obj = json.loads(json_msg)
        resp_type = json_obj['response']['type']
        message = json_obj['response'].get('message', '')
        token = json_obj['response'].get('token', '')
    except json.JSONDecodeError:
        print("Json cannot be decoded.")
        return DataTuple('error', 'JSON decode failed', '')
    except KeyError:
        print("Unexpected response format.")
        return DataTuple('error', 'Bad response format', '')

    return DataTuple(resp_type, message, token)


def join_msg(username: str, password: str) -> str:
    '''Pack join command into JSON string'''
    msg = {
        "join": {
            "username": username,
            "password": password,
            "token": ""
        }
    }
    return json.dumps(msg)


def post_msg(token: str, entry: str, timestamp: str) -> str:
    '''Pack post command into JSON string'''
    msg = {
        "token": token,
        "post": {
            "entry": entry,
            "timestamp": timestamp
        }
    }
    return json.dumps(msg)


def bio_msg(token: str, entry: str, timestamp: str) -> str:
    '''Pack bio command into JSON string'''
    msg = {
        "token": token,
        "bio": {
            "entry": entry,
            "timestamp": timestamp
        }
    }
    return json.dumps(msg)


def send_directmessage(token: str, message: str, recipient: str) -> str:
    '''Pack direct message command into JSON string'''
    msg = {
        "token": token,
        "directmessage": {
            "entry": message,
            "recipient": recipient,
            "timestamp": str(time.time())
        }
    }
    return json.dumps(msg)


def request_new_messages(token: str) -> str:
    '''Pack request for new messages into JSON string'''
    msg = {
        "token": token,
        "directmessage": "new"
    }
    return json.dumps(msg)


def request_all_messages(token: str) -> str:
    '''Pack request for all messages into JSON string'''
    msg = {
        "token": token,
        "directmessage": "all"
    }
    return json.dumps(msg)


def parse_response(json_msg: str) -> dict:
    '''
    Parse server response JSON string into a dictionary.
    Returns the response dict, or empty dict if parsing fails.
    '''
    try:
        json_obj = json.loads(json_msg)
        return json_obj.get('response', {})
    except json.JSONDecodeError:
        print("Json cannot be decoded.")
        return {}


def extract_messages(json_msg: str) -> list:
    '''
    Extract list of messages from server response.
    Returns list of dicts with keys: message, from, timestamp
    '''
    try:
        json_obj = json.loads(json_msg)
        response = json_obj.get('response', {})
        if response.get('type') == 'ok':
            return response.get('messages', [])
        return []
    except json.JSONDecodeError:
        print("Json cannot be decoded.")
        return []
