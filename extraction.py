from datetime import date

import string
import re

def extract_update_fields(update: dict) -> dict:
    """Returns all needed fields to process the message, assumes update has text"""
    return {
        "update_id": update["update_id"], # Probably will not need this
        "chat_id" : update["message"]["chat"]["id"],
        "chat_name": update["message"]["chat"]["title"],
        "date": str(date.fromtimestamp(update["message"]["date"])),
        "name": update["message"]["from"]["first_name"],
        "text": update["message"]["text"]
    }

def extract_wordle_number(text: string) -> int:
    """Retrns integer of a string's wordle number (not score, see exract_wordle_score)"""
    return int(text[7:11])

def extract_wordle_score(text: string) -> int:
    """Returns integer of a string's wordle score"""
    score = text[text.index("/") - 1]
    if score == 'X':
        return 7
    return int(score)