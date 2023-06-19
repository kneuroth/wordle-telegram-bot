import unittest
import datetime
import os

from dotenv import load_dotenv

import random
import string

project_path = os.path.abspath(os.path.dirname(__file__))
parent_path = os.path.abspath(os.path.join(project_path, os.pardir))

from validation import is_wordle_submission

from context import get_wordle_number, get_wordle

from img_gen import generate_scoreboard_image

from dbio import create_tables, drop_tables, insert_wordle_game, insert_player, insert_season, insert_wordle_day, insert_player_score,get_record, is_first_day_of_season, get_season_by_date, get_max_season, update_record, get_non_submittors, get_season_scoreboard, get_season_winners

from send_message import send_message, send_image

load_dotenv()

database = os.getenv("DATABASE")

class TestValidation(unittest.TestCase):
    def test_submission_scores(self):
        # Tests scores 0-7 with properly formatted Wordle submission
        # Expecting 0 and 7 to return False, all else should return True
        result = [is_wordle_submission(f"Wordle 5465 {i}/6") for i in range(0,8)]
        self.assertEqual(result, [False, True, True, True, True, True, True, False])

class TestContext(unittest.TestCase):
    def test_get_wordle_number(self):
        # Tests scores 0-7 with properly formatted Wordle submission
        # Expecting 0 and 7 to return False, all else should return True
        result = [get_wordle_number(datetime.date(2022, 1, i)) for i in range(1, 11)]
        result.append(get_wordle_number(datetime.date(2023, 3, 6)))
        self.assertEqual(result, [196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 625])

    def test_get_wordle(self):
        # Tests getting today's wordle from the api
        # Can't predict what the wordle will be but if it fails it will return '?????'
        result = get_wordle()
        print(f"Today's wordle is {result}")
        self.assertNotEqual('?????', result)

# class TestSendMessage(unittest.TestCase):
#     def test_send_message(self):
#         # See if received a text
#         send_message("Test")

    #def test_send_image(self):
        #send_image('scoreboard.png')

