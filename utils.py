import os, shutil
import logging
import time
import ffmpeg
from random import randrange, randint
from datetime import datetime, timedelta
import requests
import json
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

def generate_background_video():
    log = get_logger()
    required_folders = ['./video-generation/public/video', './background-videos', './background-videos/archive']
    for folder in required_folders:
        check_for_folder_or_create(folder)

    source_vids = [f'./background-videos/{f}' for f in os.listdir('./background-videos') if os.path.isfile(f'./background-videos/{f}')]

    vid_path = './video-generation/public/video/backgroundVideo.mp4'
    if os.path.isfile(vid_path):
        os.remove(vid_path)

    input_file = source_vids[randrange(len(source_vids))]
    # Generate a random start time within the duration of the input video
    duration = ffmpeg.probe(input_file)['format']['duration']
    start_time = randint(5, int(float(duration)) -70)
    log.info(f'Using video {input_file} to create random snippet starting at {start_time} seconds')
    # Extract a 1 minute snippet starting from the randomly generated start time
    (
        ffmpeg
        .input(input_file, ss=start_time)
        .trim(start=0, duration=60)
        .filter('fps', fps=30, round='up')
        .output(vid_path)
        .overwrite_output()
        .run()
    )

def remove_tts_audio_files():
    tts_folder = './video-generation/public/audio'
    for filename in os.listdir(tts_folder):
        file_path = os.path.join(tts_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def remove_file(file_path):
    os.remove(file_path)

def get_video_description_string(author, subreddit, link):
    return f'Follow for more amazing reddit stories!\n\nSubreddit: r/{subreddit}\nPost by: u/{author}\nLink to reddit post: {link}\n\n#shorts #stories #redditstories #beststories'

def check_for_folder_or_create(full_path):
    log = get_logger()
    if not os.path.isdir(full_path):
        log.info(f'Creating folder {full_path}')
        os.mkdir(full_path)

def get_logger():
    global _logger

    if _logger is not None:
        # If logger already has handlers, return existing logger instance
        if _logger.hasHandlers():
            return _logger
        else:
            # If logger doesn't have handlers, add new handlers and return logger instance
            _logger.addHandler(logging.FileHandler(f'./logs/{time.strftime("log_%Y-%m-%d_%H-%M-%S.log")}'))
            _logger.addHandler(logging.StreamHandler())
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

    _logger = logger
    return logger