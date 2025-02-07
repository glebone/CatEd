# config.py

import openai

# Set your API key here.
openai.api_key = ""
# Default correction prompt (feel free to modify this or replace it).
CORRECTION_PROMPT_DEFAULT = (
    "Please check the following text for grammar and syntax errors. "
    "Correct the text without making major changes and return the corrected text. "
    "Also, provide a list of the corrections made in bullet points. "
    "Format your response exactly as follows:\n\n"
    "Corrected Text:\n<corrected text goes here>\n\n"
    "Corrections:\n- Correction 1\n- Correction 2\n..."
)

# Global variables to be used across modules
correction_prompt = CORRECTION_PROMPT_DEFAULT
loaded_file = None

