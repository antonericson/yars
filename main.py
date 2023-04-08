import tts
import subprocess
import json
import reddit_integration
from utils import get_background_video_name
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

def create_react_config(background_video_name, sentences, video_lengths, author, subreddit):
  config = {
    "backgroundVideoName": background_video_name,
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

    video_lengths = tts.generate_tts_for_sentences(tts_instance, sentences)

    if(sum(video_lengths) > 58):
        print("Generated video would become longer than 60 seconds")
        return

    create_react_config(get_background_video_name(), sentences, video_lengths, author, subreddit)

    generate_video_command = 'cd video-generation; npx remotion render RedditStory ../out/video.mp4 --props=../current-config.json'
    subprocess.run(generate_video_command, shell=True)

if __name__ == "__main__":
    main()
