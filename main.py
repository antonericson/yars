import tts
import subprocess
import json
import reddit_integration
from utils import *
import cv2
import os
from TTS.api import TTS


def get_sentences_from_story_2(Title, Text):
    maxLen = 120
    Title = Title.strip()
    Text = Text.strip()
    parenthesis = ['(', ')']
    endMarks = ['.', '!', '?']
    if not Title == '':
        if not Title[-1] in endMarks:
            Title = Title + '.'
    if not Text == '':
        if not Text[-1] in endMarks:
            Text = Text + '.'

    allText = (Title + ' ' + Text).strip()
    paragraphs = []
    textBuffer = allText
    loop_cond = True
    while loop_cond:
        lastComma = None
        lastStop = None
        lastSpace = None
        lastParenthesis = None
        if len(textBuffer) == 0:
            break

        for id, char in enumerate(textBuffer):
            if(char in parenthesis):
                lastParenthesis = id
            if(char in endMarks):
                lastStop = id
            if(char == ','):
                lastComma = id
            if(char == ' '):
                lastSpace = id
            if id == (len(textBuffer)-1):
                #Stop of buffer
                paragraphs.append(textBuffer)
                loop_cond = False
                break
            if id>=(maxLen-1):
                ##Reached sentence length
                appendTo = None
                
                if lastStop:
                    appendTo = lastStop
                    debugTxt = "fullStop"
                elif lastParenthesis:
                    if textBuffer[lastParenthesis] == '(':
                        #Don't include this parenthesis
                        appendTo = max(lastParenthesis - 1, 0)
                    else:
                        #Include closing parenthesis
                        appendTo = lastParenthesis
                    debugTxt = "Parenthesis"
                elif lastComma:
                    appendTo = lastComma
                    debugTxt = "comma"
                elif lastSpace:
                    appendTo = lastSpace
                    debugTxt = "Space"
                else:
                    loop_cond = False
                    break

                #print("adding {} sentence  {}#".format(debugTxt, textBuffer[:appendTo+1]))
                paragraphs.append(textBuffer[:appendTo+1])
                textBuffer = textBuffer[appendTo+1:]
                break

    paragraphs = [x.strip() for x in paragraphs]
    lens = [len(x) for x in paragraphs]
    return paragraphs



def get_sentences_from_story(full_story):
    sentences = []
    for sentence in full_story.split(". "):
        sentence.strip()
        sentence += '.'
        for word in sentence.split(", "):
            if len(word.split(" ")) > 20:
                letters = word.split(" ")
                sentences.append(' '.join(letters[:len(letters)//2]))
                sentences.append(' '.join(letters[len(letters)//2:]))
            else:
                sentences.append(word)
    return sentences

def create_react_config(background_video_name, background_video_frame_count, sentences, video_lengths, author, subreddit):
  config = {
    "backgroundVideoName": background_video_name,
    "backgroundVideoFrameCount": background_video_frame_count,
    "sentences": sentences,
    "videoLengths": video_lengths,
    "totalLength": sum(video_lengths),
    "author": author,
    "subreddit": subreddit
  }
  json_config = json.dumps(config)
  with open(f'current-config.json', 'w') as config_file:
    config_file.write(json_config)

def main():
    log = get_logger()
    post = reddit_integration.get_post()
    title = post['title']
    body = post['selftext']
    author = post['author']
    subreddit = post['subreddit']
    post_id = post['name']
    link_to_post = f'https://www.reddit.com{post["permalink"]}'

    tts_instance = TTS(model_name="tts_models/en/vctk/vits")
    sentences = []
    if body:
        sentences = get_sentences_from_story_2(title, body)
    else:
        sentences = get_sentences_from_story_2(subreddit, title)

    video_lengths = tts.generate_tts_for_sentences(tts_instance, sentences)

    if(sum(video_lengths) > 58):
        print("Generated video would become longer than 60 secondss")
        remove_tts_audio_files()
        return
    
    try:
        background_video_name = get_background_video_name()
    except Exception as e:
        log.error(f'Failed to get background video. Exception {e}')
        remove_tts_audio_files()
        return

    background_video_path = f'./video-generation/public/video/{background_video_name}'

    cap = cv2.VideoCapture(background_video_path)
    background_video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    create_react_config(background_video_name, background_video_frame_count, sentences, video_lengths, author, subreddit)

    folder_name = f'{subreddit}_{post_id}'
    if not os.path.isdir(f'./out/{folder_name}'):
        log.info(f"Creating video folder ./out/{folder_name}")
        os.mkdir(f'./out/{folder_name}')
        
    with open(f'./out/{folder_name}/{post_id}_desc.txt', 'w') as description_file:
        log.info('Writing description file...')
        description_file.write(get_video_description_string(author, subreddit, link_to_post))

    generate_video_command = f'cd video-generation; npx remotion render RedditStory ../out/{subreddit}_{post_id}/AmazingRedditStory.mp4 --props=../current-config.json'
    subprocess.run(generate_video_command, shell=True)

    remove_file(background_video_path)
    remove_tts_audio_files()

if __name__ == "__main__":
    main()
