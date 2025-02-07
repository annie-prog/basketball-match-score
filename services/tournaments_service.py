"""
Module for managing tournaments, matchups, and league standings in a sports event.
Includes functions for tournament creation, updating, retrieving details, 
and handling knockout and league formats.
"""

from datetime import date, timedelta
from flask import jsonify
from data.models import (MatchUp, Tournament,
                        TournamentResponseModel)
from data.database import insert_query, read_query, update_query
from services import player_service

def all_tournaments():
    """
    Retrieves all tournaments and returns them as a list of dictionaries,
    including the full name of the winner.
    """
    data = read_query(
        '''SELECT t.id, t.title, t.prize, t.tournament_format_id, 
                  p.first_name, p.second_name,
                  m.player_one, m.player_two, m.id as match_id
           FROM tournament AS t
           LEFT JOIN player AS p ON t.winner = p.id
           LEFT JOIN matchups AS m ON m.tournament_id = t.id'''
    )

    flattened = {}
    for (tour_id, title, prize, tournament_format, first_name, second_name,
        player_one, player_two, match_id) in data:
        if tour_id not in flattened:
            winner_name = f"{first_name} {second_name}" if first_name else "No winner yet"
            flattened[tour_id] = {
                "id": tour_id,
                "title": title,
                "prize": prize,
                "tournament_format": tournament_format,
                "winner": winner_name,
                "players": [],
                "matches": []
            }
        if player_one is not None and player_one not in flattened[tour_id]["players"]:
            flattened[tour_id]["players"].append(player_one)
        if player_two is not None and player_two not in flattened[tour_id]["players"]:
            flattened[tour_id]["players"].append(player_two)
        if match_id is not None:
            flattened[tour_id]["matches"].append(match_id)

    return list(flattened.values())

def get_matchup(matchup_id: int):
    """
    Retrieves a specific matchup by its ID.
    """
    data = read_query(
        """SELECT id, tournament_id, played_at, tournament_phase, player_one, 
        player_two, player_one_score, player_two_score from matchups
        where id = %s""",
        (matchup_id,)
    )
    if not data:
        return None
    m = data[0]
    return MatchUp(
        id=m[0],tournament_id=m[1], played_at=m[2], tournament_phase=m[3],
        player_one=m[4], player_two=m[5], player_one_score=m[6], player_two_score=m[7]
    )

def get_tournament_matchups(tournament_id: int):
    """
    Retrieves all matchups for a specific tournament.
    """
    data = read_query(
        """SELECT * from matchups
        where tournament_id = %s order by tournament_phase""",
        (tournament_id,)
    )
    if not data:
        return None
    return [
        MatchUp(id=m[0],tournament_id=m[1], played_at=m[2], tournament_phase=m[3],
            player_one=m[4], player_two=m[5], player_one_score=m[6], player_two_score=m[7]
        )
        for m in data
    ]

def get_by_tournament_id(tournament_id: int):
    """
    Retrieves detailed tournament information, including matchups and players, by tournament ID.
    """
    tournament_data = read_query(
        '''SELECT  t.id, title, t.prize, t.tournament_format_id, t.winner
        FROM tournament as t WHERE t.id = %s''',
        (tournament_id,)
    )

    players = player_service.get_tournament_players(tournament_id)
    matchups = get_tournament_matchups(tournament_id) or []
    tournament_format = get_tournament_format(tournament_id)

    if not tournament_data:
        return None
    tournament_data = tournament_data[0]

    return TournamentResponseModel(
        id=tournament_data[0], title=tournament_data[1], prize=tournament_data[2],
        format=tournament_format,winner=tournament_data[4],players=players,
        matchups=matchups
    )

def get_tournament_format(tournament_id: int):
    """
    Retrieves the format of a tournament by its ID.
    """
    data = read_query(
                '''SELECT  t_f.name
                    FROM tournament_format as t_f
                    LEFT JOIN tournament as t
                    ON t_f.id = t.tournament_format_id
                    WHERE t.id = %s''', (tournament_id,))
    if not data:
        return None
    tournament_format = data[0]
    return tournament_format[0]

def check_for_existing_player(player_id: int):
    """
    Checks if a player exists by their ID.
    """
    return any(read_query('select * from player where id = %s',(player_id,)))

def create_tournament(tournament: Tournament):
    """
    Creates a new tournament and inserts it into the database.
    """
    generated_id = insert_query(
        "INSERT INTO tournament (title, prize, tournament_format_id) values (%s,%s,%s)",
        (tournament.title, tournament.prize, tournament.format_id)
    )
    tournament.id = generated_id
    return tournament

def create_random_matchups(tournament: Tournament, home: str, away: str, starting_date: date):
    """
    Creates a random matchup between two players and inserts it into the matchups table.
    """
    player1 = player_service.get_player_by_name(home)
    player2 = player_service.get_player_by_name(away)

    insert_query('''insert into matchups (tournament_id, played_at, tournament_phase,
        player_one, player_two, player_one_score, player_two_score)
        values (%s, %s, %s, %s, %s, %s, %s)''',
        (tournament.id, starting_date, 1, player1.id, player2.id, None, None)
    )

def create_empty_matchup(tournament: Tournament, matchup_date: date, phase: int):
    """
    Creates an empty matchup entry in the database for the given tournament and phase.
    """
    insert_query('''insert into matchups (tournament_id, played_at, tournament_phase,
        player_one, player_two, player_one_score, player_two_score)
        values (%s, %s, %s, %s, %s, %s, %s)''',
        (tournament.id, matchup_date, phase, None, None, None, None)
    )

