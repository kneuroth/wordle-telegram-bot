import re
import jsonschema
import os
import datetime

from context import get_wordle_number

#env = os.getenv("ENV")
#chat_id = os.getenv("CHAT_ID")
#signup_phrase = os.getenv("SIGNUP_PHRASE")

update_schema = {
    "type": "object",
    "properties": {
        "update_id": {"type": "integer"},
        "message": {
            "type": "object",
            "properties": {
                "message_id": {"type": "integer"},
                "from": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "username": {"type": "string"}
                    },
                    "required": ["id", "first_name"]
                },
                "chat": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "type": {"type": "string"}
                    },
                    "required": ["id", "title", "type"]
                },
                "date": {"type": "integer"},
                "text": {"type": "string"}
            },
            "required": ["message_id", "from", "chat", "date", "text"]
        },

    },
    "required": ["update_id", "message"]
}
# -------HELPER FUNCTIONS--------#

def is_valid_message(update):
    # Validates the JSON schema of the update object
    try:
        jsonschema.validate(instance=update, schema=update_schema)
    except jsonschema.exceptions.ValidationError as e:
        # Handle the error here
        # print(e)
        return False
    return True

def is_wordle_submission(text):
    # Validates that the text of a message follows Wordle submission structure
    pattern = re.compile("^Wordle [0-9],[0-9]{3} [1-6,X]/6")
    return bool(re.match(pattern, text))

def is_todays_wordle_number(text):
    # Validates that the Wordle number (number after the word Wordle) is today's wordle number
    return int(text[7:11]) == get_wordle_number(datetime.date.today())


# -------EXPORTED FUNCTIONS--------#

def is_valid_score_submission(update):
    """
    Verify weather the received Telegram update is a valid score submission message
    indicating that the user wants to submit their Wordle score for the day

    Parameters
    ----------
    update : object
        Telegram update object

    Returns
    -------
    Boolean
        Returns True if the given update:
        - Has valid Telegram update message schema
        - Is from the correct group chat
        - Has correctly formatted Wordle score
        - The Wordle score submission is from the current day
        Returns False otherwise

    Raises
    ------
    None

    Notes
    -----
    None
    """
    # For multiple chat supppot, replace is_valid_message_and_chat with validate_json()
    return is_valid_message(update) and is_wordle_submission(update["message"]["text"]) and is_todays_wordle_number(update["message"]["text"])