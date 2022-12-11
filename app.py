from flask import Flask, request
from GameRecord import GameRecord

import requests

import os

from ProcessedUpdate import ProcessedUpdate

from openpyxl import load_workbook

import Context

import datetime

from dotenv import load_dotenv

load_dotenv()

from ScheduledFunctions import record_todays_wordle

# Create a game record, which inits using json file (maybe) and generates season json
# files (maybe) and season config json files

app = Flask(__name__)

game_record = GameRecord()

@app.get("/record_wordle")
def record_wordle():
    return record_todays_wordle()
    


@app.get("/day_end")
def send_scoreboard():
    # Assumes the day is over, finds the day's wordle, assigns 8s for unsubmitted players, and sends the scorebord 
    word = Context.get_todays_wordle()
    game_record.get_current_season().insert_wordle(word, datetime.date.today())
    game_record.close_day()
    game_record.write_seasons()

    game_record.generate_leaderboard_img(current_season, os.environ.get("JPG_FILE_NAME"))
    # Send image
    payload = {'chat_id': os.environ.get('CHAT_ID')}
    files = {'photo': open('latest_season.jpg', 'rb')}
    requests.post(f"{os.environ.get('BOT_URL')}/sendPhoto", files=files, data=payload )

@app.get("/current_season")
def current_season():
    return str(game_record.get_current_season())

@app.get("/all_seasons")
def all_seasons():
    season_strings = ""
    for season in game_record.seasons:
        print(season)
        season_strings = season_strings + str(game_record.seasons[season])
    return season_strings

@app.post("/test_update")
def test_update():
    return str(ProcessedUpdate(request.json))

@app.get("/test_general")
def test_general():
    return Context.get_todays_wordle()

@app.post("/")
def process_update():

    # TODO: (Future updates) Use this logic to determine tile colours
    # print(type(data))
    # string = data['message']['text']
    # print(string)
    # for char in string:
    #     print(char + str(ord(char)))

    update = request.json
    #ASSUMPTION: this is any type of update object: https://core.telegram.org/bots/webhooks#testing-your-bot-with-updates
    processed_update  = ProcessedUpdate(update)

    today = datetime.date.today()

    if processed_update.is_todays_wordle():
        current_season = game_record.get_current_season()

        # Check if there is a current season
        # if not, create it using season number in season_index.txt + 1
        # then set the current season to that one

        if current_season == False:
            season_num = 1
            with open('seasons/season_index.txt') as f:
                season_num = int(f.read())

            # Method creates the season, writes json, and updates season_index.txt
            game_record.generate_season(today, today + datetime.timedelta(days=os.environ.get("SEASON_LENGTH_DAYS")), season_num + 1)
            current_season = game_record.get_current_season()


        # Now there is a current season, we can insert the score
        game_record.insert_score(current_season, processed_update.name, processed_update.score, today)

        # Check if everyone has submitted
        if current_season.all_submitted_on(today):

            # Make sure the day hasnt changed since getting the request
            word = Context.get_todays_wordle()
            game_record.get_current_season().insert_wordle(word, datetime.date.today())
            game_record.write_seasons()
            
            
            game_record.generate_leaderboard_img(current_season, os.environ.get("JPG_FILE_NAME"))
            # Send image
            payload = {'chat_id': os.environ.get('CHAT_ID')}
            files = {'photo': open('latest_season.jpg', 'rb')}
            requests.post(f"{os.environ.get('BOT_URL')}/sendPhoto", files=files, data=payload )


        return processed_update.return_message + " It has been inserted into the scoreboard."

    elif processed_update.chat_id == os.environ.get("CHAT_ID") and processed_update.is_reply_to('153'):

        payload = {'chat_id': os.environ.get('CHAT_ID'), 'text': str(update)}
        #print(requests.post(f"{os.environ.get('BOT_URL')}/sendMessage", data=payload).json()['result']['message_id'])
        return str(vars(processed_update))

    else:
        return "" 



    #TODO: Later updates (if possible to process emojis, generate comments and send fun messages back)

    #return leaderboard_html

