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
YES_NO_OPTIONS = ['Yes', 'No', 'Yes (start render)', 'No (start render)']

def get_posts(videos_to_generate=None):
    if videos_to_generate is None:
        videos_to_generate = []
    log = utils.get_logger()
    # Get a reddit post
    try:
        post = ri.get_post(allow_over_18=True)
    except ImportError as error:
        log.warning(error)
        get_posts(videos_to_generate)

    subreddit = post['subreddit']
    title = post['title']
    body = post['selftext']
    is_nsfw = post['over_18']
    nsfw_string = ''
    if is_nsfw:
        nsfw_string = 'NSFW'
    with open('current_post_tmp.md', 'w', encoding='UTF-8') as post_details_file:
        post_details_file.writelines([
            f'# {subreddit}\n',
            f'{nsfw_string}\n',
            f'{title}\n',
            body]
        )
    terminal_menu = TerminalMenu(YES_NO_OPTIONS,
                                 title='Would you like to add this video to the render queue?\n' \
                                     f'Currently {len(videos_to_generate)} video(s) in render queue',
                                 preview_command='bat --color=always --line-range=:500\
                                     --terminal-width 200 current_post_tmp.md',
                                 preview_size=0.75,
                                 clear_screen=True)
    selected_index = terminal_menu.show()

    utils.remove_file('current_post_tmp.md')

    if selected_index == 0 or selected_index == 2:
        videos_to_generate.append(post)


    if selected_index == 0 or selected_index == 1:
        get_posts(videos_to_generate)

    return videos_to_generate

def run():
    log = utils.get_logger()

    # Create a tts instance early to avoid re-creation on each loop
    tts_instance = TTS(model_name="tts_models/en/vctk/vits")

    # Loop and generate list of posts
    posts_to_generate = get_posts()
    for post in posts_to_generate :
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

        subprocess.run(generate_video_command, shell=True, check=False)

        # Clean up temporary files
        log.info('Removing temporary files')
        utils.remove_file(BACKGROUND_VIDEO_PATH)
        utils.remove_tts_audio_files()
