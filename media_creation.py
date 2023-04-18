import subprocess
import cv2
import utils
import tts

BACKGROUND_VIDEO_PATH = './video-generation/public/video/backgroundVideo.mp4'
OUTPUT_FILE_BUZZ_WORDS = 'reddit_story_crazy_reading_reddit_short_funny_sad_insane'

def generate_videos(tts_instance, posts, preview_mode=False):
    log = utils.get_logger()
    total_videos_created = 0
    for post in posts:
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
            total_videos_created -= 1
            continue

        try:
            utils.generate_background_video()
        except Exception as error:
            log.warning('Failed to generate Background video: %s', error)
            utils.remove_tts_audio_files()
            return total_videos_created

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
        if preview_mode:
            generate_video_command = 'cd video-generation; npx remotion preview RedditStory\
                --props=../current-config.json'
        else:
            generate_video_command = f'cd video-generation; npx remotion render RedditStory\
                ../out/{subreddit}_{post_id}/{subreddit}_{OUTPUT_FILE_BUZZ_WORDS}.mp4 --props=../current-config.json'
        try:
            subprocess.run(generate_video_command, shell=True, check=False)
        except KeyboardInterrupt:
            log.info('Remotion interrupted, continuing')

        # Clean up temporary files
        log.info('Removing temporary files')
        utils.remove_file(BACKGROUND_VIDEO_PATH)
        utils.remove_tts_audio_files()
        total_videos_created += 1

    return total_videos_created
