from flask import Blueprint, jsonify, render_template, request
from dotenv import load_dotenv
from dbio import get_max_season, get_season_scoreboard
from img_gen import get_total_scores
import os
import datetime


env = os.getenv("ENV")
database = os.getenv("DATABASE")

scoreboards_bp = Blueprint('scoreboards', __name__, url_prefix='/scoreboards')

load_dotenv()

@scoreboards_bp.route('<chat_id>', methods=['GET'])
def get_scoreboard(chat_id):
    chat_id = int(chat_id)
    season_id = get_max_season(database, chat_id)[0]
    data, headers = get_season_scoreboard(database, season_id)
    totals = get_total_scores(data)
    html_data = {"totals": totals, "headers": headers, "data": data, 'chat_id': chat_id}
    return render_template('scoreboard.html', data=html_data)
