"""
Service layer for player-related operations, including CRUD functionality,
team management, and player statistics.
"""

from data import database
from data.models import Player, User, UserInfo, PlayerData
from services import team_service

def country_names() -> list[str]:
    """Fetch all country names from the database."""
    names = database.read_query("SELECT name from country")
    return [i[0] for i in names]

def country_id(name: str) -> int:
    """Fetch the ID of a country given its name."""
    c_id = database.read_query("SELECT id from country where name = %s", (name,))
    return c_id[0][0]

def create_player(player: Player) -> Player | None:
    """Create a new player in the database."""
    if player.country not in country_names() or (player.team and player.team not in
                                                team_service.get_team_names()):
        return None

    team_id = team_service.get_team_id(player.team) if player.team else None
    generated_id = database.insert_query(
        """INSERT INTO player (first_name, second_name, team_id, country_id)
        VALUES (%s, %s, %s, %s)""",
        (player.first_name, player.second_name, team_id, country_id(player.country))
    )
    player.id = generated_id
    return player

def all_players(country: str = None, team: str = None) -> list[Player]:
    """Retrieve a list of players filtered by country or team."""
    query = """SELECT player.id, first_name, second_name, country.name, team.name
               FROM player
               LEFT JOIN team ON team_id = team.id
               LEFT JOIN country ON country_id = country.id"""
    params = ()

    if country and team:
        query += " WHERE team.name = %s AND country.name = %s"
        params = (team, country)
    elif country:
        query += " WHERE country.name = %s"
        params = (country,)
    elif team:
        query += " WHERE team.name = %s"
        params = (team,)

    players = database.read_query(query, params)
    return [Player.from_query_result(PlayerData(*p)) for p in players]

def get_player_by_id(player_id: int) -> Player | None:
    """Retrieve a player by their ID."""
    player = database.read_query(
        """SELECT player.id, first_name, second_name, country.name, team.name
           FROM player
           LEFT JOIN team ON team_id = team.id
           LEFT JOIN country ON country_id = country.id
           WHERE player.id = %s""",
        (player_id,)
    )

    player_data = PlayerData(*player[0])
    return Player.from_query_result(player_data) if player else None

def null_team(team_id: int) -> None:
    """Set the team_id of all players in a team to NULL."""
    database.update_query("UPDATE player set team_id = %s where team_id = %s",
        (None, team_id)
    )

def delete_player(player_id: int) -> None:
    """Delete a player by their ID."""
    database.update_query("DELETE from player where id = %s",
        (player_id,)
    )

def get_tournament_players(tournament_id: int) -> list[Player]:
    """
    Retrieve all players participating in a tournament.
    """
    player_data = database.read_query("""SELECT player_one, p.first_name, p.second_name,
        c.name, t.name, player_two, pt.first_name, pt.second_name, ct.name, tt.name
        from matchups 
        LEFT JOIN player as p on matchups.player_one = p.id 
        LEFT JOIN team as t on p.team_id = t.id 
        LEFT JOIN country as c on p.country_id = c.id
        LEFT JOIN player as pt on matchups.player_two = pt.id 
        LEFT JOIN team as tt on pt.team_id = tt.id 
        LEFT JOIN country as ct on pt.country_id = ct.id
        where tournament_id = %s and player_one is not NULL and player_two is not NULL""",
        (tournament_id,)
    )

    players = []
    for d in player_data:
        player_one_info = PlayerData(d[0], d[1], d[2], d[3], d[4])
        player_two_info = PlayerData(d[5], d[6], d[7], d[8], d[9])
        players.extend([Player.from_query_result(player_one_info),
                        Player.from_query_result(player_two_info)])

    unique_players = []
    for p in players:
        if p not in unique_players:
            unique_players.append(p)

    return unique_players

def get_player_by_name(fullname: str) -> Player | None:
    """Retrieve a player by their full name."""
    first_name, second_name = fullname.split(" ")

    data = database.read_query(
                '''SELECT * FROM player
                    WHERE first_name = %s and second_name = %s''', (first_name,second_name))

    if not data:
        return None
    player = data[0]
    player_info = PlayerData(player[0], player[1], player[2], str(player[3]), str(player[4]))
    return Player.from_query_result(player_info)

def create_player_by_name(fullname: str) -> None:
    """Create a player profile using only their name."""
    database.insert_query(
        """INSERT INTO player (first_name, second_name, team_id, country_id)
        values (%s,%s,%s,%s)""",
        (fullname[0], fullname[1], None, None)
    )

def create_unknown_participants_profile(participants: list[str]) -> list[list[str]]:
    """
    Create profiles for participants that do not already exist in the database.
    """
    players = all_players()
    existing_names = [[player.first_name, player.second_name] for player in players]
    new_names = []

    for participant in participants:
        participant_first_name, participant_second_name = participant.split(" ")
        if [participant_first_name, participant_second_name] not in existing_names:
            create_player_by_name([participant_first_name, participant_second_name])
            new_names.append([participant_first_name, participant_second_name])

    return new_names
