import datetime
from flask import Flask, request, render_template
from dotenv import load_dotenv

import os

import sys

from validation.update_validation import is_valid_score_submission ,is_valid_signup_message

from context import get_wordle_number, get_wordle

from dbio import create_tables, get_record, get_all_records, insert_wordle_game, insert_player, insert_season, insert_wordle_day, insert_player_score, update_record
from dbio import is_last_day_of_season, is_first_day_of_season, is_first_day_of_season, get_season_by_date, get_max_season, get_non_submittors, get_season_winners

from send_message import send_image, send_message

from img_gen import generate_scoreboard_image, get_scoreboard_html_and_css

from routes import wordle_games_bp, seasons_bp, players_bp, wordle_days_bp, player_scores_bp

app = Flask(__name__)

app.register_blueprint(wordle_games_bp)
app.register_blueprint(seasons_bp)
app.register_blueprint(players_bp)
app.register_blueprint(wordle_days_bp)
app.register_blueprint(player_scores_bp)

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

# Get the current wordle_game (tuple)
wordle_game_record = get_record(database, 'wordle_games', ['chat_id'], [chat_id])

if wordle_game_record == None:
    # There is no wordle_game for this chat_id, so create one
    wordle_game_record = insert_wordle_game(database, int(os.getenv("CHAT_ID")))

wordle_game_id = wordle_game_record[0]

# Create interactive database access tool right here.
# TODO: FIgure out if I can call python functions from this render_template, then if so
# add CRUD features, Create, Read, Update, Delete

# TODO: Protect this route somehow?
@app.get("/database")
def database_page():
    record_types = ['wordle_games', 'seasons', 'players', 'wordle_days', 'player_scores']
    data = { "data":[ {"name": record_type, "record":get_all_records(database, record_type)} for record_type in record_types], "url": crud_url }
    return render_template('admin_dashboard.html', data=data)


@app.get("/")
def main_page():
    latest_season = get_max_season(database, wordle_game_id)
    if latest_season != None:
        # There is a latest season so return the scoreboard for that season
        return get_scoreboard_html_and_css(database, latest_season[0])[0]
    else:
        return "No seasons yet!"

@app.post("/")
def receive_update():
    # Here we handle incoming "Update" objects from Telegram
    # These are messages our bot is aware of.

    if is_valid_score_submission(request.json):
        # Message to bot is from the right chat and is a valid wordle submission for today

        # Init useful variables to control game logic
        player_id = request.json["message"]["from"]["id"]
        player_name = request.json["message"]["from"]["first_name"]
        text = request.json["message"]["text"]
        score = text[text.index("/") - 1]
        if score == 'X':
            score = 7
        score = int(score)
        today = datetime.date.today()

        player_record = get_record(database, 'players', ['id'], [player_id])
        if  player_record == None:
            # This player is not in the players table yet, insert
            player_record = insert_player(database, player_id, player_name, wordle_game_id)
        
        # Check if there is a current season
        season_record = get_season_by_date(database, today, wordle_game_id)
        if season_record == None:
            # There is no season with today in it yet

            # Check if there is a max season to find the season number
            new_season_num = 1
            # If there is no latest season then the season to be created is season 1
            latest_season = get_max_season(database, wordle_game_id)
            if latest_season != None:
                # There is a latest season so the season to be created is 1 + the latest season number
                new_season_num = latest_season[4] + 1

            # Create a new season
            season_record = insert_season(database, new_season_num, today, today + datetime.timedelta(days=int(season_length)), wordle_game_id)
            
        season_id = season_record[0]

        # Check if there is a current wordle_day for today
        wordle_day_record = get_record(database, 'wordle_days', ['season_id', 'date'], [season_id, f"'{today}'"])
        if wordle_day_record == None:
            # There is no wordle_day for today yet
            wordle_day_record = insert_wordle_day(database, get_wordle(), get_wordle_number(today), today, season_id)

        wordle_day_id = wordle_day_record[0]

        # Now in the database we have a player, a current season, and a wordle day
        player_score_record = get_record(database, 'player_scores', ['wordle_day_id', 'player_id'], [wordle_day_id, player_id])
        if player_score_record == None:
            player_score_record = insert_player_score(database, score, wordle_day_id, player_id)

        else:
            # There already exists a player_score entry, you can't override your submission
            # TODO: Send message saying you can't do that
            pass
            # ALTERNATE UNIVERSE: There already exists a player_score entry, modify it with the new score
            # player_score_id = player_score_record[0]
            # player_score_record = update_record(database, 'player_scores', ['id'], [player_score_id], ['score'], [score])
        
        # Check if everyone has submitted
        non_submittors = get_non_submittors(database, wordle_day_id)
        if len(non_submittors) == 0:
            # Everyone has submitted
            is_first_day = is_first_day_of_season(database, season_id, today)

            if not is_first_day:
                send_image(generate_scoreboard_image(database, season_id))            

            if is_last_day_of_season(database, season_id, today):
                # Today is the last day in the season
                send_message(f"Congrats on winning, {' and '.join(get_season_winners(database, season_id))}")

    elif is_valid_signup_message(request.json):
        player_id = request.json["message"]["from"]["id"]
        player_name = request.json["message"]["from"]["first_name"]

        player_record = get_record(database, 'players', ['id'], [player_id])
        if  player_record == None:
            # This player is not in the players table yet, insert
            player_record = insert_player(database, player_id, player_name, wordle_game_id)
            send_message(f"Welcome to the game, {player_name}")

    return "Processed"

