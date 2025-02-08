"""
Module for managing tournament-related operations, including creation, updating,
viewing, and setting scores for knockouts and leagues.
"""

from datetime import date, datetime
import random
from flask import request, Blueprint, jsonify, render_template
from utils import authenticate_user
from data.models import Tournament
from services import tournaments_service
from common.responses import NoContent, NotFound, BadRequest, Successful, Unauthorized

tournaments_blueprint = Blueprint('tournaments', __name__, url_prefix='/tournaments')

@tournaments_blueprint.route('/all', methods=['GET'])
def all_tournaments():
    """
    Retrieve all tournaments as JSON.
    Returns:
        A JSON object containing a list of all tournaments.
    """
    tournaments = tournaments_service.all_tournaments()
    tournaments_data = [{
        "id": t["id"],
        "title": t["title"],
        "prize": t["prize"],
        "tournament_format": t["tournament_format"],
        "winner": t["winner"],
        "players": t["players"],
        "matches": t["matches"]
    } for t in tournaments]

    return jsonify({"tournaments": tournaments_data})

@tournaments_blueprint.get('/{id}')
def get_tournament_by_id(tournament_id: int) -> dict:
    """
    Retrieve details of a specific tournament by ID.

    :param id: Tournament ID.
    :return: JSON response with tournament details or an error message.
    """
    tournament = tournaments_service.get_by_tournament_id(tournament_id)
    if not tournament:
        return NotFound('Not such tournament')

    return tournament

@tournaments_blueprint.route('/knockout', methods=['GET', 'POST'])
def create_knockout_tournament() -> str:
    """
    Create a new knockout tournament.

    :return: JSON response indicating success or error.
    """

    if request.method == 'GET':
        return render_template('create_knockout_tournament.html')

    data = request.get_json()

    title = data.get('title')
    prize = data.get('prize')
    format_id = 1
    participants = data.get('participants', [])
    starting_date_str = data.get('starting_date')
    starting_date = datetime.strptime(starting_date_str, "%Y-%m-%d").date()

    tournament = Tournament(title=title, prize=prize, format_id=format_id, winner=None)

    user = authenticate_user()
    if not (user.is_admin() or user.is_director()):
        return Unauthorized('You are not authorized to create tournaments')

    if len(participants) not in [4, 8, 16, 32, 64, 128, 256]:
        return BadRequest('Participants count must be one of [4, 8, 16, 32, 64, 128, 256].')

    random.shuffle(participants)

    if starting_date < date.today():
        return BadRequest('Starting date should be today at the earliest!')

    tournaments_service.create_knockout_tournament(tournament, participants, starting_date)

    return Successful("Success")

@tournaments_blueprint.route('/set_winner/<int:tournament_id>', methods=['GET', 'PUT'])
def set_tournament_winner(tournament_id: int) -> str:
    """
    Sets the winner for a given tournament.
    Ensures the user is authorized and the winner is a valid participant.
    """
    if request.method == 'GET':
        return render_template('set_tournament_winner.html')

    data = request.get_json()
    winner_id = data.get('winner')

    if not winner_id:
        return BadRequest("Winner ID is required!")

    user = authenticate_user()
    if not (user.is_admin() or user.is_director()):
        return Unauthorized('You are not authorized to set tournament winners!')

    tournament = tournaments_service.get_by_tournament_id(tournament_id)
    if not tournament:
        return NotFound("Tournament not found!")

    if not tournaments_service.check_for_existing_player(winner_id):
        return BadRequest("The selected winner does not exist in this tournament!")

    tournaments_service.set_tournament_winner(tournament_id, winner_id)

    return Successful("Winner set successfully!")

@tournaments_blueprint.put('/knockout/set_score/matchup/<int:match_id>')
def set_scores(match_id: int) -> str:
    """
    Set scores for a specific matchup in a knockout tournament.
    """
    scores = request.get_json()
    score_one, score_two = scores.get('score_one', -1), scores.get('score_two', -1)

    if score_one < 0 or score_two < 0 or score_one == score_two:
        return BadRequest('Invalid scores: Ensure scores are positive and not equal.')

    user = authenticate_user()
    if not user.is_admin() and not user.is_director():
        return Unauthorized('You do not have permission to set scores.')

    matchup = tournaments_service.get_matchup(match_id)
    if not matchup:
        return NotFound('Matchup not found.')

    tournaments_service.set_matchup_score(match_id, [score_one, score_two])
    return Successful('Scores updated successfully.')

@tournaments_blueprint.route('/league', methods=['GET', 'POST'])
def create_league() -> str:
    """
    Creates a new league tournament.
    Validates input data and ensures the user is authorized to create leagues.
    """

    if request.method == 'GET':
        return render_template('create_league_tournament.html')

    data = request.get_json()

    title = data.get('title')
    prize = data.get('prize')
    format_id = 2
    participants = data.get('participants', [])
    starting_date_str = data.get('starting_date')

    try:
        starting_date = datetime.strptime(starting_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return BadRequest('Invalid or missing date format. Use YYYY-MM-DD.')

    if starting_date < date.today():
        return BadRequest('Invalid date, cannot create tournaments in the past.')

    user = authenticate_user()
    if not (user.is_admin() or user.is_director()):
        return Unauthorized('You are not authorized to create leagues')

    tournament = Tournament(title=title, prize=prize, format_id=format_id, winner=None)

    tournaments_service.create_league(
        tournament,
        participants=participants,
        starting_date=starting_date
    )

    return Successful("Success")

@tournaments_blueprint.put('/league/set_score/matchup/<int:league_id>')
def set_league_score(league_id: int) -> str:
    """
    Updates the scores for a specific matchup in a league tournament.
    Ensures the user is authorized and the matchup exists.
    """
    scores = request.get_json()
    score_one, score_two = scores.get('score_one', -1), scores.get('score_two', -1)

    if score_one < 0 or score_two < 0 or score_one == score_two:
        return BadRequest('Invalid scores: Ensure scores are positive and not equal.')

    user = authenticate_user()
    if not (user.is_admin() or user.is_director()):
        return Unauthorized('You are not authorized to set scores!')

    matchup = tournaments_service.get_matchup(league_id)
    if not matchup:
        return NoContent('Non existing matchup!')
    if not matchup.id:
        return BadRequest('Invalid matchup ID!')

    knockout = tournaments_service.get_by_tournament_id(matchup.tournament_id)
    if not knockout.format == "league":
        return "You can not set knockout tournament scores from here"

    tournaments_service.set_matchup_score(matchup.id, [score_one, score_two])

    return Successful("Scores updated successfully!")
