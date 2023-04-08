import requests
import json
import os
from datetime import datetime, timedelta
from yars_secrets import *


def getToken():

    if not os.path.isfile("Token.json"):
        baseDict = {
        "Token": "NotAValidToken",
        "ValidUntil": "19990408T163321",
        "Fetched": "19990408T163321"
        }
        json_obj = json.dumps(baseDict, indent=4)
        with open("Token.json", "w") as outfile:
            outfile.write(json_obj)

    with open('Token.json') as json_file:
        TokenData = json.load(json_file)
        ValidUntil = datetime.strptime(TokenData['ValidUntil'], '%Y%m%dT%H%M%S') 

        if ValidUntil < (datetime.now() + timedelta(hours=1)):

            os.remove('Token.json')

            # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
            auth = requests.auth.HTTPBasicAuth(Key, Secret)

            # here we pass our login method (password), username, and password
            data = {'grant_type': 'password',
                    'username': RedditUser,
                    'password': RedditPW}
            
            # setup our header info, which gives reddit a brief description of our app
            headers = {'User-Agent': 'TextToSpeechVideos/0.0.1'}

            # send our request for an OAuth token
            resAuth = requests.post('https://www.reddit.com/api/v1/access_token',
                                auth=auth, data=data, headers=headers)

            #convert response to JSON and pull access_token value
            TOKEN = resAuth.json()['access_token']

            secDelta = resAuth.json()['expires_in']

            time = datetime.now()
            validUntil = time + timedelta(seconds=secDelta)
            dict = {
                "Token": TOKEN,
                "ValidUntil": validUntil.strftime("%Y%m%dT%H%M%S"),
                "Fetched": time.strftime("%Y%m%dT%H%M%S")
            }
            json_obj = json.dumps(dict, indent=4)

            with open("Token.json", "w") as outfile:
                outfile.write(json_obj)
            return dict

        else:
            return TokenData


