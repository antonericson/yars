import tts
import subprocess
import json
from TTS.api import TTS

def getSentencesFromStory(full_story):
    sentences = []
    for sentence in full_story.split(". "):
        for word in sentence.split(", "):
            if len(word.split(" ")) > 20:
                letters = word.split(" ")
                sentences.append(' '.join(letters[:len(letters)//2]))
                sentences.append(' '.join(letters[len(letters)//2:]))
            else:
                sentences.append(word)
    return sentences

def create_react_config(backgroundVideoName, sentences, videoLengths):
  config = {
    "backgroundVideoName": backgroundVideoName,
    "sentences": sentences,
    "videoLengths": videoLengths,
    "totalLength": sum(videoLengths)
  }
  json_config = json.dumps(config)
  with open(f'current-config.json', 'w') as config_file:
    config_file.write(json_config)

def main():

    #all_text = "So my parents bought a house almost 3 years ago for me and my wife and kids to rent from them. They originally told us it would take a few months to a year to get ready so we agreed, they bought the house then asked us if we wanted to rent. We'll its been almost 3 years now and they still refuse to let my wifes side of the family help and now, me and my wife have the option to buy a home and we decided that that's what we wanted instead of renting. When we informed then of our decision they were not happy about it. It's been a month and they have still not responded to any of our messages or calls. We've tried reaching out to them and inviting them to our kids games and graduation but they have yet to even read the messages but we see them messaging in the family group chat about other family members events. So am I the asshole for deciding to buy a house instead of renting the one they bought?"
    test_story = "So my parents bought a house almost 3 years ago for me and my wife and kids to rent from them."
    all_stories = [test_story]

    tts_instance = TTS(model_name="tts_models/en/vctk/vits")
    for story in all_stories:
        sentences = getSentencesFromStory(story)
        video_lengths = tts.generateTTSForSentences(tts_instance, sentences)

    create_react_config("gameplay_video.mp4", sentences, video_lengths)

    generate_video_command = 'cd video-generation; npx remotion render RedditStory ../out/video.mp4 --props=../current-config.json'
    subprocess.run(generate_video_command, shell=True)

if __name__ == "__main__":
    main()
