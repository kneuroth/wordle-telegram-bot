from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records
import os

env = os.getenv("ENV")
database = os.getenv("DATABASE")

wordle_games_bp = Blueprint('wordle_games', __name__, url_prefix='/wordle_games')

load_dotenv()

@wordle_games_bp.route('/', methods=['GET'])
def get_all_wordle_games():
    return jsonify(get_all_records(database, 'wordle_games'))