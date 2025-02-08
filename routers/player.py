"""
This module defines routes for managing players in the application. 
It includes functionality to add, retrieve, delete, and get statistics for players.
"""

from flask import request, Blueprint, render_template, redirect, url_for, jsonify
from utils import authenticate_user
from services import player_service
from data.models import Player
from common.responses import BadRequest, NotFound, Successful, Unauthorized

player_blueprint = Blueprint('player', __name__, url_prefix='/player')

@player_blueprint.route('/', methods=['GET', 'POST'])
def add_player():
    """
    Add a new player or render the form for adding a player.
    GET: Render the HTML form for adding a player.
    POST: Create a new player in the database.
    """
    if request.method == 'GET':
        return render_template('add_player.html')

    user = authenticate_user()

    first_name = request.form.get('first_name')
    second_name = request.form.get('second_name')
    country = request.form.get('country')
    team = request.form.get('team')

    if not first_name or not second_name:
        return BadRequest("First name and second name are required")

    player = Player(first_name=first_name, second_name=second_name, country=country, team=team)

    result = player_service.create_player(player)
    if not result:
        return BadRequest("Invalid team or player data")

    role_route = f'user.dashboard_{user.role.lower()}'
    return redirect(url_for(role_route))

@player_blueprint.route('/all', methods=['GET'])
def all_players():
    """
    Retrieve all players from the database.
    Returns:
        A JSON response containing details of all players.
    """
    players = player_service.all_players()
    players_data = [
        {
            "id": player.id,
            "first_name": player.first_name,
            "second_name": player.second_name,
            "country": player.country,
            "team": player.team
        }
        for player in players
    ]
    return jsonify({"players": players_data})

@player_blueprint.route('/<int:player_id>', methods=['DELETE'])
def delete_player(player_id: int) -> str:
    """
    Delete a player by their ID.
    Args:
        player_id (int): The ID of the player to delete.
    Returns:
        A success message if deleted, or an error if not authorized or player does not exist.
    """
    user = authenticate_user()

    exists = player_service.get_player_by_id(player_id)
    if not exists:
        return NotFound("Player does not exist")

    if not user.is_admin() and not user.is_director():
        return Unauthorized("Only directors and admins can delete players")

    player_service.delete_player(player_id)

    return Successful(f"Player with ID={exists} successfully deleted!")
