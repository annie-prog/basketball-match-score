"""
This module contains unit tests for the match service functionality in the sports management system.
"""

import unittest
from unittest.mock import patch, MagicMock
from services import match_service
from data.models import Match, PlayerMatchDetailUpdate, TeamMatchDetailUpdate

class TestMatchService(unittest.TestCase):
    """
    Test case for the match_service functions. 
    Includes tests for sorting matches, creating player/team response objects, 
    and handling match creation and score updates.
    """
    def test_sort_matches_by_match_format_id(self):
        """
        Test sorting of matches by their match_format_id attribute.
        """
        matches = [
            Match(id=1, title="B Match", played_at="2025-01-01", match_format_id=2),
            Match(id=2, title="A Match", played_at="2025-02-01", match_format_id=1),
        ]

        sorted_matches = match_service.sort(matches, attribute="match_format_id")
        self.assertEqual(sorted_matches[0].match_format_id, 1)
        self.assertEqual(sorted_matches[1].match_format_id, 2)

    @patch('services.match_service.read_query')
    def test_all_player_matches(self, mock_read_query):
        """
        Test retrieval of all player matches.
        """
        mock_read_query.return_value = [
            (1, 'Match 1', '2025-01-01', 'Format A', 1, 'Player 1'),
            (1, 'Match 1', '2025-01-01', 'Format A', 2, 'Player 2'),
            (2, 'Match 2', '2025-02-01', 'Format B', 3, 'Player 3'),
        ]

        result = list(match_service.all_player_matches())

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].match_id, 1)
        self.assertIn('Player 1', list(result[0].player_name))
        self.assertIn('Player 2', list(result[0].player_name))

    @patch('services.match_service.PlayerMatchInfo.from_query_result')
    def test_create_player_response_object(self, mock_from_query_result):
        """
        Test creation of a player response object from match and player data.
        """
        match = MagicMock(id=1, title="Match 1", played_at="2025-01-01", match_format_id=1)
        players = [MagicMock(name="Player 1"), MagicMock(name="Player 2")]

        mock_from_query_result.return_value = MagicMock(name="PlayerMatchInfo")

        result = match_service.create_player_response_object(match, players)

        self.assertEqual(result['match_id'], 1)
        self.assertEqual(result['title'], "Match 1")
        self.assertEqual(result['played_at'], "2025-01-01")
        self.assertEqual(len(result['participants']), 2)

    @patch('services.match_service.TeamMatchInfo.from_query_result')
    def test_create_team_response_object(self, mock_from_query_result):
        """
        Test creation of a team response object from match and team data.
        """
        match = MagicMock(id=1, title="Match 1", played_at="2025-01-01", match_format_id=1)
        teams = [MagicMock(name="Team A"), MagicMock(name="Team B")]

        mock_from_query_result.return_value = MagicMock(name="TeamMatchInfo")

        result = match_service.create_team_response_object(match, teams)

        self.assertEqual(result['match_id'], 1)
        self.assertEqual(result['title'], "Match 1")
        self.assertEqual(result['played_at'], "2025-01-01")
        self.assertEqual(len(result['participants']), 2)

    @patch('services.match_service.player_service.get_player_by_id')
    def test_create_match_with_players_invalid_participant(self, mock_get_player):
        """
        Test creation of a match with invalid player participant.
        """
        mock_get_player.return_value = None
        match = MagicMock(id=None, title="Match 1", played_at="2025-01-01", match_format_id=1)

        participants = [{"name": 999}]

        with self.assertRaises(ValueError):
            match_service.create_match_with_players(match, participants)

    @patch('services.match_service.read_query')
    def test_all_team_matches(self, mock_read_query):
        """
        Test retrieval of all team matches.
        """
        mock_read_query.return_value = [
            (1, 'Match 1', '2025-01-01', 'Format A', 1, 'Team A'),
            (1, 'Match 1', '2025-01-01', 'Format A', 2, 'Team B'),
            (2, 'Match 2', '2025-02-01', 'Format B', 3, 'Team C'),
        ]

        result = list(match_service.all_team_matches())

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].match_id, 1)
        self.assertIn('Team A', list(result[0].team_name))
        self.assertIn('Team B', list(result[0].team_name))

    def test_sort_matches_by_title(self):
        """
        Test sorting of matches by their title.
        """
        matches = [
            Match(id=1, title="B Match", played_at="2025-01-01", match_format_id=1),
            Match(id=2, title="A Match", played_at="2025-02-01", match_format_id=2),
        ]

        sorted_matches = match_service.sort(matches, attribute="title")
        self.assertEqual(sorted_matches[0].title, "A Match")
        self.assertEqual(sorted_matches[1].title, "B Match")

    @patch('services.match_service.read_query')
    @patch('services.match_service.create_player_response_object')
    def test_get_with_players(self, mock_create_response, mock_read_query):
        """
        Test retrieval of match details with players.
        """
        mock_read_query.side_effect = [
            [(1, 'Match 1', '2025-01-01', 1)],
            [(1, 'Player 1', 1, 10), (2, 'Player 2', 1, 15)],
        ]
        mock_create_response.return_value = {
            'match_id': 1,
            'title': 'Match 1',
            'played_at': '2025-01-01',
            'format_id': 1,
            'participants': [{'name': 'Player 1'}, {'name': 'Player 2'}]
        }

        result = match_service.get_with_players(1)
        self.assertEqual(result['match_id'], 1)
        self.assertEqual(len(result['participants']), 2)

    @patch('services.match_service.read_query')
    @patch('services.match_service.create_team_response_object')
    def test_get_with_teams(self, mock_create_response, mock_read_query):
        """
        Test retrieval of match details with teams.
        """
        mock_read_query.side_effect = [
            [(1, 'Match 1', '2025-01-01', 1)],
            [(1, 'Team A', 10), (2, 'Team B', 15)],
        ]
        mock_create_response.return_value = {
            'match_id': 1,
            'title': 'Match 1',
            'played_at': '2025-01-01',
            'format_id': 1,
            'participants': [{'name': 'Team A'}, {'name': 'Team B'}]
        }

        result = match_service.get_with_teams(1)
        self.assertEqual(result['match_id'], 1)
        self.assertEqual(len(result['participants']), 2)

    @patch('services.match_service.insert_query')
    @patch('services.match_service.player_service.get_player_by_id')
    def test_create_match_with_players(self, mock_get_player, mock_insert_query):
        """
        Test creation of a match with valid players.
        """
        mock_get_player.return_value = MagicMock(id=1, first_name="Player", second_name="One")
        mock_insert_query.return_value = 1

        match = Match(id=None, title="Match 1", played_at="2025-01-01", match_format_id=1)

        participants = [{"name": 1}]

        match_service.create_match_with_players(match, participants)

        self.assertEqual(match.id, 1)

    @patch('services.match_service.insert_query')
    @patch('services.match_service.team_service.get_team_id')
    def test_create_with_teams(self, mock_get_team_id, mock_insert_query):
        """
        Test creation of a match with valid teams.
        """
        mock_get_team_id.return_value = 1
        mock_insert_query.return_value = 1

        match = Match(id=None, title="Match 1", played_at="2025-01-01", match_format_id=1)
        teams = ["Team A", "Team B"]

        match_service.create_with_teams(match, teams)

        mock_insert_query.assert_called_with(
            'INSERT INTO team_match_detail (team_id, match_id) VALUES (%s,%s)', (1, 1)
        )

    @patch('services.match_service.read_query')
    def test_player_match_exists(self, mock_read_query):
        """
        Test checking if a player match exists.
        """
        mock_read_query.return_value = [(1,)]

        result = match_service.player_match_exists(1, 1)
        self.assertTrue(result)

    @patch('services.match_service.read_query')
    def test_match_exists(self, mock_read_query):
        """
        Test checking if a match exists.
        """
        mock_read_query.return_value = [(1,)]

        result = match_service.match_exists(1)
        self.assertTrue(result)

    @patch('services.match_service.update_query')
    def test_update_player_match_score(self, mock_update_query):
        """
        Test updating player match scores.
        """
        match_update = PlayerMatchDetailUpdate(player_ids=[1, 2], score=[10, 15])

        match_service.update_player_match_score(1, match_update)

        mock_update_query.assert_called_with(
            '''UPDATE player_match_detail
                   SET score = %s 
                   WHERE player_id = %s AND match_id = %s''',
        (15, 2, 1)
        )

    @patch('services.match_service.update_query')
    def test_update_team_match_score(self, mock_update_query):
        """
        Test updating team match scores.
        """
        match_update = TeamMatchDetailUpdate(team_ids=[1, 2], score=[10, 15])

        match_service.update_team_match_score(1, match_update)

        mock_update_query.assert_called_with(
            '''UPDATE team_match_detail
            SET score = %s WHERE team_id = %s and match_id = %s''',
            (15, 2, 1)
        )
