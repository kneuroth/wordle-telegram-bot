from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, delete_record, get_all_records, update_record, insert_season
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

seasons_bp = Blueprint('seasons', __name__, url_prefix='/seasons')

load_dotenv()

#CRUD

@seasons_bp.route('/', methods=['GET'])
def get_all_seasons():
    return jsonify(get_all_records(database, 'seasons'))

@seasons_bp.route('/<int:season_id>', methods=['GET'])
def get_season(season_id):
    return jsonify(get_record(database, 'seasons', ['id'], [season_id]))

@seasons_bp.route('/', methods=['POST'])
def create_season():

    json_data = request.get_json()

    season_number = json_data.get('season_number')

    start_date_str = str(json_data.get('start_date'))
    end_date_str = str(json_data.get('end_date'))

    start_date = datetime.date(int(start_date_str[:4]), int(start_date_str[6:7]), int(start_date_str[9:10]))
    end_date = datetime.date(int(end_date_str[:4]), int(end_date_str[6:7]), int(end_date_str[9:10]))
    
    wordle_game_id = json_data.get('wordle_game_id')

    # Start and end date format: YYYYMMDD
    return jsonify(insert_season(database, season_number, start_date, end_date, wordle_game_id))

@seasons_bp.route('/<int:season_id>', methods=['PUT'])
def update_season(season_id):
    # You'll have to send all fields :/

    json_data = request.get_json()

    season_number = json_data.get('season_number')

    start_date_str = str(json_data.get('start_date'))
    end_date_str = str(json_data.get('end_date'))
    start_date = str(datetime.date(int(start_date_str[:4]), int(start_date_str[6:7]), int(start_date_str[9:10])))
    end_date = str(datetime.date(int(end_date_str[:4]), int(end_date_str[6:7]), int(end_date_str[9:10])))
    
    wordle_game_id = json_data.get('wordle_game_id')

    update_fields = ['season_number', 'start_date', 'end_date', 'wordle_game_id']
    update_values = [season_number, f"'{str(start_date)}'", f"'{str(end_date)}'", wordle_game_id]

    return jsonify(update_record(database, 'seasons', ['id'], [season_id], update_fields, update_values))
    

@seasons_bp.route('/<int:season_id>', methods=['DELETE'])
def delete_season(season_id):
    return jsonify(delete_record(database, 'seasons', season_id))
