# App README

This application provides a text editor interface that integrates OpenAI's API for text correction. It combines configuration settings, API calls, and UI interactions to offer functionalities like live editing, auto-correction, and file loading in a terminal environment.

## File Structure

- .gitignore: Specifies files and directories to ignore in the repository.
- cated.py: Contains the main application logic and the user interface built with curses.
- config.py: Holds configuration variables such as the OpenAI API key and the default correction prompt.
- openai_helper.py: Includes helper functions to interact with OpenAI's APIs.
- ui_helpers.py: Provides helper functions for managing UI components (status bar, modals, file dialogs, etc.).

## Getting Started

1. Set your OpenAI API key in config.py.
2. Ensure all dependencies (like curses, pyperclip, and openai) are installed.
3. Run the application via the main script (e.g., using `python cated.py`).

## Additional Information

Further details and usage instructions can be added to the documentation as needed.
