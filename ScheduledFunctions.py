import datetime
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def record_todays_wordle():
    headers = {
                    "X-RapidAPI-Key": os.environ.get('WORDLE_ANSWER_API_KEY'),
                    "X-RapidAPI-Host": os.environ.get('WORDLE_ANSWER_API_HOST')
                }
    word = requests.get(f"{os.environ.get('WORDLE_ANSWER_API_URL')}/today", headers=headers).json()["today"]
    wordle_map = {}
    with open("wordlemap.json", "r") as wordle_map_file:
        wordle_map = json.load(wordle_map_file)
    
    with open("wordlemap.json", "w") as wordle_map_file:
        wordle_map[str(datetime.date.today())] = word
        wordle_map_file.write(json.dumps(wordle_map))

    return json.dumps(wordle_map)