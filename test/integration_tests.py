# TO RUN INDIVIDUAL TEST CASES:
# python test/integration_tests.py <ClassName> <test_case_method>
# TO RUN ALL TESTS:
# python text/integration_tests.py

import datetime
import unittest
import os
from dotenv import load_dotenv
import requests
import sys

from context import get_wordle, get_wordle_number
from dbio import insert_wordle_game, insert_player, insert_player_game, insert_season, insert_wordle_day, insert_player_score, get_records, get_record, is_first_day_of_season, get_season_by_date, get_max_season, update_record, get_non_submittors, get_season_scoreboard, get_season_winners, get_all_records
from dbio.schema import create_tables, drop_tables

load_dotenv()

DATABASE = os.getenv("DATABASE")
CRUD_URL = os.getenv("CRUD_URL")
SEASON_LENGTH = os.getenv("SEASON_LENGTH")

# Use this as base update template
# MUST update:
# message.from.id
# message.from.first_name
# message.chat.id
# message.text
def alter_base_update(from_id: int, from_first_name: str, chat_id: int, text: str):
    return {
    "update_id": 123,
    "message": {
        "message_id": 123,
        "from": {
            "id": from_id,
            "first_name": from_first_name,
            "last_name": "Lnam"
        },
        "chat": {
            "id": chat_id,
            "title": "Fakechat",
            "type": "Private"
            },
        "date": 8999999,
        "text": text
    }
}

record_types = ["wordle_games", "seasons", "players", "player_games", "wordle_days", "player_scores"]
record_fields = {
    "wordle_games": [
        "id"
    ], 
    "seasons": [
        "id",
        "season_number",
        "start_date",
        "end_date",
        "wordle_game_id"
    ],
    "players": [
        "id",
        "name"
    ],
    "player_games": [
        "id", 
        "player_id", 
        "wordle_game_id"
    ],
    "wordle_days":[
        "id",
        "word",
        "wordle_number",
        "date"
    ], 
    "player_scores": [
        "id", 
        "score", 
        "wordle_day_id", 
        "player_id", 
        "season_id"
    ]
}

# app.py should be running in local before running these test cases
# All tests simulate a user sending the bot a message from telegram

# Most of the following should at least get test cases for:
# First player to submit
# Middle player to submit
# Last player to submit
# day_end call first day
# day_end call when 1 person submitted first day, non-last day, and last day
# day_end call when no people submitted first day, non-last day, and last day
# All above repeated but SAME player (player_id and name the same) but in 2 different wordle_games

