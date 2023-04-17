import subprocess
import cv2
from simple_term_menu import TerminalMenu
# pylint: disable-next=import-error
from TTS.api import TTS
import reddit_integration as ri
import utils
import tts

BACKGROUND_VIDEO_PATH = './video-generation/public/video/backgroundVideo.mp4'
OUTPUT_FILE_BUZZ_WORDS = 'reddit_story_crazy_reading_reddit_short_funny_sad_insane'
RUN_OPTIONS = ['One', 'Specify number']

def preview():
    generate_videos(number_of_videos=1, run_in_preview_mode=True)

def default():
    terminal_menu = TerminalMenu(RUN_OPTIONS)
    selected_index = terminal_menu.show()

    if selected_index == 0:
        number_of_videos = 1
    elif selected_index == 1:
        number_of_videos = int(input('Input number of videos to generate:\n'))

    generate_videos(number_of_videos=number_of_videos)


def generate_videos(number_of_videos, run_in_preview_mode=False):
    log = utils.get_logger()
    log.info('Generating %s video(s)', number_of_videos)

    generated_videos = 0

    # Create a tts instance early to avoid re-creation on each loop
    tts_instance = TTS(model_name="tts_models/en/vctk/vits")

    while generated_videos < number_of_videos :
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
        utils.create_react_config(background_video_frame_count, sentences, video_lengths, author, subreddit)

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
            ../out/{subreddit}_{post_id}/{subreddit}_{OUTPUT_FILE_BUZZ_WORDS}.mp4 --props=../current-config.json'
        preview_video_command = 'cd video-generation; npx remotion preview RedditStory --props=../current-config.json'

        if not run_in_preview_mode:
            subprocess.run(generate_video_command, shell=True, check=False)
        else:
            subprocess.run(preview_video_command, shell=True, check=False)

        # Clean up temporary files
        log.info('Removing temporary files')
        utils.remove_file(BACKGROUND_VIDEO_PATH)
        utils.remove_tts_audio_files()

        #It's deemed that a video has been generated
        generated_videos += 1
