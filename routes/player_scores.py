from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records, insert_player_score
import os

env = os.getenv("ENV")
database = os.getenv("DATABASE")

player_scores_bp = Blueprint('player_scores', __name__, url_prefix='/player_scores')

load_dotenv()

@player_scores_bp.route('/', methods=['GET'])
def get_all_player_scores():
    return jsonify(get_all_records(database, 'player_scores'))

@player_scores_bp.route('/', methods=['POST'])
def create_player_score():
    data = request.json()
    # NO need for duplicate detection because tables will be created with UNIQUE 
    # beside ID schema creation
    return insert_player_score(database, data['score'], data['wordle_day_id'], data['player_id'])
