import json
import os
from functools import wraps

import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials as SAC
from slacker import Slacker


def memoize(f):
    cache = {}
    
    @wraps(f)
    def helper(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    
    return helper


@memoize
def get_config():
    path = os.path.expanduser('~/.funachan/config.json')
    with open(os.path.abspath(path), 'r') as f:
        config = json.load(f)
    
    return config


@memoize
def get_google_client():
    scope = ['https://www.googleapis.com/auth/calendar']
    path = os.path.expanduser('~/.funachan/google_secret.json')
    
    credentials = SAC.from_json_keyfile_name(path, scope)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    return service


@memoize
def get_slack_client():
    token = get_config()['slack_token']
    return Slacker(token)


@memoize
def get_slack_users():
    path = os.path.expanduser('~/.funachan/slack_users.json')
    with open(path, 'r') as f:
        users = json.load(f)
    
    return users


@memoize
def get_channel_id(name):
    slack = get_slack_client()
    
    response = slack.channels.list()
    channels = response.body.get('channels')
    for c in channels:
        if c['name'] == name.strip('#'):
            return c['id']
