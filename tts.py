import contextlib
import wave
from TTS.api import TTS


def generateTTSForStory(tts, full_story):
  test_text_list = []

  for sentence in full_story.split(". "):
    for word in sentence.split(", "):
      if len(word.split(" ")) > 20:
        letters = word.split(" ")
        test_text_list.append(' '.join(letters[:len(letters)//2]))
        test_text_list.append(' '.join(letters[len(letters)//2:]))
      else:
        test_text_list.append(word)

  video_lengths = []
  tts = TTS(model_name="tts_models/en/vctk/vits")
  for i, sentence in enumerate(test_text_list):
    path_for_react = f'audio/{i}.wav'
    full_path = f'video-generation/public/{path_for_react}'
    tts.tts_to_file(text=sentence, speaker="p273", file_path=full_path)
    with contextlib.closing(wave.open(full_path,'r')) as f:
      frames = f.getnframes()
      rate = f.getframerate()
      duration = frames / float(rate)
      video_lengths.append(duration)
