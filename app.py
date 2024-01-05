import datetime
from flask import Flask, request, render_template
from dotenv import load_dotenv

import os

import sys

import logging

from validation.update_validation import is_valid_score_submission ,is_valid_signup_message

from context import get_wordle_number, get_wordle

from dbio import create_tables, get_record, get_all_records, insert_wordle_game, insert_player, insert_player_game, insert_season, insert_wordle_day, insert_player_score, update_record
from dbio import is_last_day_of_season, is_first_day_of_season, is_first_day_of_season, get_season_by_date, get_max_season, get_non_submittors, get_season_winners, get_season_scoreboard

from send_message import send_image, send_message

from img_gen import generate_scoreboard_image, get_scoreboard_html_and_css, get_total_scores

from routes import wordle_games_bp, seasons_bp, players_bp, player_games_bp, player_game_styles_bp, wordle_days_bp, player_scores_bp, scoreboards_bp

app = Flask(__name__)

app.register_blueprint(wordle_games_bp)
app.register_blueprint(seasons_bp)
app.register_blueprint(players_bp)
app.register_blueprint(player_games_bp)
app.register_blueprint(player_game_styles_bp)
app.register_blueprint(wordle_days_bp)
app.register_blueprint(player_scores_bp)

app.register_blueprint(scoreboards_bp)

load_dotenv()

# Set environment variables
env = os.getenv("ENV")
database = os.getenv("DATABASE")
chat_id = os.getenv("CHAT_ID")
season_length = os.getenv("SEASON_LENGTH")
crud_url = os.getenv("CRUD_URL")

create_tables(database)

if env == "PROD":
    # Prod environment
    print("Running in PROD")

elif env == "TEST":
    # Test environment
    print("Running in TEST")

    @app.post("/query")
    def query():
        return "Test"
    
    @app.get("/query")
    def get_query():
        return ""

else:
    #Dev environment
    print("Running in DEV")

# TODO: Update readme
# TODO: What would a first iteration of custom designs look like?

# TODO: Protect this route somehow?
# TODO: Test Dealing with tuples in html
# TODO: fix all routes and /database elements if required. Also add new tables to routes
@app.get("/database")
def database_page():
    record_types = ['wordle_games', 'seasons', 'players', 'player_games', 'player_game_styles', 'wordle_days', 'player_scores']
    data = { "data":[ {"name": record_type, "record":record_tuples_to_list(get_all_records(database, record_type))} for record_type in record_types], "url": crud_url }
    return render_template('admin_dashboard.html', data=data)

# TODO: Make this a util function or do it inside get_all_records
def record_tuples_to_list(records):
    list_records = []
    for record in records[0]:
        list_records.append(list(record))
    return list_records, records[1]



@app.get("/")
def main_page():
    wordle_games = [game_record[0] for game_record in get_all_records(database, 'wordle_games')[0]]
    data = {
        "wordle_games": wordle_games,
        "crud_url": crud_url
    }
    return render_template('game_select.html', data=data)