def create_empty_phase(tournament: Tournament, tournament_date: date, phase: int, p_count: int):
    """
    Creates empty matchups for a specific phase in a tournament.
    """
    matchup_count = p_count//2
    for _ in range(matchup_count):
        create_empty_matchup(tournament, tournament_date, phase)

def create_knockout_tournament(tournament: Tournament,
                               participants: list[str], starting_date: date):
    """
    Creates a knockout tournament with matchups based on the given participants and starting date.
    """
    try:
        participant_ids = [int(pid) for pid in participants]
    except ValueError:
        print("Participants must be a comma-separated list of numeric IDs.")

    if len(participant_ids) not in [4, 8, 16, 32, 64, 128, 256]:
        return jsonify({"error": "Participants should be 4, 8, 16, 32, 64, 128 or 256 count!"}), 401

    players = []
    for player_id in participant_ids:
        player = player_service.get_player_by_id(player_id)
        if player is None:
            raise ValueError(f"Player with ID '{player_id}' does not exist.")
        players.append(player)

    create_tournament(tournament)

    phase = 1
    p_count = len(players) // 2
    while len(players) > 1:
        player1 = players[0].first_name + ' ' + players[0].second_name
        player2 = players[1].first_name + ' ' + players[1].second_name
        create_random_matchups(tournament, player1,
                               player2, starting_date)
        players.pop(0)
        players.pop(0)

    while p_count > 1:
        create_empty_phase(tournament, starting_date, phase, p_count)
        phase += 1
        p_count //= 2

    return jsonify({"message": "Knockout tournament created successfully!"}), 201

def set_matchup_score(matchup_id: int, scores: list[int]):
    """
    Updates the scores for a given matchup.
    """
    update_query('''
        UPDATE matchups
        SET player_one_score = %s, player_two_score = %s
        WHERE id = %s''',
        (scores[0], scores[1], matchup_id)
    )

def get_matchup_ids_next_phase(matchup: MatchUp):
    """
    Retrieves the matchup IDs for the next phase of the tournament.
    """
    data = read_query("SELECT id from matchups where tournament_id = %s and tournament_phase = %s",
                    (matchup.tournament_id, matchup.tournament_phase + 1)
                )

    return [i[0] for i in data]

def get_right_id(matchup: MatchUp, current_ids: list[list[int]], next_ids: list[int]):
    """
    Retrieves the ID of the correct next matchup for a given current matchup.
    """
    if len(next_ids) > 0:
        target_id = next((i for i in range(len(current_ids)) if matchup.id in current_ids[i]), None)
        return next_ids[target_id] if target_id is not None else None

    return None

def create_phase(league: Tournament, participants: list[str], phase, starting_date: date):
    """
    Creates a phase with matchups for a league tournament.
    """
    phase %= (len(participants)-1)
    if phase:
        participants = participants[:1] + participants[-phase:] + participants[1:-phase]
    half = len(participants)//2
    phase_matchups = list(zip(participants[:half], participants[half:][::-1]))

    for m in phase_matchups:
        player1 = m[0].first_name + ' ' + m[0].second_name
        player2 = m[1].first_name + ' ' + m[1].second_name
        player_one = player_service.get_player_by_name(player1)
        player_two = player_service.get_player_by_name(player2)

        insert_query('''insert into matchups
            (tournament_id, played_at, tournament_phase, player_one, player_two,
            player_one_score, player_two_score)
            values (%s, %s, %s, %s, %s, %s, %s)''',
            (league.id, starting_date+timedelta(days=7*phase), phase + 1,
                player_one.id, player_two.id, None, None)
        )

def get_phases(participants: list[str]):
    """
    Retrieves the phases for a league tournament based on the number of participants.
    """
    phase = 1
    phases = [phase+1*i for i in range(len(participants)-1)]
    return phases

def create_league(league: Tournament, participants: list[str], starting_date: date):
    """
    Creates a league tournament with phases and matchups based on the participants.
    """
    try:
        participant_ids = [int(pid) for pid in participants]
    except ValueError:
        print("Participants must be a comma-separated list of numeric IDs.")

    players = []
    for player_id in participant_ids:
        player = player_service.get_player_by_id(player_id)
        if player is None:
            raise ValueError(f"Player with ID '{player_id}' does not exist.")
        players.append(player)

    create_tournament(league)

    days = get_phases(players)
    for day in days:
        create_phase(league, players, day, starting_date)

def get_league_tournament_matchups(tournament_id: int):
    """
    Retrieves all matchups for a given tournament.
    """
    data = read_query("SELECT * FROM match_score.matchups where tournament_id = %s",
                (tournament_id,)
            )
    if not data:
        return None

    return [MatchUp(id=m[0],tournament_id=m[1], played_at=m[2], tournament_phase=m[3],
    player_one=m[4], player_two=m[5], player_one_score=m[6], player_two_score=m[7]) for m in data]

def set_tournament_winner(tournament_id: int, winner_id: int) -> bool:
    """
    Updates the tournament table to set a winner for a given tournament.
    """
    result = update_query('''
        UPDATE tournament
        SET winner = %s
        WHERE id = %s''',
        (winner_id, tournament_id)
    )

    return result > 0
