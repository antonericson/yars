import tts
import subprocess
import json
import reddit_integration
from utils import get_background_video_name, remove_tts_audio_files, get_logger, remove_file
import cv2
from TTS.api import TTS

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

    tts_instance = TTS(model_name="tts_models/en/vctk/vits")
    sentences = []
    if body:
        sentences = get_sentences_from_story(body)
        sentences.insert(0, title)
    else:
        sentences.append(subreddit)
        sentences.append(title)

    video_lengths = tts.generate_tts_for_sentences(tts_instance, sentences)

    if(sum(video_lengths) > 58):
        print("Generated video would become longer than 60 secondss")
        return
    
    try:
        background_video_name = get_background_video_name()
    except Exception:
        log.error("Failed to get background video")
        remove_tts_audio_files()
        return

    background_video_path = f'./video-generation/public/video/{background_video_name}'

    cap = cv2.VideoCapture(background_video_path)
    background_video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    create_react_config(background_video_name, background_video_frame_count, sentences, video_lengths, author, subreddit)

    generate_video_command = 'cd video-generation; npx remotion render RedditStory ../out/video.mp4 --props=../current-config.json'
    subprocess.run(generate_video_command, shell=True)

    remove_file(background_video_path)
    remove_tts_audio_files()

if __name__ == "__main__":
    main()
