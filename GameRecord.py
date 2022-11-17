from functools import partial, reduce
import imgkit #Must install wkhtmltopdf to work https://wkhtmltopdf.org/downloads.html, add bin location to path
#'''> C:\Users\kelly\miniconda3\envs\wordle-telegram-bot\Scripts\pip3 install imgkit'''

import datetime

import json

import os

from dotenv import load_dotenv

load_dotenv()

class GameRecord:
    '''
    The class that controls the season leaderboards and creates new ones
    This class should initialize once before endpoint is open and should create itself 
    with files of all the scores and metadata
    
    Attributes
    ----------
    seasons -> Season[]
    current_season -> Season

    Methods
    ----------
    __init__(dir: str)
        Scan directory file, populate the <seasons> array with season objects
        that reflect data and metadata of each season

        For now just generate the current season as MVP but TODO in the future, 
        create every season so that users can ask the bot for past scoreboard shit
    

    generate_leaderboard_img(season: Season, file_name: str) : str
        Generates the specified season's leaderboard and saves as <file_name>,
        returns html string of leaderboard

    get_current_season()

    '''
    def __init__(self):
        #TODO scan directory files, populate <seasons> array with season objects 
        #that reflect data and metadata

        self.seasons = {}

        num_seasons = 0

        day_one = datetime.datetime(2022, 1, 23)
        today = datetime.datetime.now()
        
        with open('seasons/season_index.txt') as f:
            num_seasons = int(f.read())
        

        for i in range(1,num_seasons+1):
            self.seasons[str(i)] = self.Season(f"seasons/season_{str(i)}_metadata.json", f"seasons/season_{str(i)}_data.json")
            
        #TODO Insert to test

        #self.write_seasons()

    def insert_score(self, season, player, score, date: datetime.date):
        season.insert_score(player, score, date)
        self.write_seasons()

    def generate_season(self, first_day: datetime.date, last_day: datetime.date, season_num):
        # Inclusive :)
        # Generate python season objects that start with first_day and end on last_day
        # Be sure to call write_seasons() after generating this

        with open("season_templates/metadata_template.json") as json_config:
            config = json.load(json_config)

        with open("season_templates/data_template.json") as json_data:
            data = json.load(json_data)

        # loop through days
        day = first_day
        while(day != (last_day + datetime.timedelta(days=1))):
            day_row = [""] * len(data["headers"])
            day_row[0] = str(day)
            day += datetime.timedelta(days=1)
            data["rows"].append(day_row)

        #data["rows"]
        

        
        with open(f"seasons/season_{season_num}_metadata.json", "w") as outfile:
            outfile.write(json.dumps(config))

        with open(f"seasons/season_{season_num}_data.json", "w") as outfile:
            outfile.write(json.dumps(data))

        #then run season constructor
        self.seasons[season_num] = self.Season(f"seasons/season_{season_num}_metadata.json", f"seasons/season_{season_num}_data.json")
        self.seasons[season_num].updated = True

        with open('seasons/season_index.txt', "w") as f:
            f.write(str(season_num))


    # Write what is currently stored as python object data into season json files
    def write_seasons(self):
        for season in self.seasons:
            if self.seasons[season].updated:
                data_dump = json.dumps(self.seasons[season].data)
                config_dump = json.dumps(self.seasons[season].config)
                with open(f"seasons/season_{season}_data.json", "w") as outfile:
                    outfile.write(data_dump)
                with open(f"seasons/season_{season}_metadata.json", "w") as outfile:
                    outfile.write(config_dump)
                self.seasons[season].updated = False

    # Read what is currently in json files to python objects
    def read_seasons(self):
        with open('seasons/season_index.txt') as f:
            num_seasons = int(f.read())

        for i in range(1,num_seasons+1):
            self.seasons[str(i)] = self.Season(f"seasons/season_{str(i)}_metadata.json", f"seasons/season_{str(i)}_data.json")

        with open('seasons/season_index.txt', "w") as f:
            f.write(len(self.seasons))

    def generate_leaderboard_img(self, season, file_name):
        return season.generate_image(file_name)

    def get_current_season(self):
        # If today is not a new season day then return whichever season contains todays date
        latest_season = self.seasons[list(self.seasons.keys())[-1]]
        if any(row[0] == str(datetime.date.today()) for row in latest_season.data["rows"]) :
            return latest_season
        else:
            return False


    class Season:
        '''
        The class that controls, updates jsons and html, generates images for a season
        
        Attributes
        ----------
        updated -> Bool:
            set to True if any changes were made
        
        data -> Dict:
            Structure:
            {
                "headers" -> list,
                "rows" -> list
            }
            Contains id header names and row data 

        config -> Dict
            Structure of each header object:
            "<header_name>":
            {
                "pretty" -> str
            }
            Contains header names used for column identification, headers should be date, 
            wordle, each user's username

        Methods
        ----------

        insert_score(score -> int, date -> datetime)
            Inserts score at datetime position and sets self.updated to True

        create_season_object(config -> str (filepath), data -> str (filepath))
            Opens config and data json files and copies contents to config and data attributes

        generate_image(file_name: str) -> Bool
            Creates a jpg image of the current leaderboard and writes to file <file_name>

        generate_header_html_string() -> str
            Helper function to generate_image (above), generates the html string for headers for the
            wordle scoreboard, including styles, based on the self.config objects

        '''
        def __init__(self, config, data):
            self.config_path = config
            self.data_path = data
            self.config = self.get_config_json()
            self.data = self.get_data_json()
            if self.data["finished"]:
                print("This season has finished")
            self.updated = False


        def __str__(self):
            return f"""
{self.data}

{self.config}
            """

        def get_config_json(self):
            with open(self.config_path) as json_config:
                return json.load(json_config)

        def get_data_json(self):
            with open(self.data_path) as json_data:
                return json.load(json_data)


        def is_season_finished(self):
            # First just check the json
            if self.get_data_json()["finished"]:
                return True
            
            # Next check the python object
            # Check if today is the last day in the data rows
            if self.str_to_date(self.data["rows"][len(self.data["rows"]) - 1][0]) == datetime.date.today():
                # Check if everyone has submitted
                if self.all_submitted_on(datetime.date.today()):
                    return True
                    
            return False

        def all_submitted_on(self, date):

            row = self.get_row_by_date(date)

            if row == False:
                return False

            print(f"Checking {date}")

            # If any item ( after date, wordle_num, and word col aka names col) in specified date row
            # is empty then return false - Not everyone has submitted, otherwise return true - everyone has submitted
            if any(item == "" for item in row[3:]):
                return False
            return True


        def is_player_key(key):
            return key not in ["date", "wordle_num", "word"]

        def get_row_by_date(self, date):
            date_index = self.data["headers"].index("date")
            min_date = self.str_to_date(self.data["rows"][0][date_index])
            max_date = self.str_to_date(self.data["rows"][len(self.data["rows"]) - 1][date_index])

            closer_to_min = (date - min_date) < (max_date - date)

            row_iterator = self.data["rows"] if closer_to_min else reversed(self.data["rows"])
            
            for row in row_iterator:
                if row[date_index] == str(date):
                    return row
            return False
            

        #TODO: Re write this entire thing so data["rows"] is a key/value pair so inserting is a lot faster??
        # Or is it more important to be a list for html creation? Probably
        def insert_score(self, player, score, date: datetime.date):
            date_index = self.data["headers"].index("date")
            player_index = self.data["headers"].index(player)
            min_date = self.str_to_date(self.data["rows"][0][date_index])
            max_date = self.str_to_date(self.data["rows"][len(self.data["rows"]) - 1][date_index])

            closer_to_min = (date - min_date) < (max_date - date)

            row_iterator = self.data["rows"] if closer_to_min else reversed(self.data["rows"])
            
            for row in row_iterator:
                if row[date_index] == str(date):
                    row[player_index] = int(score)
                    break
            self.updated = True
        
        # date_string should be formatted YYYY-MM-DD (integers)
        #TODO: Should probably be a helper function or in its own file
        def str_to_date(self, date_string):
            date_list = date_string.split("-")
            return datetime.date(int(date_list[0]), int(date_list[1]),  int(date_list[2]))

            

        def generate_image(self, file_name):
            css = os.environ.get("CSS_PATH")
            newline = "\n"
            html_string = f'''
            <!DOCTYPE html>
            <div class="container-wrap">
                <section id="leaderboard">
                    <div class="ladder-title">
                        <h1>Standings</h1>
                        </div>
                    <table id="rankings" class="leaderboard-results" width="100%">
                        <thead>
                            <tr>
                                { self.generate_header_html_string() }
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                { self.generate_data_html_string() }
                            </tr>

                        </tbody>
                    </table>
                </section>
            </div>
            '''
            print("imgkit working:")
            imgkit.from_string(html_string, f'{file_name}.jpg', css=css)
            return html_string

        def generate_header_html_string(self):
            html_string = ""
            for item in self.config:
                colour = f'"background-color:{self.config[item]["colour"]};"' if "colour" in self.config[item] else '""'
                pretty = self.config[item]["pretty"] if "pretty" in self.config[item] else item
                html_string = html_string + f"<th {f'style={colour}'}> {pretty}</th>"
            html_string = html_string
            return html_string


        def generate_data_html_string(self):
            return "".join([f"<tr><th>" + "</th><th>".join(map(str,row)) + "</th></tr>" for row in self.data["rows"]])




