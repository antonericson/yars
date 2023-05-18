import contextlib
import wave
import csv
import re

PARENTHESIS = ['(', ')']
END_MARKS = ['.', '!', '?']

def replace_common_shortenings(text):
    with open('shortenings.txt', 'r', encoding='UTF-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            shortening = row[0].strip()
            expanded = row[1].strip()
            text = re.sub(rf'\b{shortening}\b', expanded, text)
    return text

def add_full_stop(text):
    if not text == '':
        if not text[-1] in END_MARKS:
            text += '.'
    return text

def get_sentences_from_story(title, text):
    preferred_len = 120
    max_len = 250
    text = remove_edits(text)
    title = add_full_stop(title.strip())
    text = add_full_stop(text.strip())

    all_text = (f'{title} {text}').strip()
    paragraphs = []
    text_buffer = all_text
    loop_cond = True
    while loop_cond:
        last_comma = last_stop = last_space = last_parenthesis = None
        if len(text_buffer) == 0:
            break

        for i, char in enumerate(text_buffer):
            if char in PARENTHESIS:
                last_parenthesis = i
            if char in END_MARKS:
                last_stop = i
            if char == ',':
                last_comma = i
            if(char == ' ') and (not i>=(preferred_len-1)):
                last_space = i
            if i == (len(text_buffer)-1):
                # Stop of buffer
                paragraphs.append(text_buffer)
                loop_cond = False
                break
            if (i >= (preferred_len-1) and last_stop) or i>=max_len:
                # Reached sentence length
                append_to = None

                if last_stop:
                    append_to = last_stop
                elif last_parenthesis:
                    if text_buffer[last_parenthesis] == PARENTHESIS[0]:
                        # Don't include this parenthesis
                        append_to = max(last_parenthesis - 1, 0)
                    else:
                        # Include closing parenthesis
                        append_to = last_parenthesis
                elif last_comma:
                    append_to = last_comma
                elif last_space:
                    append_to = last_space
                else:
                    loop_cond = False
                    break

                paragraphs.append(text_buffer[:append_to+1])
                text_buffer = text_buffer[append_to+1:]
                break

    return [x.strip() for x in paragraphs]

def remove_edits(text):
    has_edits = 'edit: ' in text or 'EDIT: ' in text or 'Edit: ' in text
    while has_edits:
        text = text.split('edit: ')[0]
        text = text.split('Edit: ')[0]
        text = text.split('EDIT: ')[0]
        has_edits = 'edit: ' in text or 'EDIT: ' in text or 'Edit: ' in text

    return text

def generate_tts_for_sentences(tts, title, body, subreddit):

    # Split text into sentences fo easier sync of text in video
    # If sentences are too long, split at commas/parenthesis/question mark etc.
    sentences = [subreddit]
    title = replace_common_shortenings(title)
    body = replace_common_shortenings(body)
    sentences.extend(get_sentences_from_story(title, body))

    video_lengths = []
    for i, sentence in enumerate(sentences):
        path_for_react = f'audio/{i}.wav'
        full_path = f'./video-generation/public/{path_for_react}'
        tts.tts_to_file(text=sentence, speaker="p273", file_path=full_path)
        with contextlib.closing(wave.open(full_path,'r')) as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration = frames / float(rate)
            video_lengths.append(duration)

    # Discard if combined audio length is over 58 seconds
    # Max length of YouTube Short is 60 seconds
    if sum(video_lengths) > 58 :
        raise AttributeError('Provided story would become longer than 60 seconds')

    return [ video_lengths, sentences ]
