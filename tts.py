import contextlib
import wave

def generateTTSForSentences(tts, sentences):
  video_lengths = []
  for i, sentence in enumerate(sentences):
    path_for_react = f'audio/{i}.wav'
    full_path = f'video-generation/public/{path_for_react}'
    tts.tts_to_file(text=sentence, speaker="p273", file_path=full_path)
    with contextlib.closing(wave.open(full_path,'r')) as f:
      frames = f.getnframes()
      rate = f.getframerate()
      duration = frames / float(rate)
      video_lengths.append(duration)
  
  return video_lengths
