import requests
import os
import json
import random
from datetime import datetime
from YARSSecrets import *
from RefreshToken import *

LOCAL_REGISTRY_FILE = './usedPosts.json'

#Ca 60 sekunder för short. blir under 900 tecken.


def getPost():

    if  not os.path.isdir('./ExtractedPosts'):
        os.mkdir('ExtractedPosts')

    postId = getLocalRedditPostId()

    if postId:
        fileName = './ExtractedPosts/' + postId + '.json'
        with open(fileName) as json_file:
            postData = json.load(json_file)
    else:
        postData = None
    return postData
        

def getLocalAvailablePosts():
    availablePosts = [os.path.splitext(i)[0] for i in os.listdir('./ExtractedPosts/')]
    random.shuffle(availablePosts)

    return availablePosts

def getLocalRedditPostId():

    if not os.path.isfile(LOCAL_REGISTRY_FILE):
        usedFilesDict = []
    else: 
        with open(LOCAL_REGISTRY_FILE) as used_posts_file:
            usedFilesDict = json.load(used_posts_file)
        
    availablePosts = getLocalAvailablePosts()
    if not availablePosts:
        if getRedditPostsFromRemote():
            availablePosts = getLocalAvailablePosts()
        else:
            return None

    if not usedFilesDict:
        #Empty
        usedFilesDict.append({"PostId": availablePosts[0],
                              "Extracted": datetime.now().strftime("%Y%m%dT%H%M%S")})
        with open(LOCAL_REGISTRY_FILE, "w") as used_posts_file:
            used_posts_file.write(json.dumps(usedFilesDict, indent=4))
        return availablePosts[0]
    else:
        for post in availablePosts:
            post_has_been_used = False
            for usedPosts in usedFilesDict:
                if post == usedPosts['PostId']:
                    post_has_been_used = True
                    break
            
            if not post_has_been_used:
                usedFilesDict.append({"PostId": post,
                        "Extracted": datetime.now().strftime("%Y%m%dT%H%M%S")})
                with open(LOCAL_REGISTRY_FILE, "w") as used_posts_file:
                    used_posts_file.write(json.dumps(usedFilesDict, indent=4))
                return post
        
        #If scripts comes here and there's no post available to return then grab more posts
        
        if getRedditPostsFromRemote():
            return getLocalRedditPostId()
        else:
            return None
    
    


def getRedditPostsFromRemote():
    has_downloaded_post = False
    SubReddits = [  'r/todayilearned',
                    'r/TrueOffMyChest',
                    'r/IWantToLearn',
                    'r/Futurology',
                    'r/Showerthoughts',
                    'r/unpopularopinion',
                    'r/LifeProTips']
    
    Token = getToken()
    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'TextToSpeechVideos/0.0.1'}
    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {Token['Token']}"}}

    for sub in SubReddits:

        TopUrl = 'https://oauth.reddit.com/' + sub + '/top/?t=month'

        res = requests.get(TopUrl,
                        headers=headers)
        allPosts = res.json()['data']['children']

        for post in allPosts:
            if "url_overridden_by_dest" in post['data']: #Post has url
                continue
            if post['data']['is_video']:
                continue
            if post['data']['over_18']:
                continue

            json_post = json.dumps(post['data'], indent=4)
            fileName = './ExtractedPosts/' + post['data']['name'] + '.json'
            if not os.path.isfile(fileName):
                with open(fileName, 'w') as json_file:
                    has_downloaded_post = True
                    json_file.write(json_post)

    return has_downloaded_post
