#!/usr/bin/env python3
import os
import sys
import json
import requests
import wget
from requests_oauthlib import OAuth1Session

consumer_key = ""
consumer_secret = ""
screen_name = ""
count = 0

def read_config():
    global consumer_key
    global consumer_secret
    global screen_name
    global count

    with open('config.json') as json_file:
        data = json.load(json_file)
        if("key" in data["consumer"]):
            consumer_key = data["consumer"]["key"]
        if("secret" in data["consumer"]): 
            consumer_secret = data["consumer"]["secret"]
        if("screen_name" in data["api"]):
            screen_name = data["api"]["screen_name"]
        if("count" in data["api"]):
            count = data["api"]["count"]


def get_oauth():
    #consumer_key = input("Please enter your key: ")  # Add your API key here
    #consumer_secret = input("Please enter your secret: ") 

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = oauth.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    print("Got OAuth token: %s" % resource_owner_key)

    # # Get authorization
    base_authorization_url = 'https://api.twitter.com/oauth/authorize'
    authorization_url = oauth.authorization_url(base_authorization_url)
    print('Please go here and authorize: %s' % authorization_url)
    verifier = input('Paste the PIN here: ')

    # # Get the access token
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    oauth = OAuth1Session(consumer_key,
                        client_secret=consumer_secret,
                        resource_owner_key=resource_owner_key,
                        resource_owner_secret=resource_owner_secret,
                        verifier=verifier)
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens['oauth_token']
    access_token_secret = oauth_tokens['oauth_token_secret']

    # Make the request
    oauth = OAuth1Session(consumer_key,
                        client_secret=consumer_secret,
                        resource_owner_key=access_token,
                        resource_owner_secret=access_token_secret)

    return oauth


# Get Twitter Favorites
def get_favorites_list(oauth):

    screen_name = input("Enter a screen name to search for: ")
    count = input("Enter the number of records to retrieve: ")

    params = {"screen_name": screen_name, "count": count }

    response = oauth.get("https://api.twitter.com/1.1/favorites/list.json", params = params)
    print("Response status: %s" % response.status_code)
    print("Body: %s" % response.text)

    return response


def get_user_timeline(oauth):

    #screen_name = input("Enter a screen name to search for: ")
    #count = input("Enter the number of records to retrieve: ")

    params = {"screen_name": screen_name, "count": count }

    response = oauth.get("https://api.twitter.com/1.1/statuses/user_timeline.json", params = params)
    print("Response status: %s" % response.status_code)
    print("Body: %s" % response.text)

    return response


def get_first(response):
    result = json.loads(response.content)
    first = result[1]
    serialized = json.dumps(first)
    print("First: %s" % serialized)
    return first


def get_entities(tweet):

    entities = tweet["entities"]
    serialized = json.dumps(entities)
    print("Entities: %s" % serialized)



def get_media(response):
    tweets = json.loads(response)
    media_files = set()
    for status in tweets:
        if("media" in status["entities"]):
            media = status["entities"].get('media', [])
            if(len(media) > 0):
                media_files.add(media[0]['media_url'])
                print("Media: %s" % media[0]['media_url'])

    return media_files
    
def download_media(media_files):
    for media_file in media_files:
        wget.download(media_file)



def get_user_timeline_media(oauth):
    user_timeline = get_user_timeline(oauth)
    get_media(user_timeline.content)
    #download_media(media_files)


def main():
    #read configuration settings
    read_config()

    #Get the oauth tokens
    oauth = get_oauth()

    get_user_timeline_media(oauth)

if __name__ == "__main__":
    main()