class TestDBIO(unittest.TestCase):
    def setUp(self):
        # Runs before each test case
        create_tables(database)

    def tearDown(self):
        # Runs after each test case
        drop_tables(database)
        os.remove(database)
    
    def test_insert_wordle_game(self):
        self.assertEqual((1, 1999), insert_wordle_game(database, 1999))

    def test_insert_season(self):
        self.assertEqual((1, 40, '2023-03-09', '2023-04-09', 1), insert_season(database, 40, datetime.date(2023, 3, 9), datetime.date(2023, 4, 9), 1))

    def test_insert_player(self):
        self.assertEqual((1999, 'Kelly', 1), insert_player(database, 1999, 'Kelly', 1))
    
    def test_insert_wordle_day(self):
        self.assertEqual((1, 'WORDLE', 400, '2023-03-09', 1), insert_wordle_day(database, 'WORDLE', 400, datetime.date(2023, 3, 9), 1))
 
    def test_player_score(self):
        self.assertEqual((1, 5, 1, 1999), insert_player_score(database, 5, 1, 1999))

    def test_get_record_player(self):
        # Insert a player to test with
        insert_player(database, -1999, 'Kelly', 1)
        self.assertEqual((-1999, 'Kelly', 1), get_record(database, 'players', ['id'], [-1999]))
    
    def test_get_record_wordle_day_by_date(self):
        # Insert a wordle_day to test with
        insert_wordle_day(database, 'WORDLE', 123, datetime.date(2023, 3, 9), 1)
        self.assertEqual((1, 'WORDLE', 123, '2023-03-09', 1), get_record(database, 'wordle_days', ['season_id', 'date'], [1, f"'{datetime.date(2023, 3, 9)}'"]))

    def test_get_record_error(self):
        self.assertEqual(None, get_record(database, 'wordle_games', ['chat_id'], [-100]))

    def test_get_season_by_date(self):
        # First insert 2 seasons to test with
        season1 = insert_season(database, 3, datetime.date(2023, 3, 9), datetime.date(2023, 4, 9), 1)
        season2 = insert_season(database, 4, datetime.date(2023, 4, 10), datetime.date(2023, 5, 10), 1)
        season3 = insert_season(database, 4, datetime.date(2023, 4, 10), datetime.date(2023, 5, 10), 2)

        # Set dates array. First 3 are in between season1 dates, 4th is 1 day before season1, 5th is between season2 dates, 6th is a year after season1
        dates = [datetime.date(2023, 3, 9), datetime.date(2023, 4, 9), datetime.date(2023, 3, 20), datetime.date(2023, 3, 8), datetime.date(2023, 4, 10), datetime.date(2024, 3, 20)]
        result = [get_season_by_date(database, date, 1) for date in dates]

        self.assertEqual([season1, season1, season1, None, season2, None], result)

    def test_get_max_season(self):
        # First insert 2 seasons to test with
        season1 = insert_season(database, 3, datetime.date(2023, 3, 9), datetime.date(2023, 4, 9), 1)
        season2 = insert_season(database, 4, datetime.date(2023, 4, 10), datetime.date(2023, 5, 10), 1)
        season3 = insert_season(database, 5, datetime.date(2023, 4, 10), datetime.date(2023, 5, 10), 2)
        
        self.assertEqual(season2, get_max_season(database, 1))

    def test_update_record(self):
        player_score = insert_player_score(database, 4, 1, 1999)
        player_score_id = player_score[0]
        
        new_player_score = update_record(database, 'player_scores', ['id'], [player_score_id], ['score'], [5])

        self.assertEqual((player_score_id, 5, 1, 1999), new_player_score )

    def test_get_non_submitors(self):
        # Create players to test with
        player1 = insert_player(database, 101, 'Player 1', 1)
        player2 = insert_player(database, 102, 'Player 2', 1)
        player3 = insert_player(database, 103, 'Player 3', 1)

        # Create wordle_day and extract the id
        wordle_day = insert_wordle_day(database, "WORDLE", 555, datetime.date(2023, 3, 10), 1)
        wordle_day_id = wordle_day[0]

        # Player1 is the only one to submit
        player1_score = insert_player_score(database, 5, 1, 101)



        self.assertEqual([player2, player3], get_non_submittors(database, wordle_day_id))

    def test_get_non_submittors_everyone_submitted(self):
                # Create players to test with
        player1 = insert_player(database, 101, 'Player 1', 1)
        player2 = insert_player(database, 102, 'Player 2', 1)
        player3 = insert_player(database, 103, 'Player 3', 1)

        # Create wordle_day and extract the id
        wordle_day = insert_wordle_day(database, "WORDLE", 555, datetime.date(2023, 3, 10), 1)
        wordle_day_id = wordle_day[0]

        # Player1, 2, and 3 subnmitted
        player1_score = insert_player_score(database, 5, 1, 101)
        player1_score = insert_player_score(database, 3, 1, 102)
        player1_score = insert_player_score(database, 2, 1, 103)

        self.assertEqual([], get_non_submittors(database, wordle_day_id))

    # def test_get_season_scoreboard(self):
    #     # Will also generate the html scoreboard, but not test it, per say
    #     # Create players to test with
    #     player1 = insert_player(database, 1, 'Player 1', 1)
    #     player2 = insert_player(database, 2, 'Player 2', 1)
    #     player3 = insert_player(database, 3, 'Player 3', 1)

    #     today = datetime.date.today()

    #     one_day_delta = datetime.timedelta(days=1)
    #     two_day_delta = datetime.timedelta(days=2)
    #     three_day_delta = datetime.timedelta(days=3)


    #     season1 = insert_season(database, 1, today, today + one_day_delta, 1)
    #     season2 = insert_season(database, 2, today + two_day_delta, today + three_day_delta, 1)

    #     wordle_day_S1_D1 = insert_wordle_day(database, "FIRST", 100, today, season1[0] )
    #     wordle_day_S1_D2 = insert_wordle_day(database, "SECND", 101, today + one_day_delta, season1[0])
    #     wordle_day_S2_D1 = insert_wordle_day(database, "THIRD", 102, today + two_day_delta, season2[0] )
    #     wordle_day_S2_D2 = insert_wordle_day(database, "FORTH", 103, today + three_day_delta, season2[0])


    #     for wordle_day in [wordle_day_S1_D1, wordle_day_S1_D2, wordle_day_S2_D1, wordle_day_S2_D2]:
    #         for player in [player1, player2, player3]:
    #             insert_player_score(database, player[0], wordle_day[0], player[0])

    #     generate_scoreboard_image(database, season1[0])

    #    self.assertEqual(([(str(today), 100, 'FIRST', 1, 2, 3), (str(today + one_day_delta), 101, 'SECND', 1, 2, 3)], ['date', 'wordle_number', 'word', 'Player 1', 'Player 2', 'Player 3']), get_season_scoreboard(database, season1[0]))

    def test_get_season_winner(self):
        # Create players to test with
        player1 = insert_player(database, 1, 'Player 1', 1)
        player2 = insert_player(database, 2, 'Player 2', 1)
        player3 = insert_player(database, 3, 'Player 3', 1)

        today = datetime.date.today()

        one_day_delta = datetime.timedelta(days=1)
        two_day_delta = datetime.timedelta(days=2)
        three_day_delta = datetime.timedelta(days=3)


        season1 = insert_season(database, 1, today, today + one_day_delta, 1)
        season2 = insert_season(database, 2, today + two_day_delta, today + three_day_delta, 1)

        wordle_day_S1_D1 = insert_wordle_day(database, "FIRST", 100, today, season1[0] )
        wordle_day_S1_D2 = insert_wordle_day(database, "SECND", 101, today + one_day_delta, season1[0])
        wordle_day_S2_D1 = insert_wordle_day(database, "THIRD", 102, today + two_day_delta, season2[0] )
        wordle_day_S2_D2 = insert_wordle_day(database, "FORTH", 103, today + three_day_delta, season2[0])


        for wordle_day in [wordle_day_S1_D1, wordle_day_S1_D2, wordle_day_S2_D1, wordle_day_S2_D2]:
            for player in [player1, player2, player3]:
                insert_player_score(database, player[0], wordle_day[0], player[0])

        self.assertEqual(['Player 1'], get_season_winners(database, 1))

    def test_get_season_winner_3_way_tie(self):
        # Create players to test with
        player1 = insert_player(database, 1, 'Player 1', 1)
        player2 = insert_player(database, 2, 'Player 2', 1)
        player3 = insert_player(database, 3, 'Player 3', 1)

        today = datetime.date.today()

        one_day_delta = datetime.timedelta(days=1)
        two_day_delta = datetime.timedelta(days=2)
        three_day_delta = datetime.timedelta(days=3)


        season1 = insert_season(database, 1, today, today + one_day_delta, 1)
        season2 = insert_season(database, 2, today + two_day_delta, today + three_day_delta, 1)

        wordle_day_S1_D1 = insert_wordle_day(database, "FIRST", 100, today, season1[0] )
        wordle_day_S1_D2 = insert_wordle_day(database, "SECND", 101, today + one_day_delta, season1[0])
        wordle_day_S2_D1 = insert_wordle_day(database, "THIRD", 102, today + two_day_delta, season2[0] )
        wordle_day_S2_D2 = insert_wordle_day(database, "FORTH", 103, today + three_day_delta, season2[0])


        for wordle_day in [wordle_day_S1_D1, wordle_day_S1_D2, wordle_day_S2_D1, wordle_day_S2_D2]:
            for player in [player1, player2, player3]:
                insert_player_score(database, 3, wordle_day[0], player[0])

        self.assertEqual(['Player 1', 'Player 2', 'Player 3'], get_season_winners(database, 1))

    def test_is_first_day_of_season_true(self):
        
        today = datetime.date.today()

        one_day_delta = datetime.timedelta(days=1)

        season1 = insert_season(database, 1, today, today + one_day_delta, 1)

        self.assertEqual(True, is_first_day_of_season(database, season1[0], today))
    
    def test_is_first_day_of_season_false(self):

        today = datetime.date.today()

        one_day_delta = datetime.timedelta(days=1)

        season1 = insert_season(database, 1, today, today + one_day_delta, 1)

        self.assertEqual(False, is_first_day_of_season(database, season1[0], today + one_day_delta))

    def test_is_first_day_of_season_middle(self):

        today = datetime.date.today()

        one_day_delta = datetime.timedelta(days=1)
        two_day_delta = datetime.timedelta(days=2)

        season1 = insert_season(database, 1, today, today + two_day_delta, 1)

        self.assertEqual(False, is_first_day_of_season(database, season1[0], today + one_day_delta))



