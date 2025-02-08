"""
This module defines routes for managing and interacting with player and team matches.

It provides endpoints for:
- Retrieving all player and team matches
- Getting details of specific matches (player or team)
- Creating new matches (player or team)
- Updating match details, scores, and more

Authentication and authorization are handled via user tokens, ensuring that
only authorized users (admins or directors) can perform certain actions.
"""

from datetime import datetime, date
from flask import request, Blueprint, render_template
from services import match_service, team_service
from data.models import PlayerMatchDetailUpdate, Match, TeamMatchDetailUpdate, Sort
from utils import authenticate_user
from common.responses import BadRequest, NotFound, Unauthorized, Successful, InternalServerError

match_blueprint = Blueprint('match', __name__, url_prefix='/match')

@match_blueprint.get('/playerMatch')
def get_all_player_matches(sort: Sort | None = None) -> list[dict[str, str | int]]:
    """
    Retrieve all player matches, optionally sorted.
    """
    matches = match_service.all_player_matches()
    sorted_matches = match_service.sort(matches, reverse=sort == 'desc') if sort else matches

    return [
        {
            "match_id": match.match_id,
            "title": match.title,
            "played_at": match.played_at,
            "match_format_name": match.match_format_name,
            "players": match.player_name,
        }
        for match in sorted_matches
    ]

@match_blueprint.get('/teamMatch')
def get_all_team_matches(sort: str | None = None) -> list[dict[str, str | int]]:
    """
    Retrieve all team matches, optionally sorted.
    """
    matches = match_service.all_team_matches()
    sorted_matches = match_service.sort(matches, reverse=sort == 'desc') if sort else matches

    return [
        {
            "match_id": match.match_id,
            "title": match.title,
            "played_at": match.played_at,
            "match_format_name": match.match_format_name,
            "players": match.team_name,
        }
        for match in sorted_matches
    ]

@match_blueprint.route('/playerMatches/', methods=['GET', 'POST'])
def create_player_match() -> str:
    """
    Create a player match or render the form for adding a match.
    """
    if request.method == 'GET':
        return render_template('add_player_match.html')

    data = request.get_json()
    participants = data.get('participants', [])
    user = authenticate_user()

    error_message = None
    if len(participants) < 2:
        error_message = "At least 2 players are required to create a match."
    elif not user.is_admin() and not user.is_director():
        error_message = "Insufficient permissions to create a match."
    elif not data.get('title'):
        error_message = "Match title is required."
    else:
        try:
            played_at = datetime.strptime(data.get('played_at'), '%Y-%m-%d').date()
            if played_at < date.today():
                error_message = "Match date cannot be in the past."
        except ValueError:
            error_message = "Match date must be in the format 'YYYY-MM-DD'."

    if error_message:
        return BadRequest(error_message)

    try:
        match = Match(
            title=data.get('title'),
            played_at=data.get('played_at'),
            match_format_id=data.get('match_format_id'),
        )
        match_service.create_match_with_players(match, participants)
        return Successful("Match created successfully!")
    except ValueError as e:
        return BadRequest(f"Error: {e}")

@match_blueprint.route('/teamMatches/', methods=['GET', 'POST'])
def create_team_match() -> str:
    """
    Create a team match or render the form for adding a team match.
    """
    if request.method == 'GET':
        return render_template('add_team_match.html')

    data = request.get_json()
    teams = data.get('teams', [])
    user = authenticate_user()

    error_message = None
    if len(teams) < 2:
        error_message = "At least 2 teams are required to create a match."
    elif not user.is_admin() and not user.is_director():
        error_message = "Insufficient permissions to create a match."
    elif not data.get('title'):
        error_message = "Match title is required."
    elif any(team not in team_service.get_team_names() for team in teams):
        invalid_team = next(team for team in teams if team not in team_service.get_team_names())
        error_message = f"No such team: {invalid_team}"
    else:
        try:
            played_at = datetime.strptime(data.get('played_at'), '%Y-%m-%d').date()
            if played_at < date.today():
                error_message = "Match date cannot be in the past."
        except ValueError:
            error_message = "Match date must be in the format 'YYYY-MM-DD'."

    if error_message:
        return BadRequest(error_message)

    try:
        match = Match(
            title=data.get('title'),
            played_at=data.get('played_at'),
            match_format_id=data.get('match_format_id'),
        )
        match_service.create_with_teams(match, teams)
        return Successful("Match created successfully!")
    except ValueError as e:
        return BadRequest(f"Validation error: {e}")

@match_blueprint.put('/playerMatchScore/<int:match_id>')
def update_player_match_score(match_id: int) -> str:
    """
    Update player match scores.
    """
    user = authenticate_user()

    if not user.is_admin() and not user.is_director():
        return Unauthorized("Insufficient permissions to update the match.")

    try:
        data = request.get_json()

        if not isinstance(data, dict):
            return BadRequest("Invalid request format. Expected a JSON object.")

        if "player_id" in data:
            data["player_ids"] = data.pop("player_id")

        if isinstance(data.get("player_ids"), int):
            data["player_ids"] = [data["player_ids"]]
        if isinstance(data.get("score"), (int, str)):
            data["scores"] = [int(data["score"])]

        match_update = PlayerMatchDetailUpdate(**data)
    except ValueError as e:
        return BadRequest(f"Invalid value: {str(e)}")

    match = match_service.get_with_players(match_id)
    if not match:
        return NotFound('No such match!')

    try:
        match_service.update_player_match_score(match_id, match_update)
        return Successful("Player match scores updated successfully!")
    except RuntimeError as e:
        return InternalServerError(f"Failed to update match scores: {str(e)}")

@match_blueprint.put('/teamMatchScore/<int:team_id>')
def update_team_match_score(team_id: int) -> str:
    """
    Update team match scores.
    """
    user = authenticate_user()

    if not user.is_admin() and not user.is_director():
        return Unauthorized("Insufficient permissions to update the match.")

    try:
        data = request.get_json()

        if not isinstance(data, dict):
            return BadRequest("Invalid request format. Expected a JSON object.")

        if "team_id" in data:
            data["team_ids"] = data.pop("team_id")

        if isinstance(data.get("team_ids"), int):
            data["team_ids"] = [data["team_ids"]]
        if isinstance(data.get("score"), (int, str)):
            data["scores"] = [int(data["score"])]

        match_update = TeamMatchDetailUpdate(**data)
    except ValueError as e:
        return BadRequest(f"Invalid request data: {str(e)}")

    match = match_service.get_with_teams(team_id)
    if not match:
        return NotFound('No such match!')

    match_service.update_team_match_score(team_id, match_update)
    return Successful("Team match score updated successfully!")
