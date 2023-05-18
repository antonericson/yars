import os
import shutil
import logging
import time
from random import randrange, randint
from datetime import datetime, timedelta
import json
import ffmpeg
import requests
# pylint: disable-next=import-error
import yars_secrets

_LOGGER = None

def get_token():
    if not os.path.isfile("token.json"):
        base_dict = {
        "token": "not_a_valid_token",
        "valid_until": "19990408T163321",
        "fetched": "19990408T163321"
        }
        json_obj = json.dumps(base_dict, indent=4)
        with open("token.json", "w", encoding='UTF-8') as outfile:
            outfile.write(json_obj)

    with open('token.json', encoding='UTF-8') as json_file:
        token_data = json.load(json_file)
        valid_until = datetime.strptime(token_data['valid_until'], '%Y%m%dT%H%M%S')

        if valid_until < (datetime.now() + timedelta(hours=1)):
            os.remove('token.json')

            # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
            auth = requests.auth.HTTPBasicAuth(yars_secrets.KEY, yars_secrets.SECRET)

            # here we pass our login method (password), username, and password
            data = {'grant_type': 'password',
                    'username': yars_secrets.REDDIT_USER,
                    'password': yars_secrets.REDDIT_PW}

            # setup our header info, which gives reddit a brief description of our app
            headers = {'User-Agent': 'TextToSpeechVideos/0.0.1'}

            # send our request for an OAuth token
            res_auth = requests.post('https://www.reddit.com/api/v1/access_token',
                                auth=auth, data=data, headers=headers, timeout=30)

            #convert response to JSON and pull access_token value
            token = res_auth.json()['access_token']

            sec_delta = res_auth.json()['expires_in']

            current_time = datetime.now()
            valid_until = current_time + timedelta(seconds=sec_delta)
            token_data = {
                "token": token,
                "valid_until": valid_until.strftime("%Y%m%dT%H%M%S"),
                "fetched": time.strftime("%Y%m%dT%H%M%S")
            }
            json_obj = json.dumps(token_data, indent=4)

            with open("token.json", "w", encoding='UTF-8') as outfile:
                outfile.write(json_obj)
            return token_data

        return token_data

def generate_background_video():
    log = get_logger()
    required_folders = ['./video-generation/public/video', './background-videos', './background-videos/archive']
    for folder in required_folders:
        check_for_folder_or_create(folder)

    source_vids = [f'./background-videos/{f}' for f in os.listdir('./background-videos')\
        if os.path.isfile(f'./background-videos/{f}')]

    vid_path = './video-generation/public/video/backgroundVideo.mp4'
    if os.path.isfile(vid_path):
        os.remove(vid_path)

    input_file = source_vids[randrange(len(source_vids))]
    # Generate a random start time within the duration of the input video
    duration = ffmpeg.probe(input_file)['format']['duration']
    start_time = randint(5, int(float(duration)) -70)
    log.info('Using video %s to create random snippet starting at %s seconds', input_file, start_time)
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
    log = get_logger()
    for filename in os.listdir(tts_folder):
        file_path = os.path.join(tts_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except RuntimeError as error:
            log.error('Failed to delete %s. Reason: %s', file_path, error)

def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

def get_video_description_string(author, subreddit, link):
    return 'Follow for more amazing reddit stories!\n\nSubreddit: ' \
            f'r/{subreddit}\nPost by: u/{author}\n' \
            f'Link to reddit post: {link}\n\n'\
            '#shorts #stories #redditstories #beststories'

def check_for_folder_or_create(full_path):
    log = get_logger()
    if not os.path.isdir(full_path):
        log.info('Creating folder %s', full_path)
        os.mkdir(full_path)

def create_react_config(background_video_frame_count, sentences, video_lengths, author, subreddit):
    config = {
        "backgroundVideoFrameCount": background_video_frame_count,
        "sentences": sentences,
        "videoLengths": video_lengths,
        "totalLength": sum(video_lengths),
        "author": author,
        "subreddit": subreddit
    }
    json_config = json.dumps(config)
    with open('current-config.json', 'w', encoding='UTF-8') as config_file:
        config_file.write(json_config)

def get_logger():
    # pylint: disable-next=global-statement
    global _LOGGER

    if _LOGGER is not None:
        # If logger already has handlers, return existing logger instance
        if _LOGGER.hasHandlers():
            return _LOGGER

        # If logger doesn't have handlers, add new handlers and return logger instance
        _LOGGER.addHandler(logging.FileHandler(f'./logs/{time.strftime("log_%Y-%m-%d_%H-%M-%S.log")}'))
        _LOGGER.addHandler(logging.StreamHandler())
        return _LOGGER

    #Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_file_name = time.strftime('log_%Y-%m-%d_%H-%M-%S.log')

    # Create a file handler that writes log messages to a file
    file_handler = logging.FileHandler(f'./logs/{log_file_name}')
    file_handler.setLevel(logging.INFO)

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

    # Set propagate to False to prevent log messages from being propagated to the root logger
    logger.propagate = False

    _LOGGER = logger
    return logger
