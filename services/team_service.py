"""
This module handles the operations for managing teams, such as creating, fetching,
deleting, and listing team data.
"""

from data import database
from data.models import Team

def create_team(team: Team):
    """
    Creates a new team if it does not already exist.
    """
    existing_team = database.read_query(
        "SELECT * FROM team WHERE name=%s", 
        (team.name,)
    )
    if existing_team:
        return None

    generated_id = database.insert_query(
        "INSERT INTO team (name) VALUES (%s) RETURNING id", 
        (team.name,)
    )
    team.id = generated_id

    return team

def all_teams():
    """
    Retrieves all teams from the database.
    """
    query = database.read_query("SELECT * from team")
    return (Team(id=t[0], name=t[1]) for t in query)

def get_team_by_id(team_id: int):
    """
    Retrieves a team by its ID.
    """
    query = database.read_query("SELECT * FROM team WHERE id = %s", (team_id,))
    if not query:
        return None
    return [Team(id=t[0], name=t[1]) for t in query]

def get_team_names():
    """
    Retrieves the names of all teams.
    """
    team_names = database.read_query("SELECT name from team")
    return [i[0] for i in team_names]

def get_team_id(name: str):
    """
    Retrieves a team's ID by its name.
    """
    team_id = database.read_query("SELECT id from team where name = %s", (name,))
    return team_id[0][0]

def delete_team(team_id: int):
    """
    Deletes a team by its ID.
    """
    database.update_query("DELETE from team where id = %s", (team_id,))
