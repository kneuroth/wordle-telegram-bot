import dbio

import os
import datetime
import random
import string

from dotenv import load_dotenv


if __name__ == "__main__":

    load_dotenv()


    # Set environment variables
    env = os.getenv("ENV")
    database = os.getenv("DATABASE")
    chat_id = os.getenv("CHAT_ID")
    season_length = os.getenv("SEASON_LENGTH")


    dbio.create_tables(database)

    today = datetime.date.today()

    # app.py has ran already so assume tables exist but have nothing in them
    wordle_game_record = dbio.insert_wordle_game(database, int(os.getenv("CHAT_ID")))

    season = dbio.insert_season(database, 1, today - datetime.timedelta(days=15), today + datetime.timedelta(days=14), 1)

    geoffrey = dbio.insert_player(database, 45127117, 'Geoffrey', 1)
    kelly = dbio.insert_player(database, 32420099, 'Kelly', 1)

    players = [geoffrey, kelly]

    for i in range(14):
        wordle_day = dbio.insert_wordle_day(database, ("").join(random.choices(string.ascii_uppercase, k=5)), 100 + i, today - datetime.timedelta(days=15) + datetime.timedelta(days=i), 1)
        for player in players:
            dbio.insert_player_score(database, random.choice([1, 2, 3, 4, 5, 6, 7, 8]), wordle_day[0], player[0])

    print('Done writing setup')