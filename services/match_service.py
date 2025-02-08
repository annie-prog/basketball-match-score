"""
This module provides services for managing match data, including functionalities 
for fetching and updating match details, as well as managing player and team match 
statistics. It interfaces with the database to read and write match-related data.
"""

from data.database import read_query, insert_query, update_query
from data.models import (
    Match, PlayerMatchDetailUpdate, TeamMatchDetailUpdate, TeamMatchInfo,
    PlayerMatchInfo, TeamMatch, PlayerMatch, TeamMatchData, PlayerMatchData
)
from services import player_service, team_service

def all_player_matches() -> tuple:
    """
    Fetches all player matches from the database. Optionally filters matches based 
    on the provided search string.
    """
    data = read_query(
        '''SELECT m.id as match_id, title, played_at, mf.name as match_format_name, 
            p.id as player_id, 
            concat(p.first_name,' ', p.second_name) as player_name
            FROM match AS m 
            LEFT JOIN player_match_detail AS pmd ON m.id = pmd.match_id
            JOIN player as p ON p.id = pmd.player_id
            LEFT JOIN match_format as mf ON m.match_format_id = mf.id''')

    flattened = {}
    for match_id, title, played_at, match_format_name, player_id, player_name in data:
        if match_id not in flattened:
            flattened[match_id] = (match_id, title, played_at, match_format_name, [], [])

        if player_id not in flattened:
            flattened[match_id][-2].append(player_id)

        if player_name not in flattened:
            flattened[match_id][5].append(player_name)

    return (PlayerMatch.from_query_result(PlayerMatchData(*obj)) for obj in flattened.values())

def all_team_matches() -> tuple:
    """
    Fetches all team matches from the database. Optionally filters matches based 
    on the provided search string.
    """
    data = read_query(
        '''SELECT m.id as match_id, title, played_at, mf.name as match_format_name, 
            t.id as team_id, t.name as team_name
            FROM match AS m 
            LEFT JOIN team_match_detail AS tmd ON m.id = tmd.match_id
            JOIN team as t ON t.id = tmd.team_id
            LEFT JOIN match_format as mf ON m.match_format_id = mf.id''')

    flattened = {}
    for match_id, title, played_at, match_format_name, team_id, team_name, in data:
        if match_id not in flattened:
            flattened[match_id] = (match_id, title, played_at, match_format_name, [], [])

        if team_id not in flattened:
            flattened[match_id][-2].append(team_id)

        if team_name not in flattened:
            flattened[match_id][5].append(team_name)

    return (TeamMatch.from_query_result(TeamMatchData(*obj)) for obj in flattened.values())

def sort(categories: list[Match], *, attribute="title", reverse=False) -> list:
    """
    Sorts a list of Match objects by a specified attribute.
    """
    if attribute == 'title':
        def sort_fn(m: Match):
            return m.title
    elif attribute == "match_format_id":
        def sort_fn(m: Match):
            return m.match_format_id
    elif attribute == "played_at":
        def sort_fn(m:Match):
            return m.played_at
    else:
        def sort_fn(m: Match):
            return m.id

    return sorted(categories, key=sort_fn, reverse=reverse)

def get_with_players(match_id: int) -> dict | None:
    """
    Retrieves match details along with player information for a specific match.
    """
    match_data = read_query(
        'select id, title, played_at, match_format_id from match where id = %s', (match_id,))

    match = next((Match.from_query_result(*row) for row in match_data), None)

    if match is None:
        return None

    players_data = read_query(
        '''SELECT player_id, concat(p.first_name, ' ', p.second_name) as name, 
            p.country_id, pmd.score
           FROM player p
           LEFT JOIN player_match_detail as pmd ON p.id = pmd.player_id
           WHERE pmd.match_id = %s''',
        (match.id,))

    return create_player_response_object(
        match,
        [PlayerMatchInfo.from_query_result(*row) for row in players_data])

def create_player_response_object(match: Match, players: list[PlayerMatchInfo]) -> dict:
    """
    Creates a response object for a match with associated player information.
    """
    return {
        'match_id': match.id,
        'title': match.title,
        'played_at': match.played_at,
        "format_id": match.match_format_id,
        'participants': players
    }

