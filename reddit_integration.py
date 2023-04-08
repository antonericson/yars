import requests
import os
import json
import random
from datetime import datetime
import token_handler

LOCAL_REGISTRY_FILE = './used_posts.json'

#Ca 60 sekunder för short. blir under 900 tecken.
def get_post():

    if  not os.path.isdir('./extracted-posts'):
        os.mkdir('extracted-posts')

    postId = get_local_reddit_post_id()

    if postId:
        fileName = './extracted-posts/' + postId + '.json'
        with open(fileName) as json_file:
            postData = json.load(json_file)
    else:
        postData = None
    return postData
        

def get_local_available_posts():
    available_posts = [os.path.splitext(i)[0] for i in os.listdir('./extracted-posts/')]
    random.shuffle(available_posts)

    return available_posts

def get_local_reddit_post_id():

    if not os.path.isfile(LOCAL_REGISTRY_FILE):
        used_files_dict = []
    else: 
        with open(LOCAL_REGISTRY_FILE) as used_posts_file:
            used_files_dict = json.load(used_posts_file)
        
    available_posts = get_local_available_posts()
    if not available_posts:
        if get_reddit_posts_from_remote():
            available_posts = get_local_available_posts()
        else:
            return None

    if not used_files_dict:
        #Empty
        used_files_dict.append({"post_id": available_posts[0],
                              "extracted": datetime.now().strftime("%Y%m%dT%H%M%S")})
        with open(LOCAL_REGISTRY_FILE, "w") as used_posts_file:
            used_posts_file.write(json.dumps(used_files_dict, indent=4))
        return available_posts[0]
    else:
        for post in available_posts:
            post_has_been_used = False
            for used_posts in used_files_dict:
                if post == used_posts['post_id']:
                    post_has_been_used = True
                    break
            
            if not post_has_been_used:
                used_files_dict.append({"post_id": post,
                        "extracted": datetime.now().strftime("%Y%m%dT%H%M%S")})
                with open(LOCAL_REGISTRY_FILE, "w") as used_posts_file:
                    used_posts_file.write(json.dumps(used_files_dict, indent=4))
                return post
        
        #If scripts comes here and there's no post available to return then grab more posts
        
        if get_reddit_posts_from_remote():
            return get_local_reddit_post_id()
        else:
            return None
    
def get_reddit_posts_from_remote():
    has_downloaded_post = False
    sub_reddits = [  'r/todayilearned',
                    'r/TrueOffMyChest',
                    'r/IWantToLearn',
                    'r/Futurology',
                    'r/Showerthoughts',
                    'r/unpopularopinion',
                    'r/LifeProTips']
    
    token = token_handler.get_token()
    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'TextToSpeechVideos/0.0.1'}
    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {token['token']}"}}

    for sub in sub_reddits:
        top_url = 'https://oauth.reddit.com/' + sub + '/top/?t=month'

        res = requests.get(top_url, headers=headers)
        all_posts = res.json()['data']['children']

        for post in all_posts:
            if "url_overridden_by_dest" in post['data']: #Post has url
                continue
            if post['data']['is_video']:
                continue
            if post['data']['over_18']:
                continue

            json_post = json.dumps(post['data'], indent=4)
            file_name = './extracted-posts/' + post['data']['name'] + '.json'
            if not os.path.isfile(file_name):
                with open(file_name, 'w') as json_file:
                    has_downloaded_post = True
                    json_file.write(json_post)

    return has_downloaded_post
