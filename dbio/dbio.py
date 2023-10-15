import sqlite3

import datetime

#TODO: Standardize return types of all of these so it's json or something, idk

# -------HELPER FUNCTIONS--------#

def delete_record(database: str, table_name: str, id:int ):
    """
    Deletes a record from a table. Used in the admin console only, not used in app.py
    
    Parameters
    ----------
    database: string
        Path/name of database to insert record
    
    table_name: str
        Name of table to insert record

    id: int
        Required id field of the desired record to delete

    Returns
    -------
    Boolean
        False if the record was not found, True if found and succesfully deleted
    """
    connection = sqlite3.connect(database)

    cursor = connection.cursor()
    query = f"DELETE FROM {table_name} WHERE id = {id}"

    try:
        # Execute DELETE query
        cursor.execute(query)
        
        # Commit the DELETE
        connection.commit()

        return True
    except sqlite3.Error as er:
        print("SQLERROR: ", er)
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
    

def insert_record(database: str, table_name: str, table_fields: tuple, record_data: tuple):
    """
    Inserts a record into a table. Will not be exported for use by app.py.

    Parameters
    ----------
    database: string
        Path/name of database to insert record
    
    table_name: str
        Name of table to insert record

    record_data: tuple
        Required record data that will be inserted

    Returns
    -------
    Tuple
        The inserted record, as it appears in the database


    """
    connection = sqlite3.connect(database)

    cursor = connection.cursor()

    # Check if record with the same field values already exists

    # Enclose record_data fields with quotes if they don't have it
    # TODO: Standardize this
    quoted_record_data = [f"'{data}'" for data in record_data]
    query = f"SELECT * FROM {table_name} WHERE {' AND '.join(f'{table_fields[field]} = {quoted_record_data[field]}' for field in range(len(table_fields)))}"
    cursor.execute(query)
    existing_record = cursor.fetchone()

    if existing_record:
        return existing_record

    try:
        # Doing these length checks because forcing a single element tuple like (element,)
        # to prevent python from interpreting the () as an expression causes SQL to get a syntax error
        # because it includes the trailing comma 
        query = f"""
        INSERT INTO {table_name} {table_fields if len(table_fields) > 1 else f"('{table_fields[0]}')"}
        VALUES {record_data if len(record_data) > 1 else f"('{record_data[0]}')"};
        """
        # Execute the INSERT query
        cursor.execute(query)
    
        # Get the most recently inserted row id
        id = cursor.lastrowid

        # Commit the INSERT
        connection.commit()

        # Execute SELECT and fetch recently INSERTED record
        cursor.execute(f"SELECT * FROM {table_name} WHERE id={id}")
        inserted_record = cursor.fetchone()
        # Return the record as it is in the database
        return inserted_record

    except sqlite3.Error as er:
        print("SQLERROR: ", er)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


# TODO: Can make following two functions into one function

def query_one(database:str, query:str):
    connection = sqlite3.connect(database)

    cursor = connection.cursor()

    try:

        # Execute SELECT and fetch record
        cursor.execute(query)
        record = cursor.fetchone()

        # Return the record as it is in the database
        return record

    except sqlite3.Error as er:
        print("SQLERROR: ", er)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def query_many(database:str, query:str):
        connection = sqlite3.connect(database)

        cursor = connection.cursor()

        try:
            # execute the SELECT query
            cursor.execute(query)
            columns = list(map(lambda x: x[0], cursor.description))
            records = cursor.fetchall()

            return records, columns
        
        except sqlite3.Error as er:
            print("SQLERROR:", er)
        finally:
            cursor.close()
            connection.close()


# -------EXPORTED FUNCTIONS--------#

def insert_wordle_game(database: str, chat_id: int):
    # Adds a wordle game into the wordle_games table
    # Have to insert the brackets and quotes in cases where insert_record table_feilds and record_date tuples are of length < 2
    return insert_record(database, 'wordle_games', ('id',), (chat_id,))

