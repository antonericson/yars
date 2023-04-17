import reddit_integration as ri
import utils
import media_creation

BACKGROUND_VIDEO_PATH = './video-generation/public/video/backgroundVideo.mp4'
OUTPUT_FILE_BUZZ_WORDS = 'reddit_story_crazy_reading_reddit_short_funny_sad_insane'
RUN_OPTIONS = ['One', 'Specify number']

def preview(tts_instance):
    log = utils.get_logger()
    try:
        posts = get_exact_number_of_posts(1)
    except ImportError as error:
        log.warning(error)
        return

    media_creation.generate_videos(tts_instance, posts, preview_mode=True)

def default(tts_instance):
    log = utils.get_logger()
    number_of_videos = None
    while number_of_videos is None:
        try:
            number_of_videos = int(input('Input number of videos to generate:\n'))
        except ValueError:
            log.error('Input is not a number')

    while number_of_videos > 0:
        try:
            posts = get_exact_number_of_posts(number_of_videos)
        except ImportError as error:
            log.warning(error)
            return

        number_of_videos -= media_creation.generate_videos(tts_instance, posts)

def get_exact_number_of_posts(number_of_posts):
    posts = []
    while len(posts) < number_of_posts:
        posts.append(ri.get_post())

    return posts
