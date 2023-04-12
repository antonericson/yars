import subprocess
import json
import argparse
import cv2
# pylint: disable-next=import-error
from TTS.api import TTS
import reddit_integration as ri
import utils
import tts

BACKGROUND_VIDEO_PATH = './video-generation/public/video/backgroundVideo.mp4'

def create_react_config(background_video_frame_count, sentences, video_lengths, author, subreddit):
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

def main(args):
    log = utils.get_logger()
    generated_videos = 0

    # Create a tts instance early to avoid re-creation on each loop
    tts_instance = TTS(model_name="tts_models/en/vctk/vits")

    while generated_videos < args.number_of_videos :
        # Get a reddit post
        try:
            post = ri.get_post()
        except ImportError as error:
            log.warning(error)
            return
        title = post['title']
        body = post['selftext']
        author = post['author']
        subreddit = post['subreddit']
        post_id = post['name']
        link_to_post = f'https://www.reddit.com{post["permalink"]}'

        # Generate TTS audio files and return list of each files length in seconds
        # and list of sentences.
        try:
            [ video_lengths, sentences ] = tts.generate_tts_for_sentences(tts_instance, title, body, subreddit)
            print(sentences)
        except AttributeError as error:
            log.warning('Failed to generate TTS: %s', error)
            utils.remove_tts_audio_files()
            continue

        try:
            utils.generate_background_video()
        except Exception as error:
            log.warning('Failed to generate Background video: %s', error)
            utils.remove_tts_audio_files()
            return

        # Calculate total frame count of background video
        # pylint: disable-next=no-member
        cap = cv2.VideoCapture(BACKGROUND_VIDEO_PATH)
        # pylint: disable-next=no-member
        background_video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # Build config file for React to use when rendering
        create_react_config(background_video_frame_count, sentences, video_lengths, author, subreddit)

        # Verify output folder exists
        folder_name = f'{subreddit}_{post_id}'
        utils.check_for_folder_or_create(f'./out/{folder_name}')

        # Write description file
        with open(f'./out/{folder_name}/{post_id}_desc.txt', 'w', encoding='UTF-8') as description_file:
            log.info('Writing description file...')
            description_file.write(utils.get_video_description_string(author, subreddit, link_to_post))

        # Generate the complete video
        log.info('Running Remotion render')
        generate_video_command = f'cd video-generation; npx remotion render RedditStory\
            ../out/{subreddit}_{post_id}/AmazingRedditStory.mp4 --props=../current-config.json'

        subprocess.run(generate_video_command, shell=True, check=False)

        # Clean up temporary files
        log.info('Removing temporary files')
        utils.remove_file(BACKGROUND_VIDEO_PATH)
        utils.remove_tts_audio_files()

        #It's deemed that a video has been generated
        generated_videos += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YAAAAAARRRRRRRR, Im a pirate!!')

    # Add your arguments here
    parser.add_argument(
        '--number_of_videos',
        '-n',
        required = False,
        type = int,
        default = 1,
        help='Generates n videos')

    main(parser.parse_args())
