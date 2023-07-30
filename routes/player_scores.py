from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records, update_record, insert_player_score, delete_record
import os
import datetime

env = os.getenv("ENV")
database = os.getenv("DATABASE")

player_scores_bp = Blueprint('player_scores', __name__, url_prefix='/player_scores')

load_dotenv()

@player_scores_bp.route('/', methods=['GET'])
def get_all_player_scores():
    return jsonify(get_all_records(database, 'player_scores'))

@player_scores_bp.route('/<int:player_score_id>', methods=['GET'])
def get_player_score(player_score_id):
    return jsonify(get_record(database, 'player_scores', ['id'], [player_score_id]))

@player_scores_bp.route('/', methods=['POST'])
def create_player_score():

    json_data = request.get_json()
    
    score = json_data.get('score')
    wordle_day_id = json_data.get('wordle_day_id')
    player_id = json_data.get('player_id')
    season_id = json_data.get('season_id')

    return jsonify(insert_player_score(database, score, wordle_day_id, player_id, season_id))

@player_scores_bp.route('/<int:player_score_id>', methods=['PUT'])
def update_player_score(player_score_id):
    # You'll have to send all fields :/

    json_data = request.get_json()
    
    score = json_data.get('score')
    wordle_day_id = json_data.get('wordle_day_id')
    player_id = json_data.get('player_id')
    season_id = json_data.get('season_id')

    update_fields = ['score', 'wordle_day_id', 'player_id', 'season_id']
    update_values = [score, wordle_day_id, player_id, season_id]

    return jsonify(update_record(database, 'player_scores', ['id'], [player_score_id], update_fields, update_values))

@player_scores_bp.route('/<int:player_score_id>', methods=['DELETE'])
def delete_player_score(player_score_id):
    return jsonify(delete_record(database, 'player_scores', player_score_id))
