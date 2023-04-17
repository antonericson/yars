from simple_term_menu import TerminalMenu
# pylint: disable-next=import-error
from TTS.api import TTS
import run_modes as modes
import utils

RUN_MODE_OPTIONS = [mode['name'] for mode in modes.ALL_OPTIONS]

def main():
    # Initialize logger first to avoid log propagatetion
    utils.get_logger()
    # Create a tts instance early to avoid re-creation on each loop
    tts_instance = TTS(model_name="tts_models/en/vctk/vits")

    terminal_menu = TerminalMenu(RUN_MODE_OPTIONS,
                                 title='How would you like to run YARS?',
                                 clear_screen=True)
    selected_index = terminal_menu.show()
    modes.ALL_OPTIONS[selected_index]['callback'](tts_instance)

if __name__ == '__main__':
    main()
