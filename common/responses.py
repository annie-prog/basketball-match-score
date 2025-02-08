"""
This module contains custom response classes for handling different 
HTTP status codes in the application.
"""

from flask import Response
from typing import Optional

class BadRequest(Response):
    """
    Represents a 400 Bad Request response with an optional content message.
    """
    def __init__(self, content: Optional[str] = '') -> None:
        super().__init__(response=content, status=400)

class NotFound(Response):
    """
    Represents a 404 Not Found response with an optional content message.
    """
    def __init__(self, content: Optional[str] = '') -> None:
        super().__init__(response=content, status=404)

class Unauthorized(Response):
    """
    Represents a 401 Unauthorized response with an optional content message.
    """
    def __init__(self, content: Optional[str] = '') -> None:
        super().__init__(response=content, status=401)

class NoContent(Response):
    """
    Represents a 204 No Content response with no content in the response body.
    """
    def __init__(self) -> None:
        super().__init__(response='', status=204)

class InternalServerError(Response):
    """
    Represents a 500 Internal Server Error response with no content in the response body.
    """
    def __init__(self) -> None:
        super().__init__(response='', status=500)

class Successful(Response):
    """
    Represents a 200 OK response with an optional content message.
    """
    def __init__(self, content: Optional[str] = '') -> None:
        super().__init__(response=content, status=200)
