# openai_helper.py

from openai import OpenAI
import config


client = OpenAI(api_key=config.openai.api_key)


def call_openai_correction(text):
    """
    Calls the OpenAI API with the current correction prompt from config.
    Returns:
        tuple: (corrected_text, list_of_corrections)
    """
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",  # Or any other model you prefer
        messages=[
            {"role": "system", "content": config.correction_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.2)
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
        return f"Error calling OpenAI API: {str(e)}", []