@app.post("/")
def receive_update():
    # Here we handle incoming "Update" objects from Telegram
    # These are messages our bot is aware of.

    today = datetime.date.today()

    print("Message received:", request.json)
    ########
    # Message validation
    # If this is a valid wordle submission for today,
    # move on to wordle_game validation
    ######## 
    if is_valid_score_submission(request.json):
        player_id = request.json["message"]["from"]["id"]
        player_name = request.json["message"]["from"]["first_name"]
        text = request.json["message"]["text"]
        chat_id = request.json["message"]["chat"]["id"]
        score = text[text.index("/") - 1]
        if score == 'X':
            score = 7
        score = int(score)

        print(f"Message received {today}:")
        print(f"Chat:{chat_id}")
        print(f"From: {player_name}:{player_id}")
        print(f"Text: {text}")
        print(f"Score: {score}\n")

        #########
        # WORDLE_GAME validation
        # If there is no wordle_game based on this chat_id,
        # create one. Otherwise move to player validation
        #########
        print("Checking if wordle_game exists for this chat")
        wordle_game_record = get_record(database, 'wordle_games', ['id'], [chat_id])
        if wordle_game_record == None:
            wordle_game_record = insert_wordle_game(database, chat_id)
            print(f"Wordle_game {wordle_game_record[0]} created")
        else:
            print(f"Wordle_game {wordle_game_record[0]} found")

        wordle_game_id = wordle_game_record[0]

        #########
        # PLAYER check
        # If there is no player record, create one. Otherwise move to player_game validation,
        # which ties a player to a wordle_game
        #########
        print(f"Checking for player {player_name}:{player_id} in database")
        player_record = get_record(database, 'players', ['id'], [player_id])
        if player_record == None:
            # This player is not in the players table yet, insert
            player_record = insert_player(database, player_id, player_name)
            print(f"Player {player_record[1]}:{player_record[0]} created")
        else:
            print(f"Player {player_record[1]}:{player_record[0]} found")

        player_id = player_record[0]


        #########
        # PLAYER_GAME check
        # If there is no player_game record, create one. Otherwise move to season validation.
        #########
        print(f"Checking for player_game with {player_name}:{player_id} and wordle_game {wordle_game_id} in database")
        player_game_record = get_record(database, 'player_games', ['player_id', 'wordle_game_id'], [player_id, wordle_game_id])
        if player_game_record == None:
            player_game_record = insert_player_game(database, player_id, wordle_game_id)
            print(f"Player_game {player_game_record[0]} created")
        else:
            print(f"Player_game {player_game_record[0]} found")

        player_game_id = player_game_record[0]

        #########
        # SEASON validation
        # If there is no current season, find the max season for this wordle_game 
        # and create the next season. If there is a season, move to wordle_day validation
        #########
        print("Checking for current season")
        season_record = get_season_by_date(database, today, wordle_game_id)
        if season_record == None:
            # There is no season with today in it yet
            print(f"No season found for {today} in wordle_game {wordle_game_id}")
            # Check if there is a max season to find the season number
            new_season_num = 1
            # If there is no latest season then the season to be created is season 1
            latest_season = get_max_season(database, wordle_game_id)
            if latest_season != None:
                # There is a latest season so the season to be created is 1 + the latest season number
                new_season_num = latest_season[1] + 1

            # Create a new season
            print(f"Season {new_season_num} for wordle_game {wordle_game_id} created")
            season_record = insert_season(database, new_season_num, today, today + datetime.timedelta(days=int(season_length) - 1), wordle_game_id)
        else:
            print(f"Season {season_record[0]} found")

        season_id = season_record[0]

        #########
        # WORDLE_DAY validation
        # If there is not a wordle_day yet, create one. If it is the same as yesterday's,
        # don't insert into the database
        #########
        print(f"Checking wordle_day for season {today}")
        wordle_day_record = get_record(database, 'wordle_days', ['date'], [ f"'{today}'"])
        if wordle_day_record == None:
            # There is no wordle_day for today yet
            wordle_day_record = insert_wordle_day(database, get_wordle(), get_wordle_number(today), today)
            print(f"Wordle_day {wordle_day_record[0]} created")
        else:
            # Check if the get_wordle is the same as previous day wordle_id, if so might need to run get_wordle again (if there is a prev day this season )
            last_wordle_day_record = get_record(database, 'wordle_days', ['date'], [f"'{today - datetime.timedelta(days=1)}'"])
            if last_wordle_day_record != None:
                if wordle_day_record[1] == last_wordle_day_record[1] or wordle_day_record[1] == '?????':
                    # Then the wordles are showing as the same for both days
                    # or today's is ????? so we can try to 
                    # call get_wordle() again and attempt to update today's wordle with the correct value
                    update_fields = ['word']
                    update_values = [f"'{get_wordle()}'"]

                    update_record(database, 'wordle_days', ['id'], [wordle_day_record[0]], update_fields, update_values)

        wordle_day_id = wordle_day_record[0]
        print(f"Continuing with wordle_day {wordle_day_id}\n")


        #########
        # PLAYER_SCORE validation
        # If there is no player score for this day in this season for this player
        # insert one. Else don't override the current value. This means we only accept the first submission
        #########
        # Now in the database we have a player, a current season, and a wordle day
        # TODO: Should now include season_id to identify which season the player_score is in
        print(f"Making sure there is no player_score for {player_name}:{player_id} for {today} in season {season_id}")
        player_score_record = get_record(database, 'player_scores', ['wordle_day_id', 'player_id', 'season_id'], [wordle_day_id, player_id, season_id])
        if player_score_record == None:
            player_score_record = insert_player_score(database, score, wordle_day_id, player_id, season_id)
            print(f"Player score {player_score_record[0]} created")
        else:
            pass
            # There already exists a player_score entry, you can't override your submission
            # TODO: Give send message debug config so it doesnt try to send a message when in TEST
            #send_message(f"You already submitted today, {player_name}\n", wordle_game_id)
            print(f"Player_score {player_score_record[0]} found")

        player_score_id = player_score_record[0]

        #########
        # END OF SUBMISSIONS validation
        # If everyone has submitted and it's not the first day of the season 
        # then send the scoreboard. Don't send if it's the first day of the season.
        #########
        # Check if everyone has submitted
        print("Checking if everyone has submitted now")
        non_submittors = get_non_submittors(database, wordle_day_id, season_id, wordle_day_id)
        if len(non_submittors) == 0:
            # Everyone has submitted
            print(f"All players in season {season_id} submitted. Making sure it isn't the first day of the season")
            is_first_day = is_first_day_of_season(database, season_id, today)

            if not is_first_day:
                print("It's not the first day of the season so sending scoreboard for today")
                send_image(generate_scoreboard_image(database, wordle_game_id, season_id), wordle_game_id)    
            else:
                print("It is the first day of the season so the scoreboard will not be sent")  
                pass      

            print(f"Checking if today is the last day of the season")
            if is_last_day_of_season(database, season_id, today):
                # Today is the last day in the season
                print("It is the last day of the season, sending congratulatory message")
                send_message(f"Congrats on winning, {' and '.join(get_season_winners(database, season_id))}", wordle_game_id)
            else:
                print("It's not the last day of the season so we're done here.")
        else:
            print(f"Oh shit, these players didnt submit yet: {str(non_submittors)}")
    return "Processed"

