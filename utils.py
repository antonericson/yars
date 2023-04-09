import requests
import json
import os, shutil
import logging
import time
import ffmpeg
from datetime import datetime, timedelta
from random import randrange
from yars_secrets import *

_logger = None

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

def get_background_video_name():
    log = get_logger()

    if not os.path.isdir('./video-generation/public/video'):
        log.info("No public/video folder, creating...")
        os.mkdir('./video-generation/public/video')
    
    if not os.path.isdir('./background-videos'):
        log.info("No background-videos folder, creating...")
        os.mkdir('./background-videos')
    
    if not os.path.isdir('./background-videos/archive'):
        log.info("No archive folder, creating...")
        os.mkdir('./background-videos/archive')

    all_videos = os.listdir('./video-generation/public/video')
    if len(all_videos) == 0:
        log.info('No pre-cut videos available. Looking for source videos.')

        source_videos = [f for f in os.listdir('./background-videos') if os.path.isfile(f'./background-videos/{f}')]

        if len(source_videos) == 0:
            log.info('No source videos found in background-videos, exiting')
            raise Exception()
        video_to_slice = source_videos[0]
        [name, filetype] = video_to_slice.split('.')
        log.info(f'Slicing {video_to_slice}...')
        ffmpeg.input(f'background-videos/{video_to_slice}').output(f'./video-generation/public/video/{name}%03d.mp4', c="copy", map="0", segment_time='00:01:00', f="segment", reset_timestamps=1).run()
        all_videos = os.listdir('./video-generation/public/video')
        log.info(f'Moving {video_to_slice} to archive...')
        os.rename(f'./background-videos/{video_to_slice}', f'./background-videos/archive/{video_to_slice}')
    
    return all_videos[randrange(len(all_videos))]

def remove_tts_audio_files():
    folder = './video-generation/public/audio'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def remove_file(file_path):
    os.remove(file_path)

def get_logger():
    global _logger

    if _logger is not None:
        return _logger
    
    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_file_name = time.strftime('log_%Y-%m-%d_%H-%M-%S.log')

    # Create a file handler that writes log messages to a file
    file_handler = logging.FileHandler(f'./logs/{log_file_name}')
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler that writes log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Define the log message format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the file and console handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger