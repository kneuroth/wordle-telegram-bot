from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, delete_record, get_all_records, update_record, insert_player_game_style
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

player_game_styles_bp = Blueprint('player_game_styles', __name__, url_prefix='/player_game_styles')

load_dotenv()

@player_game_styles_bp.route('/', methods=['GET'])
def get_all_player_games():
    return jsonify(get_all_records(database, 'player_game_styles'))

@player_game_styles_bp.route('/<int:player_game_style_id>', methods=['GET'])
def get_player_game(player_game_style_id):
    return jsonify(get_record(database, 'player_game_styles', ['id'], [player_game_style_id]))

@player_game_styles_bp.route('/', methods=['POST'])
def create_player_game():

    json_data = request.get_json()

    style_str = json_data.get('style_str')
    player_game_id = json_data.get('player_game_id')

    # Start and end date format: YYYYMMDD
    return jsonify(insert_player_game_style(database, style_str, player_game_id))

@player_game_styles_bp.route('/<int:player_game_style_id>', methods=['PUT'])
def update_player_game_style(player_game_style_id):
    # You'll have to send all fields :/

    json_data = request.get_json()

    style_str = json_data.get('style_str')
    player_game_id = json_data.get('player_game_id')

    update_fields = [ 'style_str', 'player_game_id']
    update_values = [ f"'{style_str}'", player_game_id ]

    return jsonify(update_record(database, 'player_game_styles', ['id'], [player_game_style_id], update_fields, update_values))
    

@player_game_styles_bp.route('/<int:player_game_style_id>', methods=['DELETE'])
def delete_player_game_style(player_game_style_id):
    return jsonify(delete_record(database, 'player_game_styles', player_game_style_id))
