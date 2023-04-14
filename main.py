import subprocess
import json
import argparse
import cv2
from TTS.api import TTS
import reddit_integration as ri
import utils
import tts

# Define paths and buzz words for output files
BACKGROUND_VIDEO_PATH = './video-generation/public/video/backgroundVideo.mp4'
OUTPUT_FILE_BUZZ_WORDS = 'reddit_story_crazy_reading_reddit_short_funny_sad_insane'

# Initialize logger
log = utils.get_logger()

# Function to create configuration file for video generation
def create_react_config_file(background_video_frame_count, sentences, video_lengths, author, subreddit):
    config = {
        "backgroundVideoFrameCount": background_video_frame_count,
        "sentences": sentences,
        "videoLengths": video_lengths,
        "totalLength": sum(video_lengths),
        "author": author,
        "subreddit": subreddit
    }
    json_config = json.dumps(config)
    with open('current-config.json', 'w', encoding='UTF-8') as config_file:
        config_file.write(json_config)

# Function to get post details from Reddit
def get_post_details():
    try:
        post = ri.get_post()
    except ImportError as error:
        log.warning(error)
        return
    return {
        "title": post['title'],
        "body": post['selftext'],
        "author": post['author'],
        "subreddit": post['subreddit'],
        "post_id": post['name'],
        "link_to_post": f'https://www.reddit.com{post["permalink"]}'
    }

# Function to generate TTS audio files for video
def generate_tts_audio_files(tts_instance, title, body, subreddit):
    try:
        video_lengths, sentences = tts.generate_tts_for_sentences(tts_instance, title, body, subreddit)
        print(sentences)
    except AttributeError as error:
        log.warning('Failed to generate TTS: %s', error)
        utils.remove_tts_audio_files()
        return
    return video_lengths, sentences

# Function to generate background video frame count
def generate_background_video_frame_count():
    try:
        utils.generate_background_video()
    except Exception as error:
        log.warning('Failed to generate Background video: %s', error)
        utils.remove_tts_audio_files()
        return

    cap = cv2.VideoCapture(BACKGROUND_VIDEO_PATH)
    background_video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    return background_video_frame_count

# Function to run video generation process
def run_video_generation(args, generated_videos):
    tts_instance = TTS(model_name="tts_models/en/vctk/vits")

    while generated_videos < args.number_of_videos:
        post_details = get_post_details()
        if not post_details:
            return

        result = generate_tts_audio_files(tts_instance, post_details["title"], post_details["body"], post_details["subreddit"])
        if result is None:
            continue

        video_lengths, sentences = result

        background_video_frame_count = generate_background_video_frame_count()
        if not background_video_frame_count:
            return

        create_react_config_file(background_video_frame_count, sentences, video_lengths, post_details["author"], post_details["subreddit"])

        # Verify output folder exists
        folder_name = f'{post_details["subreddit"]}_{post_details["post_id"]}'
        utils.check_for_folder_or_create(f'./out/{folder_name}')

        # Write description file
        with open(f'./out/{folder_name}/{post_details["post_id"]}_desc.txt', 'w', encoding='UTF-8') as description_file:
            log.info('Writing description file...')
            description_file.write(utils.get_video_description_string(post_details["author"], post_details["subreddit"], post_details["link_to_post"]))

        # Generate the complete video
        log.info('Running Remotion render')
        generate_video_command = f'cd video-generation; npx remotion render RedditStory\
            ../out/{post_details["subreddit"]}_{post_details["post_id"]}/{post_details["subreddit"]}_{OUTPUT_FILE_BUZZ_WORDS}.mp4 --props=../current-config.json'
        preview_video_command = 'cd video-generation; npx remotion preview RedditStory --props=../current-config.json'

        if not args.preview:
            subprocess.run(generate_video_command, shell=True, check=False)
        else:
            subprocess.run(preview_video_command, shell=True, check=False)

        # Clean up temporary files
        log.info('Removing temporary files')
        utils.remove_file(BACKGROUND_VIDEO_PATH)
        utils.remove_tts_audio_files()

        generated_videos += 1

# Main function to execute video generation
def main(args):
    log = utils.get_logger()
    generated_videos = 0

    run_video_generation(args, generated_videos)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YAAAAAARRRRRRRR(s), Im a pirate!!')

    parser.add_argument(
        '--number_of_videos',
        '-n',
        required=False,
        type=int,
        default=1,
        help='Generates n videos'
    )

    parser.add_argument(
        '--preview',
        '-p',
        required=False,
        action='store_true',
        help='Used to run remotion in preview mode instead of render mode.'
    )

    main(parser.parse_args())
