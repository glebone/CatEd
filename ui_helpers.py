import curses
import curses.textpad
import glob
import config

def update_status_bar(win, message, color_pair=1):
    """
    Update the status bar window with the given message.
    """
    win.erase()
    win.bkgd(' ', curses.color_pair(color_pair))
    max_x = win.getmaxyx()[1]
    win.addstr(0, 0, message[:max_x - 1])
    win.refresh()

def show_edit_prompt_modal(stdscr, status_win):
    """
    Show a modal window for editing the correction prompt.
    
    Keys:
      ESC      => Quit/discard changes (returns False)
      SHIFT+E  => Save/apply changes (returns True)
    
    Return:
      True  = user saved the prompt
      False = user cancelled/ESC
    
    The caller is responsible for re-drawing the screen afterwards.
    """
    # 1) Update the status bar with instructions
    update_status_bar(
        status_win,
        "PROMPT EDITING – ESC=discard, SHIFT+E=save",
        3  # color pair 3 for emphasis
    )

    max_y, max_x = stdscr.getmaxyx()
    
    # 2) Make the modal a bit bigger if terminal allows
    modal_height = min(15, max_y - 4)
    modal_width = min(100, max_x - 4)
    
    begin_y = (max_y - modal_height) // 2
    begin_x = (max_x - modal_width) // 2

    # 3) Create the modal window (bordered)
    win = curses.newwin(modal_height, modal_width, begin_y, begin_x)
    win.border()
    
    title = " Edit Correction Prompt "
    win.addstr(0, 2, title, curses.A_BOLD)
    
    usage_note = "(Type your prompt. Press ESC=discard or SHIFT+E=save.)"
    win.addstr(1, 2, usage_note, curses.A_DIM)

    bottom_reminder = "Press SHIFT+E to apply changes."
    win.addstr(modal_height - 2, 2, bottom_reminder, curses.A_BOLD)

    # 4) Subwindow for the Textbox
    edit_win_height = modal_height - 4  # space for top & bottom lines
    edit_win_width = modal_width - 4
    edit_win = win.derwin(edit_win_height, edit_win_width, 2, 2)

    # 5) Load existing prompt lines
    prompt_lines = config.correction_prompt.split('\n')
    for row, line in enumerate(prompt_lines):
        if row >= edit_win_height:
            break
        edit_win.addstr(row, 0, line[:edit_win_width])

    curses.curs_set(1)
    textbox = curses.textpad.Textbox(edit_win)

    saved = False
    while True:
        ch = edit_win.getch()
        
        if ch == 27:  # ESC => discard changes
            break
        
        elif ch == 69:  # SHIFT+E => ASCII 69
            # Save changes
            new_prompt = textbox.gather().strip()
            if new_prompt:
                config.correction_prompt = new_prompt
            saved = True
            break
        
        else:
            textbox.do_command(ch)

    curses.curs_set(0)
    win.clear()
    stdscr.touchwin()
    stdscr.refresh()

    # Update status bar to reflect if we saved or cancelled
    if saved:
        update_status_bar(status_win, "Prompt updated.", 2)
    else:
        update_status_bar(status_win, "Prompt edit cancelled.", 3)
    
    return saved

def show_modal(stdscr, corrections):
    """
    A simple modal that shows the corrections list.
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
    modal_win.getch()
    modal_win.clear()
    stdscr.touchwin()
    stdscr.refresh()

def show_about_modal(stdscr):
    about_text = [
        "^..^ CatEd - AI Text Editor",
        "Version: 0.0.1",
        "Author: Your Name",
        "License: MIT",
        "",
        "Press any key to close"
    ]
    max_y, max_x = stdscr.getmaxyx()
    modal_height = min(len(about_text) + 4, max_y - 4)
    modal_width = min((max(len(line) for line in about_text) + 4) if about_text else 40, max_x - 4)
    begin_y = (max_y - modal_height) // 2
    begin_x = (max_x - modal_width) // 2

    modal_win = curses.newwin(modal_height, modal_width, begin_y, begin_x)
    modal_win.keypad(True)
    modal_win.border()
    for idx, line in enumerate(about_text, start=1):
        if idx < modal_height - 1:
            modal_win.addstr(idx, 2, line[:modal_width - 4])
    modal_win.refresh()
    modal_win.getch()
    modal_win.clear()
    stdscr.touchwin()
    stdscr.refresh()

def load_file_modal(stdscr):
    files = sorted(glob.glob("cated_*.txt"))
    if not files:
        return None

    max_y, max_x = stdscr.getmaxyx()
    modal_height = min(len(files) + 4, max_y - 4)
    modal_width = 50
    begin_y = (max_y - modal_height) // 2
    begin_x = (max_x - modal_width) // 2

    win = curses.newwin(modal_height, modal_width, begin_y, begin_x)
    win.keypad(True)
    selected = 0

    while True:
        win.clear()
        win.border()
        win.addstr(0, 2, " Select file to load ", curses.A_BOLD)
        
        for idx, filename in enumerate(files):
            attr = curses.A_REVERSE if idx == selected else curses.A_NORMAL
            win.addstr(idx + 1, 2, filename[:modal_width - 4], attr)
        
        key = win.getch()
        if key in (curses.KEY_UP, ord('k'), ord('K')) and selected > 0:
            selected -= 1
        elif key in (curses.KEY_DOWN, ord('j'), ord('J')) and selected < len(files) - 1:
            selected += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            chosen = files[selected]
            win.clear()
            stdscr.touchwin()
            stdscr.refresh()
            return chosen
        elif key == 27:  # ESC to cancel
            win.clear()
            stdscr.touchwin()
            stdscr.refresh()
            return None
