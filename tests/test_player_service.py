"""
This module contains tests for the functions in the `player_service` module,
which is responsible for managing player-related operations.
"""

from unittest import TestCase
from unittest.mock import patch
from services import player_service
from data.models import Player

class PlayerServiceShould(TestCase):
    """
    This class contains test cases for various functions such as creating a 
    player, retrieving player data, and handling players in a tournament.
    """
    @patch("services.player_service.database.read_query")
    def test_country_id_returns_correctly(self, mock_read_query):
        """
        Test if country_id correctly returns the country ID for a given country name.
        """
        mock_read_query.return_value = [(1,)]

        result = player_service.country_id("USA")
        expected = 1

        self.assertEqual(result, expected)

    @patch("services.player_service.team_service.get_team_id")
    @patch("services.player_service.database.insert_query")
    @patch("services.player_service.country_names")
    @patch("services.player_service.country_id")
    @patch("services.player_service.team_service.get_team_names")
    def test_create_player_creates_player_correctly(
        self, mock_get_team_names, mock_country_id, mock_country_names,
        mock_insert_query, mock_get_team_id
        ):
        """
        Test if create_player correctly creates a player and returns the player 
        with the expected attributes.
        """
        mock_country_names.return_value = ["USA", "Canada"]
        mock_get_team_names.return_value = ["Lakers", "Warriors"]
        mock_get_team_id.return_value = 1
        mock_country_id.return_value = 1
        mock_insert_query.return_value = 1

        player = Player(first_name="Kobe", second_name="Bryant", country="USA", team="Lakers")
        result = player_service.create_player(player)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.first_name, "Kobe")
        self.assertEqual(result.second_name, "Bryant")
        self.assertEqual(result.country, "USA")
        self.assertEqual(result.team, "Lakers")

    @patch("services.player_service.team_service.get_team_id")
    @patch("services.player_service.database.insert_query")
    @patch("services.player_service.country_names")
    @patch("services.player_service.team_service.get_team_names")
    def test_create_player_invalid_team(self, mock_get_team_names, mock_country_names, _, __):
        """
        Test if create_player returns None when an invalid team is provided.
        """
        mock_country_names.return_value = ["USA", "Canada"]
        mock_get_team_names.return_value = ["Lakers"]

        player = Player(first_name="Kobe", second_name="Bryant", country="USA", team="Bulls")
        result = player_service.create_player(player)

        self.assertIsNone(result)

    @patch("services.player_service.database.read_query")
    def test_get_player_by_id_returns_correctly(self, mock_read_query):
        """
        Test if get_player_by_id correctly retrieves the player based on ID.
        """
        mock_read_query.return_value = [(23, 'Michael', 'Jordan', 'USA', 'Chicago Bulls')]

        result = player_service.get_player_by_id(23)
        expected = Player(
            id=23, first_name="Michael", second_name="Jordan", country="USA",
            team="Chicago Bulls"
        )

        self.assertEqual(result, expected)

    @patch("services.player_service.database")
    def test_get_tournament_players_returns_correctly(self, mock_base):
        """
        Test if get_tournament_players correctly retrieves players for a given tournament.
        """
        mock_base.read_query.return_value = [
            (23, 'Michael', 'Jordan', 'USA', 'Chicago Bulls', 33, 'Scottie',
             'Pippen', 'USA', 'Chicago Bulls'
            ),
            (30, 'Stephen', 'Curry', 'USA', 'Golden State Warriors', 34, 'Shaquille',
             'O\'Neal', 'USA', None
            ),
            (23, 'Michael', 'Jordan', 'USA', 'Chicago Bulls', 34, 'Shaquille',
             'O\'Neal', 'USA', None
            ),
            (33, 'Scottie', 'Pippen', 'USA', 'Chicago Bulls', 30, 'Stephen',
             'Curry', 'USA', 'Golden State Warriors'
            )
        ]

        result = player_service.get_tournament_players(1)
        expected = [
            Player(
                id=23, first_name="Michael", second_name="Jordan", country="USA",
                team="Chicago Bulls"
            ),
            Player(
                id=33, first_name="Scottie", second_name="Pippen", country="USA",
                team="Chicago Bulls"
            ),
            Player(
                id=30, first_name="Stephen", second_name="Curry", country="USA",
                team="Golden State Warriors"
            ),
            Player(
                id=34, first_name="Shaquille", second_name="O'Neal", country="USA",
                team=None
            )
        ]

        self.assertEqual(result, expected)

    @patch("services.player_service.database")
    def test_get_tournament_players_returns_correctly_when_no_players(self, mock_base):
        """
        Test if get_tournament_players returns an empty list when no players are found.
        """
        mock_base.read_query.return_value = []

        result = player_service.get_tournament_players(1)
        expected = []
        self.assertEqual(result, expected)

    @patch("services.player_service.database.update_query")
    def test_delete_player(self, mock_update_query):
        """
        Test if delete_player correctly deletes a player by ID.
        """
        mock_update_query.return_value = None

        player_service.delete_player(1)

        mock_update_query.assert_called_once_with("DELETE from player where id = %s", (1,))

    @patch("services.player_service.database")
    def test_get_player_by_name_returns_correctly(self, mock_base):
        """
        Test if get_player_by_name correctly retrieves a player based on full name.
        """
        mock_base.read_query.return_value = [(23, 'Michael', 'Jordan', 'USA', 'Chicago Bulls')]

        result = player_service.get_player_by_name("Michael Jordan")
        expected = Player(
            id=23, first_name="Michael", second_name="Jordan", country="USA",
            team="Chicago Bulls"
        )

        self.assertEqual(result, expected)

    @patch("services.player_service.database")
    def test_get_player_by_name_returns_correctly_when_no_player(self, mock_base):
        """
        Test if get_player_by_name returns None when no player is found by the name.
        """
        mock_base.read_query.return_value = []

        result = player_service.get_player_by_name("Michael Jordan")
        expected = None

        self.assertEqual(result, expected)

    @patch("services.player_service.database")
    def test_all_players_returns_correctly(self, mock_base):
        """
        Test if all_players correctly returns a list of all players.
        """
        mock_base.read_query.return_value = [
            (23, 'Michael', 'Jordan', 'USA', 'Chicago Bulls'),
            (30, 'Stephen', 'Curry', 'USA', 'Golden State Warriors'),
            (34, 'Shaquille', 'O\'Neal', 'USA', None),
            (33, 'Scottie', 'Pippen', 'USA', 'Chicago Bulls')
        ]

        result = player_service.all_players()
        expected = [
            Player(
                id=23, first_name="Michael", second_name="Jordan", country="USA",
                team="Chicago Bulls"
            ),
            Player(
                id=30, first_name="Stephen", second_name="Curry", country="USA",
                team="Golden State Warriors"
            ),
            Player(
                id=34, first_name="Shaquille", second_name="O'Neal", country="USA",
                team=None
            ),
            Player(
                id=33, first_name="Scottie", second_name="Pippen", country="USA",
                team="Chicago Bulls"
            )
        ]
        self.assertEqual(result, expected)

    @patch("services.player_service.database")
    def test_all_players_returns_correctly_when_no_players(self, mock_base):
        """
        Test if all_players returns an empty list when no players are found.
        """
        mock_base.read_query.return_value = []

        result = player_service.all_players()
        expected = []

        self.assertEqual(result, expected)

    @patch("services.player_service.all_players")
    @patch("services.player_service.create_player_by_name")
    def test_create_unknown_participants_profile_returns_correctly_when_no_players(
        self, mock_create, mock_all
    ):
        """
        Test if create_unknown_participants_profile correctly handles the case 
        when no players are found and returns the correct player names.
        """
        mock_create.return_value = None
        mock_all.return_value = []

        result = player_service.create_unknown_participants_profile(
            ["Michael Jordan", "Kobe Bryant", "LeBron James", "Stephen Curry"]
        )
        expected = [
            ["Michael", "Jordan"], ["Kobe", "Bryant"], ["LeBron", "James"], ["Stephen", "Curry"]
        ]

        self.assertEqual(result, expected)

    @patch("services.player_service.database")
    def test_country_names_returns_correctly(self, mock_database):
        """
        Test if country_names correctly returns a list of country names when queried.
        """
        mock_database.read_query.return_value = [("USA",), ("Canada",)]

        result = player_service.country_names()
        expected = ["USA", "Canada"]

        self.assertEqual(result, expected)

    @patch("services.player_service.country_names")
    @patch("services.player_service.team_service")
    def test_create_player_returns_correctly_when_no_such_team(self, mock_team, mock_country):
        """
        Test if create_player returns None when no such team exists in the database.
        """
        mock_team.team_names.return_value = ["Lakers", "Warriors"]
        mock_country.return_value = ["USA", "Canada"]

        result = player_service.create_player(
            Player(first_name="Kobe", second_name="Bryant", country="USA", team="Bulls")
        )
        expected = None

        self.assertEqual(result, expected)

    @patch("services.player_service.country_names")
    def test_create_player_returns_correctly_when_no_such_country(self, mock_country):
        """
        Test if create_player returns None when no such country exists in the database.
        """
        mock_country.return_value = ["Canada", "Spain"]

        result = player_service.create_player(
            Player(first_name="Kobe", second_name="Bryant", country="USA", team="Lakers")
        )
        expected = None

        self.assertEqual(result, expected)

    @patch("services.player_service.database.update_query")
    def test_null_team_sets_team_id_to_null(self, mock_update_query):
        """
        Test if null_team correctly sets the team_id to None for a player.
        """
        mock_update_query.return_value = None

        result = player_service.null_team(1)
        mock_update_query.assert_called_with(
            "UPDATE player set team_id = %s where team_id = %s", (None, 1)
        )
        self.assertIsNone(result)
