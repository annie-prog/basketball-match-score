"""
This module provides user-related services for a sports management application. 
It includes functionalities for user authentication, creating and managing user 
profiles, promoting users to specific roles, and linking user accounts with player 
profiles.
"""

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from hashlib import blake2s
import jwt
import os
from data.models import LogInfo, User, UserInfo
from data import database

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SALT = os.getenv("SALT")
ALGO = os.getenv("ALGO")

def _hash(password: str):
    """Hashes the password using blake2s with a salt."""
    password += SALT
    return blake2s(password.encode()).hexdigest()

def create_token(user: User):
    """Generates a JWT token for the given user."""
    expiration = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {
        "email": user.email,
        "password": user.password,
        "role": user.role,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGO)
    return token

def from_token(token: str):
    """Decodes a JWT token into a LogInfo object."""
    decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGO)
    return LogInfo(email=decoded["email"], password=decoded["password"])

def create_user(loginfo: LogInfo, name: str, role: str = "user"):
    """Creates a new user in the database."""
    if role not in ["user", "admin", "director"]:
        raise ValueError(f"Invalid role: {role}")

    h_password = _hash(loginfo.password)

    query = """INSERT INTO users (email, password, role, name)
               VALUES (%s, %s, %s, %s)"""

    generated_id = database.insert_query(query,
                                         (loginfo.email, h_password, role, name))

    user_info = UserInfo(generated_id, loginfo.email, h_password, role, name)

    return User.from_query_result(user_info)

def find_user(loginfo: LogInfo):
    """Finds a user by their email and password."""
    h_password = _hash(loginfo.password)

    query = "SELECT * from users where email = %s and password = %s"
    user = database.read_query(query, (loginfo.email, h_password))
    if not user:
        return None
    user = user[0]

    user_info = UserInfo(user[0], user[1], loginfo.password, user[3], user[4])

    return User.from_query_result(user_info)

def promote_to_director(user: User):
    """Promotes a user to the director role."""
    updated = database.update_query(
        "UPDATE users SET role = %s WHERE id = %s", 
        ('director', user.id)
    )
    return updated > 0

def all_users():
    """Fetches all users from the database."""
    query = database.read_query("SELECT * FROM users")
    return [User.from_query_result(UserInfo(*row)) for row in query]

def get_user_by_id(user_id: int):
    """Fetches a user by their ID."""
    data = database.read_query("SELECT * from users where id = %s", (user_id,))
    user = data[0]
    if not user:
        return None

    user_info = UserInfo(user[0], user[1], user[2], user[3], user[4])

    return User.from_query_result(user_info)

def delete_user(user_id: int):
    """Delete a user by their ID."""
    database.update_query("DELETE from users where id = %s",
        (user_id,)
    )
