'''
^..^ CAT(C) Soft Cat Editor
---------------------------
02 February 25 || glebone@gmail.com || ArchPad
'''

import curses
import curses.textpad
from openai import OpenAI
import pyperclip
from idlelib.editor import EditorWindow

# Initialize the OpenAI client with your API key.
client = OpenAI(api_key="")
# --- Helper: Call OpenAI to correct text ---
def call_openai_correction(text):
    """
    Calls the OpenAI API with a prompt to correct grammar and syntax errors.
    The response should contain a corrected text and a list of corrections.
    """
    prompt = (
        "Please check the following text for grammar and syntax errors. "
        "Correct the text without making major changes and return the corrected text. "
        "Also, provide a list of the corrections made in bullet points. "
        "Format your response exactly as follows:\n\n"
        "Corrected Text:\n<corrected text goes here>\n\nCorrections:\n- Correction 1\n- Correction 2\n..."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or your chosen model.
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )
        reply = response.choices[0].message.content

        # Parse the reply into corrected text and a list of corrections.
        if "Corrected Text:" in reply and "Corrections:" in reply:
            parts = reply.split("Corrections:")
            corrected_text = parts[0].replace("Corrected Text:", "").strip()
            corrections = parts[1].strip().splitlines()
        else:
            corrected_text = reply
            corrections = ["Could not parse corrections."]
        return corrected_text, corrections
    except Exception as e:
        return "Error calling OpenAI API: " + str(e), []

# --- Helper: Show Modal Window with Corrections ---
def show_modal(stdscr, corrections):
    """
    Create a centered modal window that lists the corrections.
    """
    max_y, max_x = stdscr.getmaxyx()
    modal_height = min(len(corrections) + 4, max_y - 4)
    modal_width = min((max(len(line) for line in corrections) + 4) if corrections else 40, max_x - 4)
    begin_y = (max_y - modal_height) // 2
    begin_x = (max_x - modal_width) // 2

    modal_win = curses.newwin(modal_height, modal_width, begin_y, begin_x)
    modal_win.keypad(True)
    modal_win.border()
    modal_win.addstr(1, 2, "Corrections:", curses.A_BOLD)
    for idx, line in enumerate(corrections, start=2):
        if idx < modal_height - 1:
            modal_win.addstr(idx, 2, line[:modal_width - 4])
    modal_win.addstr(modal_height - 2, 2, "Press any key to close")
    modal_win.refresh()
    modal_win.getch()  # Wait for a key press.
    modal_win.clear()
    stdscr.touchwin()
    stdscr.refresh()

# --- Helper: Update the Status Bar ---
def update_status_bar(status_win, message, color_pair=1):
    status_win.erase()
    status_win.bkgd(' ', curses.color_pair(color_pair))
    status_win.addstr(0, 0, message)
    status_win.refresh()

# --- Main Application ---
def main(stdscr):
    # Basic curses setup.
    curses.curs_set(1)
    curses.start_color()
    curses.raw()  # Pass control keys directly.

    # Set up color pairs.
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Editor mode.
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Corrected (command) mode.
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)     # Error/status messages.

    max_y, max_x = stdscr.getmaxyx()
    # Divide the screen: upper half for editor, lower half for corrected text, plus one status bar line.
    editor_height = max_y // 2 - 1
    result_height = max_y - editor_height - 2

    # Create windows.
    editor_win = curses.newwin(editor_height, max_x, 0, 0)
    result_win = curses.newwin(result_height, max_x, editor_height, 0)
    status_win = curses.newwin(1, max_x, max_y - 1, 0)

    # Enable keypad mode.
    editor_win.keypad(True)
    result_win.keypad(True)
    status_win.keypad(True)
    stdscr.keypad(True)

    # Create a Textbox for editor mode.
    editor_box = curses.textpad.Textbox(editor_win, insert_mode=True)

    # Variables to hold the text and corrections.
    original_text = ""
    result_text = ""
    corrections_list = []

    # Start in editor mode.
    current_mode = "editor"
    update_status_bar(status_win, "^..^ CATed - EDITOR MODE – Type text. Press TAB to switch to corrected mode.", 1)

    while True:
        if current_mode == "editor":
            ch = editor_win.getch()
            if ch == 9:  # TAB key pressed.
                # Gather text from editor and store it as the original text.
                editor_win.refresh()
                original_text = ""
                for y in range(editor_height):
                    try:
                        line = editor_win.instr(y, 0).decode('utf-8').rstrip()
                    except Exception:
                        line = ""
                    original_text += line + "\n"
                # Copy original text to the result window (uncorrected initially).
                result_win.erase()
                for idx, line in enumerate(original_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()
                # Switch to corrected (command) mode.
                current_mode = "corrected"
                update_status_bar(status_win,
                    "^..^ CATed - CORRECTED MODE – R: rewrite/correct | E: view errors | C: copy | Q: quit", 2)
            elif ch == 27:  # ESC key exits.
                break
            else:
                # Let the Textbox handle all other keys.
                editor_box.do_command(ch)
                editor_win.refresh()

        elif current_mode == "corrected":
            ch = result_win.getch()
            if ch in (ord('r'), ord('R')):
                # R: Call the correction API using the stored original text.
                update_status_bar(status_win, "R pressed: Correcting errors...", 2)
                result_text, corrections_list = call_openai_correction(original_text)
                result_win.erase()
                for idx, line in enumerate(result_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()
                update_status_bar(status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view errors | C: copy | Q: quit", 2)
            elif ch in (ord('e'), ord('E')):
                update_status_bar(status_win, "Viewing corrections...", 2)
                if corrections_list:
                    show_modal(stdscr, corrections_list)
                else:
                    update_status_bar(status_win, "No corrections available.", 3)
                    curses.napms(1000)
                # Re-display the corrected text after closing the modal.
                result_win.erase()
                for idx, line in enumerate(result_text.splitlines()):
                    if idx < result_height:
                        result_win.addstr(idx, 0, line[:max_x - 1])
                result_win.refresh()
                update_status_bar(status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view errors | C: copy | Q: quit", 2)
            elif ch in (ord('c'), ord('C')):
                pyperclip.copy(result_text)
                update_status_bar(status_win, "Corrected text copied to clipboard!", 2)
                curses.napms(1000)
                update_status_bar(status_win,
                    "CORRECTED MODE – R: rewrite/correct | E: view errors | C: copy | Q: quit", 2)
            elif ch in (ord('q'), ord('Q')):
                break
            # Ignore any other keys in corrected mode.

if __name__ == '__main__':
    curses.wrapper(main)
