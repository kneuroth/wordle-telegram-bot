import datetime
import re
import os
import requests

def get_wordle_number(date: datetime.date):
    # Maps Wordle number 505 to Nov 6, 2022 (arbitrarily selected)
    delta = int(re.split(' days|:| day,', str(date - datetime.date(2022, 11, 6)))[0])
    return delta + 505


def get_wordle():
    try:

        headers = {
                "X-RapidAPI-Key": os.environ.get('WORDLE_ANSWER_API_KEY'),
                "X-RapidAPI-Host": os.environ.get('WORDLE_ANSWER_API_HOST')
            }
        
        return requests.get(f"{os.environ.get('WORDLE_ANSWER_API_URL')}/today", headers=headers).json()["today"]

            
    except Exception as err:
        print(err)
        return "?????"