def insert_season(database: str, season_number: int, start_date: datetime.date, end_date: datetime.date, wordle_game_id: int):
    # Adds a season into the seasons table. Cast dates to str. See insert_record for more info
    return insert_record(database, 'seasons', ('season_number', 'start_date', 'end_date', 'wordle_game_id'), (season_number, str(start_date), str(end_date), wordle_game_id))

def insert_player(database: str, player_id: int, player_name: str):
    # Adds a player into the players table. See insert_record for more info
    return insert_record(database, 'players', ('id', 'name'), (player_id, player_name))

def insert_player_game(database: str, player_id: int, wordle_game_id: int):
    # Adds a player game into the player_games table.
    return insert_record(database, 'player_games', ('player_id', 'wordle_game_id'), (player_id, wordle_game_id))

def insert_player_game_style(database: str, style_str: str, player_game_id: int):
    # Adds a player game style into the player_game_styles table.
    return insert_record(database, 'player_game_styles', ('style_str', 'player_game_id'), (style_str, player_game_id))
    
def insert_wordle_day(database: str, word: str, wordle_number: int, date: datetime.date):
    # Adds a wordle day into the wordle_days table. Cast date to str. See insert_record for more info
    return insert_record(database, 'wordle_days', ('word', 'wordle_number', 'date'), (word, wordle_number, str(date)))

def insert_player_score(database: str, score: int, wordle_day_id: int, player_id: int, season_id: int):
    return insert_record(database, 'player_scores', ('score', 'wordle_day_id', 'player_id', 'season_id'), (score, wordle_day_id, player_id, season_id))

def get_record(database: str, table_name: str, fields: list, values: list):
    # Get a record based on lists of fields and values. If a string is involved you MUST close the value in ''
    if len(fields) != len(values):
        raise Exception("Length of 'fields' and 'values' must be the same")
    where_clause = " AND ".join([f"{field}={value}" for field, value in zip(fields, values)])
    return query_one(database, f"SELECT * FROM {table_name} WHERE {where_clause}")

def get_records(database: str, table_name: str, fields: list, values: list):
    # Get many records based on lists of fields and values. If a string is involved in the values, you MUST close the value in ''
    if len(fields) != len(values):
        raise Exception("Length of 'fields' and 'values' must be the same")
    where_clause = " AND ".join([f"{field}={value}" for field, value in zip(fields, values)])
    return query_many(database, f"SELECT * FROM {table_name} WHERE {where_clause}")[0]

def get_all_records(database: str, table_name: str):
    return query_many(database, f"SELECT * FROM {table_name}")

def update_record(database: str, table_name: str, id_fields: list, id_values: list, update_fields: list, update_values: list):
    # Update a record. id_fields and values go in the WHERE clause to specify which record to update, while the 
    # update_fields and and values are the values that should be updated
    # connect to the database
    # Dates should be strings enclosed in 'quotes'
    connection = sqlite3.connect(database)

    # create a cursor object
    cursor = connection.cursor()

    set_clause = " , ".join([f"{field}={value}" for field, value in zip(update_fields, update_values)])
    where_clause = " AND ".join([f"{field}={value}" for field, value in zip(id_fields, id_values)])
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
    print(query)
    try:

        # execute an UPDATE query to modify a record
        cursor.execute(query)

        # Commit the UPDATE
        connection.commit()

        # execute a SELECT query to retrieve the updated record
        cursor.execute(f"SELECT * FROM {table_name} WHERE {where_clause}")
        record = cursor.fetchone()

        # Return the record as it is in the database
        return record

    except sqlite3.Error as er:
        print("SQLERROR: ", er)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


# -------SPECIALIZED QUERIES--------#

def is_first_day_of_season(database, season_id, date):
    start_date = query_one(database, f"""
    SELECT start_date FROM seasons WHERE id={season_id}
    """)[0]
    return start_date == str(date)

