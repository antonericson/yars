import requests
import json
import os
from datetime import datetime, timedelta
from yars_secrets import *

def get_token():
    if not os.path.isfile("token.json"):
        base_dict = {
        "token": "not_a_valid_token",
        "valid_until": "19990408T163321",
        "fetched": "19990408T163321"
        }
        json_obj = json.dumps(base_dict, indent=4)
        with open("token.json", "w") as outfile:
            outfile.write(json_obj)

    with open('token.json') as json_file:
        token_data = json.load(json_file)
        valid_until = datetime.strptime(token_data['valid_until'], '%Y%m%dT%H%M%S') 

        if valid_until < (datetime.now() + timedelta(hours=1)):

            os.remove('token.json')

            # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
            auth = requests.auth.HTTPBasicAuth(key, secret)

            # here we pass our login method (password), username, and password
            data = {'grant_type': 'password',
                    'username': reddit_user,
                    'password': reddit_pw}
            
            # setup our header info, which gives reddit a brief description of our app
            headers = {'User-Agent': 'TextToSpeechVideos/0.0.1'}

            # send our request for an OAuth token
            res_auth = requests.post('https://www.reddit.com/api/v1/access_token',
                                auth=auth, data=data, headers=headers)

            #convert response to JSON and pull access_token value
            token = res_auth.json()['access_token']

            sec_delta = res_auth.json()['expires_in']

            time = datetime.now()
            valid_until = time + timedelta(seconds=sec_delta)
            dict = {
                "token": token,
                "valid_until": valid_until.strftime("%Y%m%dT%H%M%S"),
                "fetched": time.strftime("%Y%m%dT%H%M%S")
            }
            json_obj = json.dumps(dict, indent=4)

            with open("token.json", "w") as outfile:
                outfile.write(json_obj)
            return dict

        else:
            return token_data
