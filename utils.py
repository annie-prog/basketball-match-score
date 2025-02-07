"""
This module handles user authentication by extracting and validating JWT tokens.
"""

from flask import request, redirect, url_for
import jwt
from services import user_service
from common.responses import Unauthorized

def extract_token_from_request():
    """
    Extract the token from the request headers.
    """
    cookie_header = request.headers.get('Cookie')

    if cookie_header is None:
        return None

    cookie_pairs = [item.split('=') for item in cookie_header.split('; ') if '=' in item]
    cookies = {pair[0]: pair[1] for pair in cookie_pairs}
    return cookies.get('access_token')

def authenticate_user():
    """
    Extract the token from the request, validate it, and return the user.
    Handles expired token by redirecting to home page.
    """
    token = extract_token_from_request()

    try:
        user_auth = user_service.from_token(token)
    except jwt.exceptions.ExpiredSignatureError:
        return redirect(url_for('home'))

    if not user_auth:
        raise Unauthorized('Invalid token')

    return user_service.find_user(user_auth)