def is_last_day_of_season(database, season_id, date):
    end_date = query_one(database, f"""
    SELECT end_date FROM seasons WHERE id={season_id}
    """)[0]
    return end_date == str(date)

def get_season_scoreboard(database, season_id, censored=False):
    # Returns tuple of (records, columns)
    # TODO: Get p.name from players where player_game has season's wordle_game_id
    season_players = query_many(database, f"""
                                
        SELECT * 
        FROM players p
        WHERE p.id IN (
            SELECT pg.player_id
            FROM player_games pg
            WHERE pg.wordle_game_id IN (
                SELECT wg.id
                FROM wordle_games wg
                WHERE wg.id IN (              
                    SELECT s.wordle_game_id
                    FROM seasons s
                    WHERE s.id={season_id}
                    LIMIT 1
                )
            )
        )
    """)[0]

    result = query_many(database, f"""

                        SELECT
                        date,
                        wordle_number,
                        word,
                        {','.join([f"SUM(CASE WHEN p.name = '{player_name[1]}' THEN ps.score ELSE 0 END) AS '{player_name[1]}'" for player_name in season_players])}
                        FROM player_scores ps
                        JOIN wordle_days wd ON ps.wordle_day_id = wd.id
                        JOIN players p ON ps.player_id = p.id
                        WHERE ps.season_id={season_id}
                        GROUP BY date, wordle_number, word
    
    """)

    if censored:
        for index, row in enumerate(result[0]):
            date = datetime.date(int(row[0][0:4]), int(row[0][5:7]), int(row[0][8:10]))
            if date == datetime.date.today():
                tup_list = list(row)
                tup_list[2] = 'XXXXX'
                result[0][index] = tuple(tup_list)

    return result

                        # SELECT
                        # date,
                        # wordle_number,
                        # word,
                        # SUM(CASE WHEN p.name = 'Player 1' THEN ps.score ELSE 0 END) AS 'Player 1',
                        # SUM(CASE WHEN p.name = 'Player 2' THEN ps.score ELSE 0 END) AS 'Player 2'
                        # FROM player_scores ps
                        # JOIN wordle_days wd ON ps.wordle_day_id = wd.id
                        # JOIN players p ON ps.player_id = p.id
                        # WHERE ps.season_id = 1
                        # GROUP BY date, wordle_number, word

def get_season_by_date(database: str, date: datetime.date, wordle_game_id: int):
    return query_one(database, f"SELECT * FROM seasons WHERE wordle_game_id={wordle_game_id} AND '{date}' BETWEEN start_date AND end_date")

def get_max_season(database: str, wordle_game_id: int):
    # Returns the max season of wordle_game_id
    return query_one(database, f"SELECT * FROM seasons WHERE wordle_game_id={wordle_game_id} ORDER BY season_number DESC LIMIT 1")

def get_non_submittors(database: str, wordle_day_id: int, season_id: int):
    # Returns all players (tuple) who did not yet submit. Returns [] if everyone that exists submitted
    return query_many(database, f"SELECT * FROM players WHERE id NOT IN (SELECT player_id FROM player_scores WHERE wordle_day_id={wordle_day_id} AND season_id={season_id})")[0]

def get_season_winners(database: str, season_id: int):
    # Retuns all players (player name strings) who have the highest score, you will have to check if the season is over
    
    # Returns a list of tuples (player_name, score) where score is their total score
    player_scores = query_many(database, f"SELECT name, totals.score FROM players, (SELECT player_id, SUM(score) as score FROM player_scores WHERE wordle_day_id IN (SELECT id FROM wordle_days WHERE season_id={season_id}) GROUP BY player_id) as totals WHERE totals.player_id=id")[0]

    min = 9999
    winners = []

    for player, score in player_scores:
        if score < min:
            min = score
    
    for player, score in player_scores:
        if score == min:
            winners.append(player)
    
    return winners

if __name__ == "__main__":
    pass
