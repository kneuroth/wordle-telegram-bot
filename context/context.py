import datetime
import re
import os
import requests
from bs4 import BeautifulSoup

def get_wordle_number(date: datetime.date):
    # Maps Wordle number 505 to Nov 6, 2022 (arbitrarily selected)
    delta = int(re.split(' days|:| day,', str(date - datetime.date(2022, 11, 6)))[0])
    return delta + 505
    
def get_wordle():
    try:
        # Define the URL of the local HTML page (replace with your file path)
        today = datetime.date.today()
        url = f"https://www.nytimes.com/svc/wordle/v2/{today.year}-{today.month}-{today.day}.json"

        # Send an HTTP GET request to fetch the HTML content
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            return str(response.json()["solution"]).upper()
    
        else:
            print("Failed to fetch the local HTML page. Status code:", response.status_code)
            return "?????"

    except Exception as err:
        print(err)
        return "?????"

