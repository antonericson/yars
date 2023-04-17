from simple_term_menu import TerminalMenu
import run_modes as modes

RUN_MODE_OPTIONS = [mode['name'] for mode in modes.ALL_OPTIONS]

def main():
    terminal_menu = TerminalMenu(RUN_MODE_OPTIONS)
    selected_index = terminal_menu.show()
    modes.ALL_OPTIONS[selected_index]['callback']()

if __name__ == '__main__':
    main()
