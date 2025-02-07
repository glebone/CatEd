import curses
import curses.textpad
import os
import pyperclip
from datetime import datetime

import config
from openai_helper import call_openai_correction
from ui_helpers import (
    update_status_bar,
    show_modal,
    show_about_modal,
    show_edit_prompt_modal,
    load_file_modal
)

def main(stdscr):
    curses.curs_set(1)
    curses.start_color()
    curses.raw()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Editor mode
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW) # Corrected mode
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)    # Error/status messages

    max_y, max_x = stdscr.getmaxyx()
    editor_height = max_y // 2 - 1
    result_height = max_y - editor_height - 2

    editor_win = curses.newwin(editor_height, max_x, 0, 0)
    result_win = curses.newwin(result_height, max_x, editor_height, 0)
    status_win = curses.newwin(1, max_x, max_y - 1, 0)

    editor_win.keypad(True)
    result_win.keypad(True)
    status_win.keypad(True)
    stdscr.keypad(True)

    editor_box = curses.textpad.Textbox(editor_win, insert_mode=True)

    original_text = ""
    result_text = ""
    corrections_list = []
    current_mode = "editor"

    update_status_bar(
        status_win,
        "^..^ CATed - EDITOR MODE – Type text. Press TAB to switch to corrected mode.",
        1
    )

    while True:
        if current_mode == "editor":
            ch = editor_win.getch()
            if ch == 9:  # TAB => switch to corrected mode
                editor_win.refresh()
                original_text = ""

                for y in range(editor_height):
                    try:
                        line = editor_win.instr(y, 0).decode('utf-8').rstrip()
                    except Exception:
                        line = ""
                    original_text += line + "\n"

                # Auto-save
                if config.loaded_file:
                    filename = config.loaded_file
                else:
                    filename = "cated_" + datetime.now().strftime("%d_%m_%Y") + ".txt"
                    config.loaded_file = filename

                with open(filename, "w") as f:
                    f.write(original_text)

                # Display in result pane
                result_win.erase()
                for idx, line in enumerate(original_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()

                # Switch mode
                current_mode = "corrected"
                update_status_bar(
                    status_win,
                    "^..^ CATed - CORRECTED MODE – R: rewrite/correct | E: view corrections | C: copy | P: edit prompt | L: load file | Q: quit",
                    2
                )

            elif ch == 27:  # ESC => Quit from editor mode
                break
            elif ch in (ord('a'), ord('A')):
                show_about_modal(stdscr)
                editor_win.refresh()
                status_win.refresh()
            else:
                editor_box.do_command(ch)
                editor_win.refresh()

        elif current_mode == "corrected":
            ch = result_win.getch()
            if ch in (ord('r'), ord('R')):
                update_status_bar(status_win, "R pressed: Correcting errors...", 2)
                result_text, corrections_list = call_openai_correction(original_text)

                result_win.erase()
                for idx, line in enumerate(result_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()

                update_status_bar(
                    status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view corrections | C: copy | P: edit prompt | L: load file | Q: quit",
                    2
                )

            elif ch in (ord('e'), ord('E')):
                update_status_bar(status_win, "Viewing corrections...", 2)
                if corrections_list:
                    show_modal(stdscr, corrections_list)
                else:
                    update_status_bar(status_win, "No corrections available.", 3)
                    curses.napms(1000)

                # Repaint the result window
                result_win.erase()
                for idx, line in enumerate(result_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()

                update_status_bar(
                    status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view corrections | C: copy | P: edit prompt | L: load file | Q: quit",
                    2
                )

            elif ch in (ord('p'), ord('P')):
                # --- EDIT PROMPT ---
                saved = show_edit_prompt_modal(stdscr, status_win)
                # Regardless of saved or cancelled, we remain in corrected mode.
                # Re-draw the split screen to avoid a blank screen:
                editor_win.erase()
                for idx, line in enumerate(original_text.splitlines()):
                    if idx < editor_height:
                        editor_win.addstr(idx, 0, line[:max_x - 1])
                editor_win.refresh()

                result_win.erase()
                for idx, line in enumerate(result_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()

                # Re-update the status bar
                update_status_bar(
                    status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view corrections | C: copy | P: edit prompt | L: load file | Q: quit",
                    2
                )

            elif ch in (ord('l'), ord('L')):
                chosen = load_file_modal(stdscr)
                if chosen:
                    with open(chosen, "r") as f:
                        content = f.read()
                    config.loaded_file = chosen

                    editor_win.erase()
                    for idx, line in enumerate(content.splitlines()):
                        if idx < editor_height:
                            editor_win.addstr(idx, 0, line[:max_x - 1])
                    editor_win.refresh()

                    # Switch back to editor
                    current_mode = "editor"
                    update_status_bar(
                        status_win,
                        f"^..^ CATed - EDITOR MODE – Loaded file: {os.path.basename(config.loaded_file)} | Press TAB to update",
                        1
                    )
                else:
                    update_status_bar(status_win, "File load cancelled.", 3)

            elif ch in (ord('c'), ord('C')):
                pyperclip.copy(result_text)
                update_status_bar(status_win, "Corrected text copied to clipboard!", 2)
                curses.napms(1000)
                update_status_bar(
                    status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view corrections | C: copy | P: edit prompt | L: load file | Q: quit",
                    2
                )

            elif ch in (ord('q'), ord('Q')):
                # Quit from corrected mode
                break

if __name__ == '__main__':
    curses.wrapper(main)
