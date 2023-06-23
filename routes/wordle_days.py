from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from dbio import get_record, get_all_records
import os

env = os.getenv("ENV")
database = os.getenv("DATABASE")

wordle_days_bp = Blueprint('wordle_days', __name__, url_prefix='/wordle_days')

load_dotenv()

@wordle_days_bp.route('/', methods=['GET'])
def get_all_wordle_days():
    return jsonify(get_all_records(database, 'wordle_days'))