from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, delete_record, get_all_records, update_record, insert_player
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

players_bp = Blueprint('players', __name__, url_prefix='/players')

load_dotenv()

@players_bp.route('/', methods=['GET'])
def get_all_players():
    return jsonify(get_all_records(database, 'players'))

@players_bp.route('/<int:player_id>', methods=['GET'])
def get_player(player_id):
    return jsonify(get_record(database, 'players', ['id'], [player_id]))

@players_bp.route('/', methods=['POST'])
def create_player():

    json_data = request.get_json()

    name = json_data.get('name')
    id = json_data.get('id') # This is unique to player, most records dont get their ID passed here
    wordle_game_id = json_data.get('wordle_game_id')

    print(name, id, wordle_game_id)

    # Start and end date format: YYYYMMDD
    return jsonify(insert_player(database, id, name, wordle_game_id))

@players_bp.route('/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    # You'll have to send all fields :/

    json_data = request.get_json()

    name = json_data.get('name')
    wordle_game_id = json_data.get('wordle_game_id')

    update_fields = [ 'name', 'wordle_game_id']
    update_values = [ f"'{name}'", wordle_game_id]

    return jsonify(update_record(database, 'players', ['id'], [player_id], update_fields, update_values))
    

@players_bp.route('/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    return jsonify(delete_record(database, 'players', player_id))