class TestDatabaseStateEmpty(unittest.TestCase):
    """
    Tests that run with the database completely empty
    Test cases are self-documenting
    """

    def setUp(self):
        # Runs before each test case
        drop_tables(DATABASE)
        os.remove(DATABASE)
        create_tables(DATABASE)

    def tearDown(self):
        # Runs after each test case
        drop_tables(DATABASE)
        os.remove(DATABASE)

    def test_bad_wordle_number(self):
        # Description: A player submits with a wordle number different from the worlde_number of the day
        # Expecting: Still enpty database
        body = alter_base_update(123, "Kelly", 111, "Wordle 123 4/6")
        requests.post(f"{CRUD_URL}", json=body)
        [self.assertEqual(get_all_records(DATABASE, record_type), ([], record_fields[record_type])) for record_type in record_types]

    def test_bad_text_string(self):
        # Description: A player submits with poorly formatted text
        # Expecting: Still empty database 
        today = datetime.date.today()
        body = alter_base_update(123, "Kelly", 111, f"Wordle: {get_wordle_number(today)} 5/6")
        requests.post(f"{CRUD_URL}", json=body)
        [self.assertEqual(get_all_records(DATABASE, record_type), ([], record_fields[record_type])) for record_type in record_types]

    def test_good_submission(self):
        # Description: A player submits with correct wordle_number and formatted text
        # Expecting: New wordle_game, season, player, player_game, wordle_day, and player_score to 
        # be inserted into the database
        today = datetime.date.today()
        player_id = 123
        player_name = "Kelly"
        wordle_game_id = 111
        score = 5
        text = f"Wordle {get_wordle_number(today)} {score}/6"
        body = alter_base_update(player_id, player_name, wordle_game_id, text)

        requests.post(f"{CRUD_URL}", json=body)

        expected_results = {
            "wordle_games": ([(wordle_game_id,)], ['id']),
            "seasons": ([(1, 1, str(today), str(today + datetime.timedelta(days=(int(SEASON_LENGTH) - 1))), wordle_game_id)], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([(player_id, 'Kelly')], ['id', 'name']), 
            "player_games": ([(1, player_id, wordle_game_id)], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": ([(1, get_wordle(), get_wordle_number(today), str(today))], ['id', 'word', 'wordle_number', 'date']),
            "player_scores": ([(1, score, 1, player_id, 1)], ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])

    def test_day_end_call(self):
        requests.get(f"{CRUD_URL}/day_end")
        # Expecting empty database still
        [self.assertEqual(get_all_records(DATABASE, record_type), ([], record_fields[record_type])) for record_type in record_types]

    def test_no_submit_day_end(self):
        # Test calling day_end the day after no person submits
        # This wouldnt happen in real life because a game only starts when someone sends a valid score
        # but it still tests day_end functionality when no one has submitted
        today = datetime.date.today()
        wordle_game = insert_wordle_game(DATABASE, 111)
        season = insert_season(DATABASE, 1, today - datetime.timedelta(days=1), today + datetime.timedelta(days=int(SEASON_LENGTH) - 1), wordle_game[0])
        player = insert_player(DATABASE, 123, "Kelly")
        player_game = insert_player_game(DATABASE, player[0], wordle_game[0]) 
        wordle_day = insert_wordle_day(DATABASE, "YSTRD", 456, today - datetime.timedelta(days=1))

        requests.get(f"{CRUD_URL}/day_end")

        # Check if scoreboard file exists
        # Expecting no scoreboard to have been sent
        self.assertEqual(os.path.isfile(f"scoreboard-{today}-{111}-S{1}.png"), True )

    def test_one_submit_day_end(self):
        # Test calling day_end the day after one person submits and makes a wordle_game
        # Scoreboard should be sent because it is the only player in the game that submitted
        today = datetime.date.today()
        wordle_game = insert_wordle_game(DATABASE, 111)
        season = insert_season(DATABASE, 1, today - datetime.timedelta(days=1), today + datetime.timedelta(days=int(SEASON_LENGTH) - 1), wordle_game[0])
        player = insert_player(DATABASE, 123, "Kelly")
        player_game = insert_player_game(DATABASE, player[0], wordle_game[0]) 
        wordle_day = insert_wordle_day(DATABASE, "YSTRD", 456, today - datetime.timedelta(days=1))
        player_score = insert_player_score(DATABASE, 3, wordle_day[0], player[0], season[0])

        requests.get(f"{CRUD_URL}/day_end")

        # Check if scoreboard file exists
        # Expecting no scoreboard to have been sent
        self.assertEqual(os.path.isfile(f"scoreboard-{today}-{111}-S{1}.png"), True )        

    def test_one_of_two_submits_day_end(self):
        # Test calling day_end the day after one person submits and makes a wordle_game
        # Scoreboard should be sent because it is the only player in the game that submitted
        today = datetime.date.today()
        wordle_game = insert_wordle_game(DATABASE, 111)
        season = insert_season(DATABASE, 1, today - datetime.timedelta(days=1), today + datetime.timedelta(days=int(SEASON_LENGTH) - 1), wordle_game[0])
        playerK = insert_player(DATABASE, 123, "Kelly")
        playerA = insert_player(DATABASE, 456, "Anna")
        player_gameK = insert_player_game(DATABASE, playerK[0], wordle_game[0]) 
        player_gameA = insert_player_game(DATABASE, playerA[0], wordle_game[0])
        wordle_day = insert_wordle_day(DATABASE, "YSTRD", 456, today - datetime.timedelta(days=1))
        player_score = insert_player_score(DATABASE, 3, wordle_day[0], playerK[0], season[0])

        requests.get(f"{CRUD_URL}/day_end")

        # Check if scoreboard file exists
        # Expecting no scoreboard to have been sent
        self.assertEqual(os.path.isfile(f"scoreboard-{today}-{111}-S{1}.png"), True )        

class TestDatabaseStateOnePrevGame(unittest.TestCase):

    def setUp(self):
        # Runs before each test case
        drop_tables(DATABASE)
        os.remove(DATABASE)
        create_tables(DATABASE)

        self.init_wordle_game = insert_wordle_game(DATABASE, 111)
        self.init_player = insert_player(DATABASE, 123, "Kelly")
        self.init_player_game = insert_player_game(DATABASE, 123, 111)

        self.init_first_day = datetime.date.today() - datetime.timedelta(days=int(SEASON_LENGTH))
        self.init_last_day = datetime.date.today() - datetime.timedelta(days=1)

        self.init_season = insert_season(DATABASE, 1, self.init_first_day, self.init_last_day, self.init_wordle_game[0])
        self.init_wordle_days = []
        self.init_player_scores = []
        # FOr as many days are in the season, insert a wordle_day and a player_score for Kelly
        for day in range((self.init_last_day - self.init_first_day).days + 1):

            wordle_day = insert_wordle_day(DATABASE, "NOMTR", get_wordle_number(datetime.date.today()), datetime.date.today() - datetime.timedelta(days=int(SEASON_LENGTH) - day) )
            self.init_wordle_days.append(wordle_day)
            self.init_player_scores.append(insert_player_score(DATABASE, 5, wordle_day[0], self.init_player[0], self.init_season[0]))


    def tearDown(self):
        # Runs after each test case
        #drop_tables(DATABASE)
        #os.remove(DATABASE)
        pass

    def test_bad_wordle_number(self):
        body = alter_base_update(123, "Kelly", 111, "Wordle 123 4/6")
        requests.post(f"{CRUD_URL}", json=body)

        expected_results = {
            "wordle_games": ([self.init_wordle_game], ['id']),
            "seasons": ([self.init_season], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([self.init_player], ['id', 'name']), 
            "player_games": ([self.init_player_game], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": (self.init_wordle_days, ['id', 'word', 'wordle_number', 'date']),
            "player_scores": (self.init_player_scores, ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])
    
    def test_bad_text_string(self):
        today = datetime.date.today()
        body = alter_base_update(123, "Kelly", 111, f"Wordle: {get_wordle_number(today)} 5/6")
        requests.post(f"{CRUD_URL}", json=body)

        expected_results = {
            "wordle_games": ([self.init_wordle_game], ['id']),
            "seasons": ([self.init_season], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([self.init_player], ['id', 'name']), 
            "player_games": ([self.init_player_game], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": (self.init_wordle_days, ['id', 'word', 'wordle_number', 'date']),
            "player_scores": (self.init_player_scores, ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])
    
    def test_good_submission_same_game(self):
        today = datetime.date.today()
        player_id = 123
        player_name = "Kelly"
        wordle_game_id = self.init_wordle_game[0]
        score = 5
        text = f"Wordle {get_wordle_number(today)} {score}/6"
        body = alter_base_update(player_id, player_name, wordle_game_id, text)

        requests.post(f"{CRUD_URL}", json=body)

        expected_results = {
            "wordle_games": ([self.init_wordle_game], ['id']),
            "seasons": ([self.init_season] + [(2, 2, str(today), str(today + datetime.timedelta(days=(int(SEASON_LENGTH) - 1))), wordle_game_id)], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([self.init_player], ['id', 'name']), 
            "player_games": ([self.init_player_game], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": (self.init_wordle_days + [(31, get_wordle(), get_wordle_number(today), str(today))], ['id', 'word', 'wordle_number', 'date']),
            "player_scores": (self.init_player_scores + [(31, score, 31, player_id, 2)], ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])
    
    def test_good_submission_different_game(self):
        today = datetime.date.today()
        player_id = 123
        player_name = "Kelly"
        new_wordle_game_id = 777
        score = 5
        text = f"Wordle {get_wordle_number(today)} {score}/6"
        body = alter_base_update(player_id, player_name, new_wordle_game_id, text)

        requests.post(f"{CRUD_URL}", json=body)

        expected_results = {
            "wordle_games": ([self.init_wordle_game] + [(new_wordle_game_id, )], ['id']),
            "seasons": ([self.init_season] + [(2, 1, str(today), str(today + datetime.timedelta(days=(int(SEASON_LENGTH) - 1))), new_wordle_game_id)], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([self.init_player], ['id', 'name']), 
            "player_games": ([self.init_player_game] + [(2, player_id, new_wordle_game_id)], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": (self.init_wordle_days + [(31, get_wordle(), get_wordle_number(today), str(today))], ['id', 'word', 'wordle_number', 'date']),
            "player_scores": (self.init_player_scores + [(31, score, 31, player_id, 2)], ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])
    
    def test_good_submission_same_game_old_player_and_new_player(self):
        today = datetime.date.today()
        old_player_id = 123
        old_player_name = "Kelly"
        wordle_game_id = self.init_wordle_game[0]
        old_score = 5
        old_text = f"Wordle {get_wordle_number(today)} {old_score}/6"
        old_body = alter_base_update(old_player_id, old_player_name, wordle_game_id, old_text)

        requests.post(f"{CRUD_URL}", json=old_body)

        today = datetime.date.today()
        new_player_id = 891
        new_player_name = "Sammy"
        wordle_game_id = self.init_wordle_game[0]
        new_score = 6
        new_text = f"Wordle {get_wordle_number(today)} {new_score}/6"
        new_body = alter_base_update(new_player_id, new_player_name, wordle_game_id, new_text)

        requests.post(f"{CRUD_URL}", json=new_body)

        expected_results = {
            "wordle_games": ([self.init_wordle_game], ['id']),
            "seasons": ([self.init_season] + [(2, 2, str(today), str(today + datetime.timedelta(days=(int(SEASON_LENGTH) - 1))), wordle_game_id)], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([self.init_player] + [(new_player_id, new_player_name)], ['id', 'name']), 
            "player_games": ([self.init_player_game] + [(2, new_player_id, wordle_game_id)], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": (self.init_wordle_days + [(31, get_wordle(), get_wordle_number(today), str(today))], ['id', 'word', 'wordle_number', 'date']),
            "player_scores": (self.init_player_scores + [(31, old_score, 31, old_player_id, 2), (32, new_score, 31, new_player_id, 2)], ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])
    

    def test_good_submission_different_game_same_player_new_player(self):
        today = datetime.date.today()
        old_player_id = 123
        old_player_name = "Kelly"
        new_wordle_game_id = 777
        old_score = 5
        text = f"Wordle {get_wordle_number(today)} {old_score}/6"
        old_body = alter_base_update(old_player_id, old_player_name, new_wordle_game_id, text)

        today = datetime.date.today()
        new_player_id = 444
        new_player_name = "Shallom"
        new_wordle_game_id = 777
        new_score = 2
        text = f"Wordle {get_wordle_number(today)} {new_score}/6"
        new_body = alter_base_update(new_player_id, new_player_name, new_wordle_game_id, text)

        requests.post(f"{CRUD_URL}", json=new_body)
        requests.post(f"{CRUD_URL}", json=old_body)

        expected_results = {
            "wordle_games": ([self.init_wordle_game] + [(new_wordle_game_id, )], ['id']),
            "seasons": ([self.init_season] + [(2, 1, str(today), str(today + datetime.timedelta(days=(int(SEASON_LENGTH) - 1))), new_wordle_game_id)], ['id', 'season_number', 'start_date', 'end_date', 'wordle_game_id']),
            "players": ([self.init_player] + [(new_player_id, new_player_name)], ['id', 'name']), 
            "player_games": ([self.init_player_game] + [(2, new_player_id, new_wordle_game_id), (3, old_player_id, new_wordle_game_id)], ['id', 'player_id', 'wordle_game_id']),
            "wordle_days": (self.init_wordle_days + [(31, get_wordle(), get_wordle_number(today), str(today))], ['id', 'word', 'wordle_number', 'date']),
            "player_scores": (self.init_player_scores + [(31, new_score, 31, new_player_id, 2), (32, old_score, 31, old_player_id, 2)], ['id', 'score', 'wordle_day_id', 'player_id', 'season_id'])
        }

        self.assertEqual(get_all_records(DATABASE, "wordle_games"), expected_results["wordle_games"])
        self.assertEqual(get_all_records(DATABASE, "seasons"), expected_results["seasons"])
        self.assertEqual(get_all_records(DATABASE, "players"), expected_results["players"])
        self.assertEqual(get_all_records(DATABASE, "player_games"), expected_results["player_games"])
        self.assertEqual(get_all_records(DATABASE, "wordle_days"), expected_results["wordle_days"])
        self.assertEqual(get_all_records(DATABASE, "player_scores"), expected_results["player_scores"])
    
    def test_day_end(self):
        today = datetime.date.today()
        requests.get(f"{CRUD_URL}/day_end")
        # Expecting nothing to send because it should have sent yesterday already
        self.assertEqual(os.path.isfile(f"scoreboard-{today}-{self.init_wordle_game}-S{self.init_season}.png"), False )        

if __name__=="__main__":
    if os.getenv("ENV") in ["DEV", "TEST", "LOCAL"]:
        if len(sys.argv) <= 2:
            unittest.main()
        else:
            suite = unittest.TestSuite()
            suite.addTest(eval(sys.argv[1])(sys.argv[2]))
            unittest.TextTestRunner().run(suite)
    else:
        print("Do not run this in prod you will destroy the database and everything I love")