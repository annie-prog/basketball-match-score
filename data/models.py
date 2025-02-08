"""
Module containing models and utilities for tournament-related data.
"""
from collections import namedtuple
from datetime import date
from enum import Enum
import re
from pydantic import BaseModel

PlayerData = namedtuple('PlayerData', ['id', 'first_name', 'second_name', 'country', 'team'])
UserInfo = namedtuple('UserInfo', ['id', 'email', 'password', 'role', 'name'])
PlayerMatchData = namedtuple(
    'PlayerMatchData', [
        'match_id', 'title', 'played_at', 'match_format_name', 'player_id', 'player_name'
    ]
)
TeamMatchData = namedtuple(
    'TeamMatchData', [
        'match_id', 'title', 'played_at', 'match_format_name', 'team_id', 'team_name'
    ]
)
TournamentData = namedtuple(
    'TournamentData', [
        'id', 'title', 'prize', 'format_id', 'winner', 'players', 'matchups'
    ]
)

class Team(BaseModel):
    """
    Represents a sports team.
    
    Attributes:
        id (int | None): The ID of the team.
        name (str): The name of the team.
    """
    id: int | None = None
    name: str

class Player(BaseModel):
    """
    Represents a player in the tournament.
    
    Attributes:
        id (int | None): The player's ID.
        first_name (str | None): The player's first name.
        second_name (str | None): The player's second name.
        country (str | None): The country the player represents.
        team (str | None): The team the player is associated with.
    """
    id: int | None = None
    first_name: str | None = None
    second_name: str | None = None
    country: str | None = None
    team: str | None = None

    @classmethod
    def from_query_result(cls, player_data: PlayerData) -> "Player":
        """
        Creates a Player instance from query results.
        """
        return cls(**player_data._asdict())

class Role(str, Enum):
    """
    Enum representing the possible roles a user can have.
    """
    ADM = "admin"
    USR = "user"
    DRC = "director"

class Sort(str, Enum):
    """
    Enum for sorting order in ascending or descending.
    """
    ASC = "asc"
    DESC = "desc"

class User(BaseModel):
    """
    Represents a user in the system.
    
    Attributes:
        id (int | None): The user's ID.
        email (str): The user's email.
        password (str): The user's password.
        role (Role | None): The user's role in the system (admin, user, or director).
    """
    id: int | None = None
    email: str
    password: str
    role: Role | None = None
    name : str

    def validate_email(self, values: dict) -> dict:
        """
        Validates the email format for the user.
        """
        email = values.get("email")
        if email:
            if not self.is_valid_email(email):
                raise ValueError(f"Invalid email format: {email}")
        return values

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Basic regex validation for an email.
        """
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return bool(re.match(email_regex, email))

    @classmethod
    def from_query_result(cls, user: UserInfo) -> "User":
        """
        Creates a User instance from database query results.
        """
        return cls(**user._asdict())

    def is_admin(self):
        """
        Checks if the user has admin privileges.
        """
        return self.role == "admin"

    def is_director(self):
        """
        Checks if the user has director privileges.
        """
        return self.role == "director"

class LogInfo(BaseModel):
    """
    Represents login information for a user.
    
    Attributes:
        email (str): The user's email.
        password (str): The user's password.
    """
    email: str
    password: str

    def validate_email(self, values: dict) -> dict:
        """
        Validates the email format for the login information.
        """
        email = values.get("email")
        if email:
            if not self.is_valid_email(email):
                raise ValueError(f"Invalid email format: {email}")
        return values

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Basic regex validation for an email.
        """
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return bool(re.match(email_regex, email))

class Status(str, Enum):
    """
    Enum representing the status of a request.
    """
    PENDING = "pending"
    DENIED = "denied"
    ACCEPTED = "accepted"

class Match(BaseModel):
    """
    Model representing a match in the tournament.

    Attributes:
        id (int | None): The unique identifier for the match.
        title (str | None): The title of the match.
        played_at (date): The date the match was played.
        match_format_id (int | None): The ID of the match format used in the match.
    """
    id: int | None = None
    title: str | None = None
    played_at: date = None
    match_format_id: int | None

    @classmethod
    def from_query_result(cls, match_id: int, title: str, played_at: date, match_format_id: int) -> "Match":
        """
        Creates a Match instance from query results.
        """
        return cls(
            id = match_id,
            title = title,
            played_at = played_at,
            match_format_id = match_format_id)

class PlayerMatch(BaseModel):
    """
    Model representing a player's involvement in a match.

    Attributes:
        match_id (int): The ID of the match.
        title (str): The title of the match.
        played_at (date): The date the match was played.
        match_format_name (str): The name of the match format.
        player_id (list[int]): A list of player IDs involved in the match.
        player_name (list[str]): A list of player names involved in the match.
    """
    match_id: int
    title: str
    played_at: date
    match_format_name: str
    player_id: list[int]
    player_name: list[str]

    @classmethod
    def from_query_result(cls, player_match: PlayerMatchData) -> "PlayerMatch":
        """
        Creates a PlayerMatch instance from query results.
        """
        return cls(**player_match._asdict())