@app.get("/day_end")
def day_end():
    # This runs at the very START of each day technically but the purpose is to close out the previous wordle_day
    # and potentially the season. 

    # Yesterday is the day we are closing. It is 12am of the next day at this point
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    # TODO: Add all the logs and test this like crazy
    print(f"Closing all the games for {yesterday}")
    for wordle_game in get_all_records(database, "wordle_games")[0]:
        if len(wordle_game) > 0:
            wordle_game_id = wordle_game[0]
            # TODO: These will be the same, similar to how players id is the telegram user id
            print(f"Closing wordle_game {wordle_game_id}")
            # There should be one, but if for some reason not, check if there is a season for yesterday
            print(f"Checking if there was a season for yesterday")
            yesterday_season_record = get_season_by_date(database, yesterday, wordle_game_id)
            if yesterday_season_record == None:
                # There is no season with yesterday in it yet
                print("There wasn't a season yesterday, its fine dont have to do anything.")
                break

            yesterday_season_id = yesterday_season_record[0]

            print(f"Continuing with season_id {yesterday_season_id}")
            # Check if there is a current wordle_day for yesterday
            # This covers the event that no one submitted the whole day, 
            # thus no wordle_day entry was created.
            print("Checking if there was a wordle_day for yesterday")
            yesterday_wordle_day_record = get_record(database, 'wordle_days', ['date'], [f"'{yesterday}'"])
            if yesterday_wordle_day_record == None:
                print("No wordle day found, inserting the record. Won't be able to find the wordle word")
                # There is no wordle_day for yesterday yet 
                # Can't get wordle for yesterday so leave as ?????
                yesterday_wordle_day_record = insert_wordle_day(database, "?????", get_wordle_number(yesterday), yesterday)

            yesterday_wordle_day_id = yesterday_wordle_day_record[0]
            print(f"Continuing with wordle_day {yesterday_wordle_day_id}\n")

            # Check if everyone submitted yesterday
            print(f"Checking if anyone in wordle_game {wordle_game_id} didnt submit yesterday")
            non_submittors = get_non_submittors(database, yesterday_wordle_day_id, yesterday_season_id, wordle_game_id)

            for non_submittor in non_submittors:
                print(f"Oh shit, {non_submittor[1]} didnt submit, giving score of 8")
                insert_player_score(database, 8, yesterday_wordle_day_id, non_submittor[0], yesterday_season_id)

            # 8's have been supplied
            # Don't send the scoreboard if there where no non-submittors 
            # Or if there where no non-submittors and its the first day, send the scoreboard
            # This is confusing and could be a OR but it's separated for readability and logical differences in conditions
            was_first_day = is_first_day_of_season(database, yesterday_season_id, yesterday)
            print("Checking if it was the first day of the season that just ended.")
            if was_first_day:
                print("It was the first day of the season, sending scoreboard")
                # It is the end of the first day so we have to send scoreboard regardless of how many people submitted
                image = generate_scoreboard_image(database, wordle_game_id, yesterday_season_id)
                send_image(image, wordle_game_id)
            elif len(non_submittors) > 0:
                print("It wasnt the first day of the season but some people didnt submit, sending the scoreboard")
                # It's not the first day and at least 1 person didnt submit so we have to send the scoreboard
                image = generate_scoreboard_image(database, wordle_game_id, yesterday_season_id)
                send_image(image, wordle_game_id)
            else:
                # It is not the end of the first day and everyone submitted, so the last submission yesterday
                # would have sent the scoreboard
                print("It wasn't the first day of the season and everyone submitted so not sending scoreboard because it should have already sent")
                pass
            
            print("Checking if it's the last day of the season")
            if is_last_day_of_season(database, yesterday_season_id, yesterday) and len(non_submittors) > 0:
                # Yesterday was the last day in the season
                print("It was the last day of the season, sending congrats to everyone who won")
                message = f"Congrats on winning, {' and '.join(get_season_winners(database, yesterday_season_id))}"
                send_message(message, wordle_game_id)

    return "Done"#(images, messages)

if __name__== "__main__":
    app.run(host='0.0.0.0', port=5000)

