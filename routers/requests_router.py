"""
Module for handling user promotion requests.
"""

from flask import request, Blueprint, render_template, jsonify
from utils import authenticate_user
from services import user_service
from common.responses import NotFound, Unauthorized, BadRequest

requests_blueprint = Blueprint('requests', __name__, url_prefix='/requests')

@requests_blueprint.route('/', methods=['GET', 'POST'])
def promote_user():
    """
    Handle user promotion requests.

    GET: Render the promotion form.
    POST: Promote a user to the 'Director' role if the requesting user has sufficient permissions.
    """
    if request.method == 'GET':
        return render_template('promote_user.html')

    user = authenticate_user()
    if not user.is_admin() and not user.is_director():
        return Unauthorized("You do not have permission to promote users")

    data = request.get_json()
    user_id = data.get('user_id')
    user_to_promote = user_service.get_user_by_id(user_id)
    if not user_to_promote:
        return NotFound("User not found")

    if user_to_promote.is_admin() or user_to_promote.is_director():
        return BadRequest("User is already a director")

    updated = user_service.promote_to_director(user_to_promote)
    if updated:
        return jsonify({'message': f"User {user_to_promote.email} has been promoted to Director"})
    return BadRequest("Failed to promote user")
