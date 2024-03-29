#!/usr/bin/env python3
import os
import sys
import json
import requests
import wget
import webbrowser
from requests_oauthlib import OAuth1Session

consumer_key = ""
consumer_secret = ""
screen_name = ""
count = 0
oauth = {}

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
    global oauth
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
def get_favorites_list():

    screen_name = input("Enter a screen name to search for: ")
    count = input("Enter the number of records to retrieve: ")

    params = {"screen_name": screen_name, "count": count }

    response = oauth.get("https://api.twitter.com/1.1/favorites/list.json", params = params)
    print("Response status: %s" % response.status_code)
    print("Body: %s" % response.text)

    return response


def get_user_timeline():

    #screen_name = input("Enter a screen name to search for: ")
    #count = input("Enter the number of records to retrieve: ")

    params = {"screen_name": screen_name, "count": count }

    response = oauth.get("https://api.twitter.com/1.1/statuses/user_timeline.json", params = params)
    #print("Response status: %s" % response.status_code)
    #print("Body: %s" % response.text)

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


def get_hashtag_media(response):
    tweets = json.loads(response)
    media_files = set()
    for status in tweets["statuses"]:
        #print("Status: %s" % status)
        if("media" in status["entities"]):
            media = status["entities"].get('media', [])
            if(len(media) > 0):
                media_files.add(media[0]['media_url'])
                print("Media: %s" % media[0]['media_url'])
         

    return media_files
    
def download_media(media_files):
    for media_file in media_files:
        wget.download(media_file)



def get_user_timeline_media():
    user_timeline = get_user_timeline()
    get_media(user_timeline.content)
    #download_media(media_files)


def search_by_hashtag(q, n):
    params = {"q": q, "count": n}

    response = oauth.get("https://api.twitter.com/1.1/search/tweets.json", params = params)
    #print("Response status: %s" % response.status_code)
    #print("Body: %s" % response.text)

    return response

def data_to_html_table(data):
    html = '<table><tbody>'
    for item in data:
        html += '<tr><td>' + str(item) + '</td></tr>'
    html += '</tbody></table>'
    return html

def media_to_html_img(data):
    html = '<img src='"'" + str(data) + "'"" width='100%'/>"
    print("%s" % html)
    return html

def media_to_html_table(data):
    html = '<table id=\"twitter-api\"><tbody>'
    for item in data:
        html += '<tr><td>' + str(media_to_html_img(item)) + '</td></tr>'
    html += '</tbody></table>'
    print("%s" % html)
    return html

def write_file(filename, mode, data):
    f = open(filename, "w")
    f.write(data)
    f.close()

def read_file(filename, mode):
    with open(filename, mode) as myfile:
        data = myfile.read()
        return data

def open_html_file(filename):
    #new = 2 # open in a new tab, if possible

    #open a public URL, in this case, the webbrowser docs
    #url = "http://docs.python.org/library/webbrowser.html"
    #webbrowser.open(url,new=new)

    # open an HTML file on my own (Windows) computer
    #Change path to reflect file location
    web_file = 'file:///'+os.getcwd()+'/' + filename
    webbrowser.open_new_tab(web_file)


def main():
    #read configuration settings
    read_config()

    #Get the oauth tokens
    get_oauth()

    
    response = search_by_hashtag("#GodOfWar #PS4Share", 20)
    media = get_hashtag_media(response.content)

    html = media_to_html_table(media)

    #Get base index.html
    base_contents = read_file("base.html", "r")

    new_html = base_contents.replace("<table id=\"twitter-api\"></table>", html)

    filename = "index.html"
    write_file(filename, "w", new_html)

    open_html_file(filename)

if __name__ == "__main__":
    main()




