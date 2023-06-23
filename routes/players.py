from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records
import os

env = os.getenv("ENV")
database = os.getenv("DATABASE")

players_bp = Blueprint('players', __name__, url_prefix='/players')

load_dotenv()

@players_bp.route('/', methods=['GET'])
def get_all_players():
    return jsonify(get_all_records(database, 'players'))