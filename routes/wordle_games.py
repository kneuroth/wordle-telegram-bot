from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records, update_record, insert_wordle_game, delete_record
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

wordle_games_bp = Blueprint('wordle_games', __name__, url_prefix='/wordle_games')

load_dotenv()

@wordle_games_bp.route('/', methods=['GET'])
def get_all_wordle_games():
    return jsonify(get_all_records(database, 'wordle_games'))

@wordle_games_bp.route('/<int:wordle_game_id>', methods=['GET'])
def get_wordle_game(wordle_game_id):
    return jsonify(get_record(database, 'wordle_games', ['id'], [wordle_game_id]))

@wordle_games_bp.route('/', methods=['POST'])
def create_wordle_game():

    json_data = request.get_json()

    chat_id = int(json_data.get('id'))

    return jsonify(insert_wordle_game(database, chat_id))

@wordle_games_bp.route('/<wordle_game_id>', methods=['PUT'])
def update_wordle_game(wordle_game_id):
    # You'll have to send all fields :/

    json_data = request.get_json()


    print(json_data)

    chat_id = int(json_data.get('id'))

    update_fields = ['id']
    update_values = [chat_id]

    return jsonify(update_record(database, 'wordle_games', ['id'], [wordle_game_id], update_fields, update_values))
    

@wordle_games_bp.route('/<wordle_game_id>', methods=['DELETE'])
def delete_wordle_game(wordle_game_id):
    return jsonify(delete_record(database, 'wordle_games', wordle_game_id))