def get_with_teams(match_id: int) -> dict | None:
    """
    Retrieves match details along with team information for a specific match.
    """
    match_data = read_query(
        'select id, title, played_at, match_format_id from match where id = %s', (match_id,))
    match = next((Match.from_query_result(*row) for row in match_data), None)

    if match is None:
        return None

    players_data = read_query(
        '''SELECT t.id, t.name, tmd.score
	FROM team t
		LEFT JOIN team_match_detail as tmd ON t.id = tmd.team_id
               WHERE match_id = %s''',
        (match.id,))

    return create_team_response_object(
        match,
        [TeamMatchInfo.from_query_result(*row) for row in players_data])

def create_team_response_object(match: Match, teams: list[TeamMatchInfo]) -> dict:
    """
    Creates a response object for a match with associated team information.
    """
    return {
        'match_id': match.id,
        'title': match.title,
        'played_at': match.played_at,
        "format_id": match.match_format_id,
        'participants': teams
    }

def create_match_with_players(match: Match, participants: list[dict]) -> None:
    """
    Creates a new match and associates it with a list of player participants.
    """
    match_players = []
    for player_info in participants:
        if "name" in player_info:
            player_id = player_info["name"]
        else:
            raise ValueError(f"Invalid participant data: {player_info}. 'id' required.")

        player = player_service.get_player_by_id(player_id)
        if player is None:
            raise ValueError(f"Player with ID '{player_id}' does not exist.")
        match_players.append(player)

    generated_id = insert_query(
        'INSERT INTO match (title, played_at, match_format_id) VALUES (%s, %s, %s) RETURNING id',
        (match.title, match.played_at, match.match_format_id)
    )
    match.id = generated_id

    for player in match_players:
        insert_query(
            'INSERT INTO player_match_detail (player_id, match_id) VALUES (%s, %s)',
            (player.id, match.id)
        )

def create_with_teams(match: Match, teams: list[str]) -> None:
    """
    Creates a new match and associates it with a list of team participants.
    """
    generated_id = insert_query(
        'INSERT INTO match (title, played_at, match_format_id) VALUES (%s,%s,%s)',
        (match.title, match.played_at, match.match_format_id))
    match.id = generated_id

    team_ids = [team_service.get_team_id(t) for t in teams]
    for team_id in team_ids:
        insert_query(
            'INSERT INTO team_match_detail (team_id, match_id) VALUES (%s,%s)',
            (team_id, match.id)
        )

def player_match_exists(match_id: int, player_id: int) -> bool:
    """
    Checks if a specific player has a record for a given match.
    """
    data = read_query(
        'SELECT 1 FROM player_match_detail WHERE match_id = %s AND player_id = %s',
        (match_id, player_id)
    )
    return len(data) > 0

def match_exists(match_id: int) -> bool:
    """
    Checks if a match exists in player_match_detail.
    """
    data = read_query(
        'SELECT 1 FROM player_match_detail WHERE match_id = %s LIMIT 1',
        (match_id,)
    )
    return len(data) > 0

def update_player_match_score(match_id: int, match_update: PlayerMatchDetailUpdate) -> None:
    """
    Updates the scores for player participants in a specific match.
    If a player does not already have a record for the match, a new entry is created.
    """
    if not match_exists(match_id):
        raise ValueError(f"Match {match_id} does not exist in player_match_detail!")

    for player, score in zip(match_update.player_ids, match_update.score):
        if player_match_exists(match_id, player):
            update_query(
                """UPDATE player_match_detail
                   SET score = %s 
                   WHERE player_id = %s AND match_id = %s""",
                (score, player, match_id)
            )
        else:
            insert_query(
                """INSERT INTO player_match_detail (player_id, match_id, score) 
                   VALUES (%s, %s, %s)""",
                (player, match_id, score)
            )

def update_team_match_score(match_id: int, match_update: TeamMatchDetailUpdate) -> None:
    """
    Updates the scores for team participants in a specific match.
    """
    for team, score in zip(match_update.team_ids, match_update.score):
        match = update_query("""UPDATE team_match_detail
            SET score = %s WHERE team_id = %s and match_id = %s""",
            (score, team, match_id)
        )

    return match
