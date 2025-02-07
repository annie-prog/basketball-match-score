"""
Module for team-related routes, including adding, retrieving, and deleting teams.
"""

from flask import request, Blueprint, jsonify, render_template, redirect, url_for
from utils import authenticate_user
from services import team_service, player_service
from data.models import Team
from common.responses import BadRequest, NotFound, Successful, Unauthorized

team_blueprint = Blueprint('team', __name__, url_prefix='/team')

@team_blueprint.route('/', methods=['GET', 'POST'])
def add_team():
    """
    Handle adding a new team.

    GET: Render the add team form.
    POST: Add a new team to the database if the user is authorized.
    """
    if request.method == 'GET':
        return render_template('add_team.html')

    user = authenticate_user()
    if not user.is_admin() and not user.is_director():
        return Unauthorized("Only directors and admins can create teams")

    team_name = request.form.get('name')
    if not team_name:
        raise BadRequest("Team data is required")

    team = Team(name=team_name)
    result = team_service.create_team(team)

    if not result:
        return BadRequest("Team name already taken")

    role_route = f'user.dashboard_{user.role.lower()}'
    return redirect(url_for(role_route))

@team_blueprint.route('/all', methods=['GET'])
def all_teams():
    """
    Retrieve all teams as JSON.
    Returns:
        A JSON object containing a list of all teams.
    """
    teams = team_service.all_teams()
    teams_data = [{"id": team.id, "name": team.name} for team in teams]
    return jsonify({"teams": teams_data})

@team_blueprint.route('/<int:team_id>', methods=['DELETE'])
def delete_team(team_id: int):
    """
    Delete a team by its ID.
    Args:
        team_id (int): ID of the team to delete.
    Returns:
        JSON response indicating the result of the deletion.
    """
    user = authenticate_user()
    if not user.is_admin() and not user.is_director():
        return Unauthorized("Only directors and admins can delete teams")

    team = team_service.get_team_by_id(team_id)
    if not team:
        return NotFound("Team does not exist")

    player_service.null_team(team_id)
    team_service.delete_team(team_id)

    return Successful(f"Successfully deleted team {team_id} and updated players")
