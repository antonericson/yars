import tts
import subprocess
import json
import reddit_integration
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
            else:
                sentences.append(word)
    return sentences

def create_react_config(background_video_name, sentences, video_lengths):
  config = {
    "backgroundVideoName": background_video_name,
    "sentences": sentences,
    "videoLengths": video_lengths,
    "totalLength": sum(video_lengths)
  }
  json_config = json.dumps(config)
  with open(f'current-config.json', 'w') as config_file:
    config_file.write(json_config)

def main():

    post = reddit_integration.get_post()
    #test_story = "So my parents bought a house almost 3 years ago for me and my wife and kids to rent from them. They originally told us it would take a few months to a year to get ready so we agreed, they bought the house then asked us if we wanted to rent. We'll its been almost 3 years now and they still refuse to let my wifes side of the family help and now, me and my wife have the option to buy a home and we decided that that's what we wanted instead of renting. When we informed then of our decision they were not happy about it. It's been a month and they have still not responded to any of our messages or calls. We've tried reaching out to them and inviting them to our kids games and graduation but they have yet to even read the messages but we see them messaging in the family group chat about other family members events. So am I the asshole for deciding to buy a house instead of renting the one they bought?"
    #test_story = "I'm a pleaser. Mainly because I want to help out and want people to like me. I'm also a person who is overloaded with ideas, gets very enthusiastic over these and have the urge to share. So when someone comes to me for help or advice, whether personal or work related, I come up with solutions that usually work out pretty well when executed.\n\nProblem is that I always have the feeling that I don't get enough credit for it. I feel like I really helped someone about but don't feel loved because of it. I often feel like people use me and take all the credit for themselves. \n\nHow do I stop pleasing?"
    all_stories = [post['selftext']]

    tts_instance = TTS(model_name="tts_models/en/vctk/vits")
    for story in all_stories:
        sentences = get_sentences_from_story(story)
        video_lengths = tts.generate_tts_for_sentences(tts_instance, sentences)

    create_react_config("gameplay_video.mp4", sentences, video_lengths)

    generate_video_command = 'cd video-generation; npx remotion render RedditStory ../out/video.mp4 --props=../current-config.json'
    subprocess.run(generate_video_command, shell=True)

if __name__ == "__main__":
    main()
