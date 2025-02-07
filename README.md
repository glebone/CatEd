# ^..^ CATEd - AI-powered Text Editor


CATEd - ncurses based text editor with AI-powered text completion.


## File Structure

- cated.py: Contains the main application logic and the user interface built with curses.
- config.py: Holds configuration variables such as the OpenAI API key and the default correction prompt.
- openai_helper.py: Includes helper functions to interact with OpenAI's APIs.
- ui_helpers.py: Provides helper functions for managing UI components (status bar, modals, file dialogs, etc.).

## Getting Started

1. Set your OpenAI API key in config.py.
2. Ensure all dependencies (like curses, pyperclip, and openai) are installed.
3. Run the application via the main script (e.g., using `python cated.py`).

