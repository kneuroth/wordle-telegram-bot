from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records, update_record, insert_wordle_day, delete_record
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

wordle_days_bp = Blueprint('wordle_days', __name__, url_prefix='/wordle_days')

load_dotenv()

@wordle_days_bp.route('/', methods=['GET'])
def get_all_wordle_days():
    return jsonify(get_all_records(database, 'wordle_days'))

@wordle_days_bp.route('/<int:wordle_day_id>', methods=['GET'])
def get_wordle_day(wordle_day_id):
    return jsonify(get_record(database, 'wordle_days', ['id'], [wordle_day_id]))

@wordle_days_bp.route('/', methods=['POST'])
def create_wordle_day():

    json_data = request.get_json()

    date_str = str(json_data.get('date'))
    
    word = json_data.get('word')
    wordle_number = json_data.get('wordle_number')
    date = datetime.date(int(date_str[:4]), int(date_str[6:7]), int(date_str[9:10]))
    season_id = json_data.get('season_id')    

    return jsonify(insert_wordle_day(database, word, wordle_number, date, season_id))

@wordle_days_bp.route('/<int:wordle_day_id>', methods=['PUT'])
def update_wordle_day(wordle_day_id):
    # You'll have to send all fields :/

    json_data = request.get_json()

    date_str = str(json_data.get('date'))
    
    word = json_data.get('word')
    wordle_number = json_data.get('wordle_number')
    date = datetime.date(int(date_str[:4]), int(date_str[6:7]), int(date_str[9:10]))
    season_id = json_data.get('season_id')  

    update_fields = ['word', 'wordle_number', 'date', 'season_id']
    update_values = [f"'{word}'", wordle_number, f"'{str(date)}'", season_id]

    return jsonify(update_record(database, 'wordle_days', ['id'], [wordle_day_id], update_fields, update_values))

@wordle_days_bp.route('/<int:wordle_day_id>', methods=['DELETE'])
def delete_wordle_day(wordle_day_id):
    return jsonify(delete_record(database, 'wordle_days', wordle_day_id))