class TeamMatch(BaseModel):
    """
    Model representing a match involving multiple teams.

    Attributes:
        match_id (int): The unique identifier for the match.
        title (str): The title or description of the match.
        played_at (date): The date the match was played.
        match_format_name (str): The name of the match format.
        team_id (list[int]): A list of team IDs participating in the match.
        team_name (list[str]): A list of team names participating in the match.
    """
    match_id: int
    title: str
    played_at: date
    match_format_name: str
    team_id: list[int]
    team_name: list[str]

    @classmethod
    def from_query_result(cls, team_match_data: TeamMatchData) -> "TeamMatch":
        """
        Creates a TeamMatch instance from query results.
        """
        return cls(**team_match_data._asdict())

class PlayerMatchInfo(BaseModel):
    """
    Model representing player-specific match information.

    Attributes:
        player_id (int): The unique identifier for the player.
        player_name (str): The name of the player.
        country_id (int | None): The ID of the player's country, if applicable.
        score (int): The player's score in the match.
    """
    player_id: int
    player_name: str
    country_id: int = None
    score: int

    @classmethod
    def from_query_result(cls,player_id: int, player_name: str, country_id: int, score: int) -> "PlayerMatchInfo":
        """
        Creates a PlayerMatchInfo instance from query results.
        """
        return cls(
            player_id=player_id,
            player_name=player_name,
            country_id=country_id,
            score=score if score is not None else 0
        )

class TeamMatchInfo(BaseModel):
    """
    Model representing team-specific match information.

    Attributes:
        team_id (int): The unique identifier for the team.
        team_name (str): The name of the team.
        score (int): The score of the team in the match.
    """
    team_id: int
    team_name: str
    score: int

    @classmethod
    def from_query_result(cls, team_id: int, team_name: str, score: int) -> "TeamMatchInfo":
        """
        Creates a TeamMatchInfo instance from query results.
        """
        return cls(
            team_id=team_id,
            team_name=team_name,
            score=score if score is not None else 0
        )

class MatchUpdate(BaseModel):
    """
    Model representing updates to a match.

    Attributes:
        title (str | None): The new title for the match, if provided.
        played_at (date): The new date the match was played, if updated.
    """
    title: str | None
    played_at: date

class MatchFormat(BaseModel):
    """
    Model representing the format of a match (e.g., players, teams).

    Attributes:
        id (int | None): The unique identifier for the match format.
        name (str): The name of the match format.
    """
    id: int | None
    name: str

    @classmethod
    def from_query_result(cls, match_format_id: int, name: str):
        """
        Creates a MatchFormat instance from query results.
        """
        return cls(
            id=match_format_id,
            name=name)

class PlayerMatchDetailUpdate(BaseModel):
    """
    Model for updating player details in a match.

    Attributes:
        player_ids (list[int]): A list of player IDs whose details are to be updated.
        score (list[int]): A list of scores corresponding to the players' IDs.
    """
    player_ids: list[int]
    score: list[int]

class TeamMatchDetailUpdate(BaseModel):
    """
    Model for updating team details in a match.

    Attributes:
        team_ids (list[int]): A list of team IDs whose details are to be updated.
        score (list[int]): A list of scores corresponding to the teams' IDs.
    """
    team_ids: list[int]
    score: list[int]

class MatchUp(BaseModel):
    """
    Model representing a matchup between players in a tournament.

    Attributes:
        id (int | None): The unique identifier for the matchup.
        tournament_id (int | None): The ID of the tournament the matchup is part of.
        played_at (date | None): The date the matchup is played, if available.
        tournament_phase (int | None): The phase of the tournament for this matchup.
        player_one (int | None): The ID of the first player.
        player_two (int | None): The ID of the second player.
        player_one_score (int | None): The score of the first player in the matchup.
        player_two_score (int | None): The score of the second player in the matchup.
    """
    id: int | None = None
    tournament_id: int | None = None
    played_at: date | None = None
    tournament_phase: int | None = None
    player_one: int | None = None
    player_two: int | None = None
    player_one_score: int | None = None
    player_two_score: int | None = None

class Tournament(BaseModel):
    """
    Model representing a tournament.

    Attributes:
        id (int | None): The unique identifier for the tournament.
        name (str): The name of the tournament.
        start_date (date): The start date of the tournament.
        end_date (date): The end date of the tournament.
        status (Status): The current status of the tournament (e.g., pending, denied, accepted).
        match_ids (list[int]): A list of match IDs associated with the tournament.
    """
    id: int | None = None
    title: str | None = None
    prize: str | None = None
    format_id: int | None = None
    winner: int | None = None
    players: list[Player] | None = []
    matchups:  list[MatchUp] | None = []

    @classmethod
    def from_query_result(cls, tournament_data: TournamentData) -> "Tournament":
        """
        Creates a Tournament instance from query results.
        """
        return cls(**tournament_data._asdict())

class TournamentResponseModel(BaseModel):
    """
    Model representing the response data for a tournament.

    Attributes:
        id (int | None): The unique identifier for the tournament.
        title (str): The title of the tournament.
        prize (str | None): The prize associated with the tournament, if applicable.
        format (str): The format of the tournament (e.g., knockout, league).
        winner (int | str): The ID or name of the winner of the tournament, if available.
        players (list[Player]): A list of players participating in the tournament, if available.
        matchups (list[MatchUp]): A list of matchups for the tournament, if available.
    """
    id: int | None
    title: str
    prize: str | None
    format: str
    winner: int | str | None
    players: list[Player] | None = []
    matchups:  list[MatchUp] | None = []
