import os
import json
import random
from datetime import datetime
import requests
import utils

USED_POSTS_FILE = './used_posts.json'
LOCAL_POSTS_DIRECTORY = './extracted-posts'

def get_post(allow_over_18=False, post_id=None):
    log = utils.get_logger()
    utils.check_for_folder_or_create(LOCAL_POSTS_DIRECTORY)

    # Post id only set if generating with specific given post id
    # Ignore all logic and only generate from this post id
    if post_id:
        file_name = f'{LOCAL_POSTS_DIRECTORY}/{post_id}.json'
        with open(file_name, encoding='UTF-8') as json_file:
            specific_post = json.load(json_file)
        return specific_post

    # Load used posts list from file
    used_post_objects = get_used_post_objects()

    local_post_files = os.listdir(LOCAL_POSTS_DIRECTORY)
    # Remove all used posts from local post folder
    for local_post_id in [post.split('.')[0] for post in local_post_files]:
        if has_post_been_used(used_post_objects, local_post_id):
            log.info('%s has already been used, deleting', local_post_id)
            utils.remove_file(f'{LOCAL_POSTS_DIRECTORY}/{local_post_id}.json')

    # Check if any local posts are availible
    # If not fetch more and store as json files
    local_post_files = os.listdir(LOCAL_POSTS_DIRECTORY)
    if not local_post_files:
        fetch_new_posts(allow_over_18)

    # Get updated list of local posts
    local_post_files = os.listdir(LOCAL_POSTS_DIRECTORY)
    random.seed()
    random.shuffle(local_post_files)

    post_file_to_use = local_post_files[0]
    add_post_to_used_posts(used_post_objects, post_file_to_use.split('.')[0])

    # Get post data from post-file
    with open(f'{LOCAL_POSTS_DIRECTORY}/{post_file_to_use}', 'r', encoding='UTF-8') as json_file:
        post_data = json.load(json_file)

    return post_data

def has_post_been_used(used_post_objects, post_id):
    for post_object in used_post_objects:
        if post_id == post_object['post_id']:
            return True
    return False

def add_post_to_used_posts(used_post_objects, post_id):
    used_post_objects.append({"post_id": post_id,
                                "extracted": datetime.now().strftime("%Y%m%dT%H%M%S")})

    with open(USED_POSTS_FILE, "w", encoding='UTF-8') as used_posts_file:
        used_posts_file.write(
            json.dumps(used_post_objects, indent=4))

def get_used_post_objects():
    with open(USED_POSTS_FILE, 'r', encoding='UTF-8') as used_posts_file:
        used_post_objects = json.load(used_posts_file)
    return used_post_objects

def fetch_new_posts(allow_over_18=False):
    sub_reddits = ['r/todayilearned',
                   'r/TrueOffMyChest',
                   'r/Showerthoughts',
                   'r/unpopularopinion',
                   'r/LifeProTips',
                   'r/AmItheAsshole',
                   'r/UnethicalLifeProTips',
                   'r/ScienceFacts']
    do_not_filter_url_list = ['r/ScienceFacts',
                              'r/todayilearned']
    token = utils.get_token()
    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'TextToSpeechVideos/0.0.1'}
    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {token['token']}"}}

    for sub in sub_reddits:
        top_url = 'https://oauth.reddit.com/' + sub + '/top/?t=month'

        res = requests.get(top_url, headers=headers, timeout=30)
        all_posts = res.json()['data']['children']

        for post in all_posts:
            post_data = post['data']
            if "url_overridden_by_dest" in post_data and\
                (not post_data['subreddit_name_prefixed'] in do_not_filter_url_list):
                continue
            if 'is_video' in post_data:
                if post_data['is_video']:
                    continue
            if 'over_18' in post_data and not allow_over_18:
                if post_data['over_18']:
                    continue

            json_post = json.dumps(post_data, indent=4)
            file_name = f'{LOCAL_POSTS_DIRECTORY}/{post_data["name"]}.json'
            if not os.path.isfile(file_name):
                with open(file_name, 'w', encoding='UTF-8') as json_file:
                    json_file.write(json_post)