class TestImgGen(unittest.TestCase):
    def setUp(self):
        # Runs before each test case
        create_tables(database)

    def tearDown(self):
        # Runs after each test case
        drop_tables(database)
        os.remove(database)

    # def test_generate_scoreboard_image(self):
    #     # Doesn't actually run a true test but still generates a sample scoreboard
    #     # image. Test by viewing the image

    #     wordle_game = insert_wordle_game(database, 1)

    #     wordle_game_id = wordle_game[0]
    #     players = []
    #     for i in range(6):
    #         player = insert_player(database, i, f'Wordler {i}', wordle_game_id)
    #         players.append(player)

    #     today = datetime.date.today()

    #     season_length = 30

    #     season1 = insert_season(database, 1, today, today + datetime.timedelta(days=season_length), 1)

    #     for i in range(season_length):
    #         wordle_day = insert_wordle_day(database, ("").join(random.choices(string.ascii_uppercase, k=5)), 100 + i, today + datetime.timedelta(days=i), 1)
    #         for player in players:
    #             insert_player_score(database, random.choice([1, 2, 3, 4, 5, 6, 7, 8]), wordle_day[0], player[0])

    #     scoreboard_path = generate_scoreboard_image(database, 1)

    #     send_image(scoreboard_path)
        
    #     send_message(f"Congrats to {' and '.join(get_season_winners(database, 1))}! You won")

        #self.assertEqual(f"{parent_path}/scoreboard.png", scoreboard_path)


if __name__ == '__main__':
    unittest.main()