@app.get("/day_end")
def day_end():
    # This runs at the very START of each day technically but the purpose is to close out the previous wordle_day
    # and potentially the season. 

    # Yesterday is the day we are closing. It is 12am of the next day at this point
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    # There should be one, but if for some reason not, check if there is a season for yesterday
    yesterday_season_record = get_season_by_date(database, yesterday, wordle_game_id)
    if yesterday_season_record == None:
        # There is no season with yesterday in it yet

        # Check if there is a max season to find the season number
        new_season_num = 1
        latest_season = get_max_season(database, wordle_game_id)
        if latest_season != None:
            # There is a latest season so the season to be created is season 1 + latest season number
            new_season_num = latest_season[4] + 1

        # Create a new season
        yesterday_season_record = insert_season(database, new_season_num, yesterday, yesterday + datetime.timedelta(days=int(season_length)), wordle_game_id)

    yesterday_season_id = yesterday_season_record[1]

    # Check if there is a current wordle_day for yesterday
    # This covers the event that no one submitted the whole day, 
    # thus no wordle_day entry was created.
    yesterday_wordle_day_record = get_record(database, 'wordle_days', ['season_id', 'date'], [yesterday_season_id, f"'{yesterday}'"])
    if yesterday_wordle_day_record == None:
        # There is no wordle_day for yesterday yet 
        # Can't get wordle for yesterday so leave as ?????
        yesterday_wordle_day_record = insert_wordle_day(database, "?????", get_wordle_number(yesterday), yesterday, yesterday_season_id)

    yesterday_wordle_day_id = yesterday_wordle_day_record[0]

    # Check if everyone submitted yesterday
    non_submittors = get_non_submittors(database, yesterday_wordle_day_id)

    for non_submittor in non_submittors:
        insert_player_score(database, 8, yesterday_wordle_day_id, non_submittor[0])

    # 8's have been supplied
    # Don't send the scoreboard if there where no non-submittors 
    # Or if there where no non-submittors and its the first day, send the scoreboard
    # This is confusing and could be a OR but it's separated for readability and logical differences in conditions
    was_first_day = is_first_day_of_season(database, yesterday_season_id, yesterday)
    if was_first_day:
        # It is the end of the first day so we have to send scoreboard regardless of how many people submitted
        send_image(generate_scoreboard_image(database, yesterday_season_id))
    elif len(non_submittors) > 0:
        # It's not the first day and at least 1 person didnt submit so we have to send the scoreboard
        send_image(generate_scoreboard_image(database, yesterday_season_id))
    else:
        # It is not the end of the first day and everyone submitted, so the last submission yesterday
        # would have sent the scoreboard
        pass

    if is_last_day_of_season(database, yesterday_season_id, yesterday) and len(non_submittors) > 0:
        # Yesterday was the last day in the season
        send_message(f"Congrats on winning, {' and '.join(get_season_winners(database, yesterday_season_id))}")

    return "End"

if __name__== "__main__":
    app.run(host='0.0.0.0', port=5000)

