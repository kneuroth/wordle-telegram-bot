import datetime
import json
import os
import re
import requests
import ScheduledFunctions
from dotenv import load_dotenv

load_dotenv()

def get_todays_wordle():
    
    try:
        with open("wordlemap.json", "r") as wordle_map_file:
            wordle_map = json.load(wordle_map_file)
            return wordle_map[str(datetime.date.today())]
    except:
        print("not found locally, looking to API")
        ScheduledFunctions.record_todays_wordle()
        try:

            with open("wordlemap.json", "r") as wordle_map_file:
                wordle_map = json.load(wordle_map_file)
                return wordle_map[str(datetime.date.today())]
        except:
            return "NOT FOUND"


def get_wordle_number(date):
    # 505: Nov 6, 2022
    delta = int(re.split(' days|:| day,', str(date - datetime.date(2022, 11, 6)))[0])
    return delta + 505
    #return datetime.date.today - date

