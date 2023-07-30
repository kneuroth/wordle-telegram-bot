from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, delete_record, get_all_records, update_record, insert_player_game
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

player_games_bp = Blueprint('player_games', __name__, url_prefix='/player_games')

load_dotenv()

@player_games_bp.route('/', methods=['GET'])
def get_all_player_games():
    return jsonify(get_all_records(database, 'player_games'))

@player_games_bp.route('/<int:player_game_id>', methods=['GET'])
def get_player_game(player_game_id):
    return jsonify(get_record(database, 'player_games', ['id'], [player_game_id]))

@player_games_bp.route('/', methods=['POST'])
def create_player_game():

    json_data = request.get_json()

    player_id = json_data.get('player_id')
    wordle_game_id = json_data.get('wordle_game_id')

    # Start and end date format: YYYYMMDD
    return jsonify(insert_player_game(database, player_id, wordle_game_id))

@player_games_bp.route('/<int:player_game_id>', methods=['PUT'])
def update_player_game(player_game_id):
    # You'll have to send all fields :/

    json_data = request.get_json()

    player_id = json_data.get('player_id')
    wordle_game_id = json_data.get('wordle_game_id')

    update_fields = [ 'player_id', 'wordle_game_id']
    update_values = [ player_id, wordle_game_id ]

    return jsonify(update_record(database, 'player_games', ['id'], [player_game_id], update_fields, update_values))
    

@player_games_bp.route('/<int:player_game_id>', methods=['DELETE'])
def delete_player_game(player_game_id):
    return jsonify(delete_record(database, 'player_games', player_game_id))
