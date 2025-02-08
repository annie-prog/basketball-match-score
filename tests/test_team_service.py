"""
This module contains tests for the functions in the `team_service` module, 
which handles the business logic related to managing teams in the system. 
"""

from unittest import TestCase
from unittest.mock import patch
from services import team_service
from data.models import Team

class TeamServiceShould(TestCase):
    """
    Unit tests for the team_service module.
    """
    @patch("services.team_service.database")
    def test_create_team_returns_correctly(self, mock_database):
        """
        Test if create_team correctly inserts a team and returns the created team with ID.
        """
        mock_database.read_query.return_value = []
        mock_database.insert_query.return_value = 1

        team = Team(name="Golden State Warriors")
        result = team_service.create_team(team)
        expected = Team(id=1, name="Golden State Warriors")

        self.assertEqual(result, expected)

    @patch("services.team_service.database")
    def test_create_team_returns_none_when_team_exists(self, mock_database):
        """
        Test if create_team returns None when the team already exists in the database.
        """
        mock_database.read_query.return_value = [(1, "Golden State Warriors")]

        team = Team(name="Golden State Warriors")
        result = team_service.create_team(team)

        self.assertIsNone(result)

    @patch("services.team_service.database")
    def test_all_teams_returns_correctly(self, mock_database):
        """
        Test if all_teams correctly returns all teams from the database.
        """
        mock_database.read_query.return_value = [
            (1, "Golden State Warriors"),
            (2, "Los Angeles Lakers")
        ]

        result = team_service.all_teams()
        expected = [
            Team(id=1, name="Golden State Warriors"),
            Team(id=2, name="Los Angeles Lakers")
        ]

        self.assertEqual(list(result), expected)

    @patch("services.team_service.database")
    def test_all_teams_returns_empty_list_when_no_teams(self, mock_database):
        """
        Test if all_teams returns an empty list when no teams are found in the database.
        """
        mock_database.read_query.return_value = []

        result = team_service.all_teams()
        expected = []

        self.assertEqual(list(result), expected)

    @patch("services.team_service.database")
    def test_get_team_by_id_returns_correctly(self, mock_database):
        """
        Test if get_team_by_id correctly returns a team based on the provided ID.
        """
        mock_database.read_query.return_value = [(1, "Golden State Warriors")]

        result = team_service.get_team_by_id(1)
        expected = [Team(id=1, name="Golden State Warriors")]

        self.assertEqual(result, expected)

    @patch("services.team_service.database")
    def test_get_team_by_id_returns_none_when_no_team_found(self, mock_database):
        """
        Test if get_team_by_id returns None when no team is found for the given ID.
        """
        mock_database.read_query.return_value = []

        result = team_service.get_team_by_id(99)
        expected = None

        self.assertEqual(result, expected)

    @patch("services.team_service.database")
    def test_get_team_names_returns_correctly(self, mock_database):
        """
        Test if get_team_names correctly returns a list of team names.
        """
        mock_database.read_query.return_value = [
            ("Golden State Warriors",),
            ("Los Angeles Lakers",)
        ]

        result = team_service.get_team_names()
        expected = ["Golden State Warriors", "Los Angeles Lakers"]

        self.assertEqual(result, expected)

    @patch("services.team_service.database")
    def test_get_team_id_returns_correctly(self, mock_database):
        """
        Test if get_team_id correctly returns the team ID for a given team name.
        """
        mock_database.read_query.return_value = [(1,)]

        result = team_service.get_team_id("Golden State Warriors")
        expected = 1

        self.assertEqual(result, expected)

    @patch("services.team_service.database")
    def test_delete_team_returns_correctly(self, mock_database):
        """
        Test if delete_team correctly calls the delete query and returns None.
        """
        mock_database.update_query.return_value = None

        result = team_service.delete_team(1)

        mock_database.update_query.assert_called_with("DELETE from team where id = %s", (1,))
        self.assertIsNone(result)
