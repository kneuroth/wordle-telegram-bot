import sqlite3

def create_tables(datebase_name: str):

    # Create a connection to the database
    connection = sqlite3.connect(datebase_name)

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    new_create_tables_query = """

    CREATE TABLE IF NOT EXISTS wordle_games (
        id INTEGER PRIMARY KEY UNIQUE
    );

    CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY UNIQUE,
        season_number INTEGER,
        start_date DATE,
        end_date DATE,
        wordle_game_id INTEGER,
        FOREIGN KEY (wordle_game_id) REFERENCES wordle_games(id)
    );

    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY UNIQUE,
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS player_games (
        id INTEGER PRIMARY KEY UNIQUE,
        player_id INTEGER,
        wordle_game_id INTEGER,
        FOREIGN KEY (player_id) REFERENCES players(id),
        FOREIGN KEY (wordle_game_id) REFERENCES wordle_games(id)
    );

    CREATE TABLE IF NOT EXISTS player_game_styles (
        id INTEGER PRIMARY KEY UNIQUE,
        style_str TEXT,
        player_game_id INTEGER,
        FOREIGN KEY (player_game_id) REFERENCES player_games(id)
    );

    CREATE TABLE IF NOT EXISTS wordle_days (
        id INTEGER PRIMARY KEY UNIQUE,
        word TEXT,
        wordle_number INTEGER,
        date DATE
    );

    CREATE TABLE IF NOT EXISTS player_scores (
        id INTEGER PRIMARY KEY UNIQUE,
        score INTEGER,
        wordle_day_id INTEGER,
        player_id INTEGER,
        season_id INTEGER,
        FOREIGN KEY (wordle_day_id) REFERENCES wordle_days(id),
        FOREIGN KEY (player_id) REFERENCES players(id),
        FOREIGN KEY (season_id) REFERENCES seasons(id)
    );
"""

    # Execute the CREATE TABLE queries using the cursor
    cursor.executescript(new_create_tables_query)

    # Commit the changes to the database
    connection.commit()

    # Close the connection to the database
    connection.close()

def drop_tables(database_name: str):
    # Connect to the database
    conn = sqlite3.connect(database_name)

    # Create a cursor object
    cursor = conn.cursor()

    def drop_table(table: str):
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # Drop a table
    table_names = ['wordle_games', 'seasons', 'players', 'player_games', 'wordle_days', 'player_scores']
    list(map(drop_table, table_names))

    # Commit the transaction
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_tables()