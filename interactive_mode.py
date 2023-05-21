from simple_term_menu import TerminalMenu
import reddit_integration as ri
import utils
import media_creation

YES_NO_OPTIONS = ['Yes', 'No', 'Yes (start render)', 'No (start render)']
SUBREDDIT_OPTIONS = ['Done', 'All'] + ri.ALL_SUBREDDITS

def get_posts(videos_to_generate=None, subreddits=None, timeframe=None):
    if videos_to_generate is None:
        videos_to_generate = []
    log = utils.get_logger()
    # Get a reddit post
    try:
        post = ri.get_post(allow_over_18=True, subreddits=subreddits, timeframe=timeframe)
    except ImportError as error:
        log.warning(error)
        get_posts(videos_to_generate, subreddits=subreddits, timeframe=timeframe)

    subreddit = post['subreddit']
    title = post['title']
    body = post['selftext']
    is_nsfw = post['over_18']

    with open('current_post_tmp.md', 'w', encoding='UTF-8') as post_details_file:
        post_details_file.writelines([
            f'# {subreddit}\n',
            f'{"NSFW" if is_nsfw else ""}\n',
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

    if selected_index in (0, 2):
        videos_to_generate.append(post)

    if selected_index in (0, 1):
        get_posts(videos_to_generate, subreddits=subreddits, timeframe=timeframe)

    return videos_to_generate

def run(tts_instance):
    # Choose settings
    selecting_subreddits = True
    selected_subreddits = []
    while selecting_subreddits:
        subreddit_menu = TerminalMenu(SUBREDDIT_OPTIONS,
                                    title='Which subreddits would you like to fetch posts from?',
                                    preview_command='bat --color=always --line-range=:500\
                                        --terminal-width 200 selected_subreddits.md',
                                    preview_size=0.75,
                                    clear_screen=True)
        selected_subreddit_index = subreddit_menu.show()
        if selected_subreddit_index > 1:
            selected_subreddits.append(ri.ALL_SUBREDDITS[selected_subreddit_index-2])
            with open('selected_subreddits.md', 'a', encoding='UTF-8') as selected_subreddits_file:
                selected_subreddits_file.write(f'{selected_subreddits[-1]}\n')
        elif selected_subreddit_index == 1:
            selected_subreddits = ri.ALL_SUBREDDITS
            selecting_subreddits = False
        elif selected_subreddit_index == 0:
            selecting_subreddits = False
    if selected_subreddits:
        utils.remove_file('selected_subreddits.md')

    timeframe_menu = TerminalMenu(ri.POSSIBLE_TIMEFRAMES,
                                 title='Fetch top posts from:',
                                 clear_screen=True)
    selected_timeframe_index = timeframe_menu.show()

    # Generate all posts
    media_creation.generate_videos(tts_instance,
                                   get_posts(subreddits=set(selected_subreddits),
                                             timeframe=ri.POSSIBLE_TIMEFRAMES[selected_timeframe_index]))
