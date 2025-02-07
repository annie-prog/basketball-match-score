"""
This module defines routes for handling match format operations.
"""

from flask import Blueprint, jsonify
from services import match_format_service

match_format_blueprint = Blueprint('match_format', __name__, url_prefix='/match_format')

@match_format_blueprint.route('/', methods=['GET'])
def all_formats():
    """
    Retrieve all match formats with their details.
    """
    formats = match_format_service.all_formats()
    formats_data = [
        {"id": format.id, "name": format.name}
        for format in formats
    ]
    return jsonify(formats_data)
