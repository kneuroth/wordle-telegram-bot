import datetime
import re
import os
import requests
from bs4 import BeautifulSoup

def get_wordle_number(date: datetime.date):
    # Maps Wordle number 505 to Nov 6, 2022 (arbitrarily selected)
    delta = int(re.split(' days|:| day,', str(date - datetime.date(2022, 11, 6)))[0])
    return delta + 505

# def get_wordle():
#     try:

#         headers = {
#                 "X-RapidAPI-Key": os.environ.get('WORDLE_ANSWER_API_KEY'),
#                 "X-RapidAPI-Host": os.environ.get('WORDLE_ANSWER_API_HOST')
#             }
#         result = requests.get(f"{os.environ.get('WORDLE_ANSWER_API_URL')}/today", headers=headers).json()["today"]
#         if result == '':
#             return "?????"
#         return result
            
#     except Exception as err:
#         print(err)
#         return "?????"
    
def get_wordle():
    try:
        # Define the URL of the local HTML page (replace with your file path)
        url = "https://www.stockq.org/life/wordle-answers.php#today"

        # Send an HTTP GET request to fetch the HTML content
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup

            soup = BeautifulSoup(response.text, 'html.parser')
            soup_text = soup.get_text()
            today = datetime.date.today()
            index = soup_text[:].find(f'{today.year}/{today.month}/{today.day}')
            wordle = soup_text[index: index + 22].split(' ')[2]
            return wordle
    
        else:
            print("Failed to fetch the local HTML page. Status code:", response.status_code)
            return "?????"

    except Exception as err:
        print(err)
        return "?????"

