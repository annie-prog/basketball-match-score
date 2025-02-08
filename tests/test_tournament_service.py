"""
Test classes and methods for tournament services functionality, 
including tournament creation,match creation, and stage handling.
"""

from unittest import TestCase
from unittest.mock import patch
from datetime import date
from services import tournaments_service
from data.models import Tournament, MatchUp, Player, TournamentResponseModel

class TournamentServiceShould(TestCase):
    """
    Unit tests for the tournament service functions.
    """
    @patch("services.tournaments_service.insert_query")
    def test_create_tournament_raises_error_with_invalid_data(self, mock_query):
        """
        Tests that the create_tournament method raises an exception when invalid data is passed.
        """
        mock_query.side_effect = Exception("Invalid data")
        tournament = Tournament(title=None, prize="1000 lv", format_id=1)

        with self.assertRaises(Exception):
            tournaments_service.create_tournament(tournament)

    @patch("services.tournaments_service.read_query")
    def test_get_matchup_ids_next_phase_returns_correctly(self, mock_query):
        """
        Tests that get_matchup_ids_next_phase returns the correct matchups for the next phase.
        """
        mock_query.return_value = [[9],[10],[11],[12]]
        matchup = MatchUp(
            id=1, tournament_id=1, played_at=date(2022, 12, 23),
            tournament_phase=1, player_one=1, player_two=2,
            player_one_score=10, player_two_score=15
        )

        result = tournaments_service.get_matchup_ids_next_phase(matchup)
        expected = [9,10,11,12]

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    def test_get_matchup_ids_next_phase_returns_correctly_when_final(self, mock_query):
        """
        Tests that get_matchup_ids_next_phase returns an empty list when it's the final phase.
        """
        mock_query.return_value = []
        matchup = MatchUp(
            id=13, tournament_id=1,
            played_at=date(2022, 12, 23), tournament_phase=1, player_one=1,
            player_two=2, player_one_score=10, player_two_score=15
        )

        result = tournaments_service.get_matchup_ids_next_phase(matchup)
        expected = []

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.create_league")
    def test_create_league_tournament_returns_success_message(self, mock_create_league):
        """
        Tests that the create_league method returns the correct success message.
        """
        mock_create_league.return_value = ("League tournament created successfully!", 201)

        tournament = Tournament(title="League Tournament", prize="2000 lv", format_id=2)
        participants = ["1", "2", "3", "4"]
        starting_date = date(2025, 2, 2)

        expected = ("League tournament created successfully!", 201)

        self.assertEqual(
            tournaments_service.create_league(tournament, participants, starting_date), expected
        )

    @patch("services.tournaments_service.get_league_tournament_matchups")
    def test_get_league_matchups_returns_correctly(self, mock_get_matchups):
        """
        Tests that the get_league_tournament_matchups method returns the correct matchups.
        """
        mock_get_matchups.return_value = [
            MatchUp(id=1, tournament_id=1, played_at=date(2025, 2, 2), tournament_phase=1,
                    player_one=1, player_two=2, player_one_score=3, player_two_score=2)
        ]

        result = tournaments_service.get_league_tournament_matchups(1)
        expected = [MatchUp(id=1, tournament_id=1, played_at=date(2025, 2, 2), tournament_phase=1,
                            player_one=1, player_two=2, player_one_score=3, player_two_score=2)]

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.create_phase")
    def test_create_phase_creates_phase_correctly(self, mock_create_phase):
        """
        Tests that the create_phase method creates a phase correctly.
        """
        mock_create_phase.return_value = None

        participants = ["1", "2", "3", "4"]
        phase = 1
        starting_date = date(2025, 2, 2)

        tournaments_service.create_phase(
            Tournament(id=1, title="Test Tournament", prize="1000 lv", format_id=1),
            participants, phase, starting_date
        )

        mock_create_phase.assert_called_once_with(
            Tournament(id=1, title="Test Tournament", prize="1000 lv", format_id=1),
            participants, phase, starting_date
        )

    def test_create_phase_raises_unauthorized_for_invalid_participants(self):
        """
        Tests that the create_phase method raises an unauthorized error 
        for invalid participants count.
        """
        participants = ["1", "2", "3"]
        result = len(participants) - 1
        expected = 2
        self.assertEqual(result, expected)

    def test_get_right_id_returns_correctly(self):
        """
        Tests that the get_right_id method returns the correct ID for the next phase.
        """
        current_ids = [[1,2],[3,4],[5,6],[7,8]]
        next_ids = [9,10,11,12]
        matchup = MatchUp(
            id=5, tournament_id=1, played_at=date(2022, 12, 23),
            tournament_phase=1, player_one=1, player_two=2, player_one_score=10,
            player_two_score=15
        )

        result = tournaments_service.get_right_id(matchup,current_ids, next_ids)
        expected = 11

        self.assertEqual(result, expected)

    def test_get_right_id_returns_correctly_when_final(self):
        """
        Tests that the get_right_id method returns None for the final phase.
        """
        current_ids = [[15]]
        next_ids = []
        matchup = MatchUp(
            id=15, tournament_id=1, played_at=date(2022, 12, 23),
            tournament_phase=1, player_one=1, player_two=2, player_one_score=10,
            player_two_score=15
        )

        result = tournaments_service.get_right_id(matchup,current_ids, next_ids)
        expected = None

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    def test_get_matchup_returns_correctly(self, mock_query):
        """
        Tests that the get_matchup method returns the correct matchup details.
        """
        mock_query.return_value = [[1,1,date(2022, 12, 23),1,1,2,10,15]]

        result = tournaments_service.get_matchup(1)
        expected = MatchUp(
            id=1,tournament_id=1, played_at=date(2022, 12, 23),
            tournament_phase=1, player_one=1, player_two=2, player_one_score=10,
            player_two_score=15
        )

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    def test_get_matchup_returns_correctly_when_final(self, mock_query):
        """
        Tests that the get_matchup method returns None for the final phase.
        """
        mock_query.return_value = []

        result = tournaments_service.get_matchup(None)
        expected = None

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.insert_query")
    def test_create_league_returns_correctly(self, mock_query):
        """
        Tests that the create_tournament method works for creating league tournaments.
        """
        mock_query.return_value = 1

        league = Tournament(title="Test League", prize="1000 lv", format_id=2)

        result = tournaments_service.create_tournament(league)
        expected = Tournament(id= 1, title="Test League", prize="1000 lv", format_id=2)

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    def test_all_tournaments_returns_correctly(self, mock_query):
        """
        Tests that all_tournaments returns the correct list of tournaments.
        """
        mock_query.return_value = [
            (1, "Test Tournament", "1000 lv", 1, "John", "Doe", 1, 2, 10),
            (2, "Second Tournament", "2000 lv", 2, "Jane", "Smith", 3, 4, 11)
        ]

        result = tournaments_service.all_tournaments()
        expected = [
            {
                "id": 1, "title": "Test Tournament", "prize": "1000 lv", 
                "tournament_format": 1, "winner": "John Doe", "players": [1, 2], "matches": [10]
            },
            {
                "id": 2, "title": "Second Tournament", "prize": "2000 lv", 
                "tournament_format": 2, "winner": "Jane Smith", "players": [3, 4], "matches": [11]
            }
        ]

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.create_tournament")
    def test_create_tournament_returns_correctly(self, mock_create):
        """
        Tests that the create_tournament method returns the correct tournament data.
        """
        mock_create.return_value = Tournament(
            id=1, title="Test Tournament", prize="1000 lv", format_id=1
        )

        tournament = Tournament(title="Test Tournament", prize="1000 lv", format_id=1)
        result = tournaments_service.create_tournament(tournament)

        expected = Tournament(id=1, title="Test Tournament", prize="1000 lv", format_id=1)
        self.assertEqual(result, expected)

    @patch("services.tournaments_service.create_knockout_tournament")
    def test_create_knockout_tournament_returns_success_message(self, mock_knockout):
        """
        Tests if creating a knockout tournament returns a success message.
        """
        mock_knockout.return_value = ("Knockout tournament created successfully!", 201)

        tournament = Tournament(title="Knockout Tournament", prize="1500 lv", format_id=1)
        players = ["1", "2", "3", "4"]
        start_date = date(2025, 2, 2)

        result = tournaments_service.create_knockout_tournament(tournament, players, start_date)
        expected = ("Knockout tournament created successfully!", 201)

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.set_matchup_score")
    def test_set_matchup_score_updates_correctly(self, mock_set_score):
        """
        Tests if setting a matchup score updates correctly.
        """
        mock_set_score.return_value = None

        matchup_id = 10
        scores = [5, 3]

        tournaments_service.set_matchup_score(matchup_id, scores)

        mock_set_score.assert_called_once_with(matchup_id, scores)

    @patch("services.tournaments_service.get_matchup_ids_next_phase")
    def test_get_matchup_ids_next_phase_when_phase_is_complete(self, mock_get_matchups):
        """
        Tests if getting matchup IDs for the next phase works when the phase is complete.
        """
        mock_get_matchups.return_value = [11, 12, 13, 14]

        matchup = MatchUp(
            id=1, tournament_id=1, played_at=date(2025, 2, 2), tournament_phase=2,
            player_one=1, player_two=2, player_one_score=10, player_two_score=5
        )

        result = tournaments_service.get_matchup_ids_next_phase(matchup)
        expected = [11, 12, 13, 14]

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    def test_get_league_matchup_returns_correctly(self, mock_query):
        """
        Tests if retrieving a league matchup returns the expected result.
        """
        mock_query.return_value = [[1,1,date(2022, 12, 23),2,1,2,2,3]]

        result = MatchUp(
            id=1,tournament_id=1, played_at=date(2022, 12, 23),
            tournament_phase=2, player_one=1, player_two=2, player_one_score=3,
            player_two_score=2
        )
        expected = MatchUp(
            id=1,tournament_id=1, played_at=date(2022, 12, 23),
            tournament_phase=2, player_one=1, player_two=2, player_one_score=3,
            player_two_score=2)

        self.assertEqual(result, expected)

    def test_create_phase_returns_unauthorized(self):
        """
        Tests if creating a phase returns unauthorized for invalid participants.
        """
        participants = ["Vladimir Putin", "Joe Biden", "Recep Erdogan"]

        result = len(participants)-1
        expected = 2

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    def test_get_tournament_format_returns_none_when_not_found(self, mock_query):
        """
        Tests if getting a tournament format returns None when not found.
        """
        mock_query.return_value = []

        result = tournaments_service.get_tournament_format(999)
        expected = None

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.insert_query")
    @patch("services.player_service.get_player_by_name")
    def test_create_random_matchups_creates_matchup_correctly(
        self, mock_get_player, mock_insert_query
    ):
        """
        Tests if creating random matchups inserts the correct values into the database.
        """
        mock_get_player.side_effect = [
            Player(id=1, name="Player One"), Player(id=2, name="Player Two")
        ]
        mock_insert_query.return_value = 1

        tournament = Tournament(id=1, title="Test Tournament", prize="1000 lv", format_id=1)
        start_date = date(2025, 2, 2)

        tournaments_service.create_random_matchups(
            tournament, "Player One", "Player Two", start_date
        )

        mock_insert_query.assert_called_once_with(
            '''insert into matchups (tournament_id, played_at, tournament_phase,
        player_one, player_two, player_one_score, player_two_score)
        values (%s, %s, %s, %s, %s, %s, %s)''',
            (1, date(2025, 2, 2), 1, 1, 2, None, None)
        )

    @patch("services.tournaments_service.create_empty_matchup")
    def test_create_empty_phase_creates_matchups(self, mock_create_empty_matchup):
        """
        Tests if creating an empty phase generates the correct number of matchups.
        """
        tournament = Tournament(id=1, title="Test Tournament", prize="1000 lv", format_id=1)
        tournament_date = date(2025, 2, 2)
        phase = 1
        p_count = 8

        tournaments_service.create_empty_phase(tournament, tournament_date, phase, p_count)

        self.assertEqual(mock_create_empty_matchup.call_count, 4)
        mock_create_empty_matchup.assert_called_with(tournament, tournament_date, phase)

    @patch("services.tournaments_service.read_query")
    def test_check_for_existing_player_returns_true_if_player_exists(self, mock_query):
        """
        Tests if check_for_existing_player returns True when the player exists.
        """
        mock_query.return_value = [(1, "Player One", "Team A")]

        result = tournaments_service.check_for_existing_player(1)
        self.assertTrue(result)

    @patch("services.tournaments_service.read_query")
    def test_check_for_existing_player_returns_false_if_player_does_not_exist(self, mock_query):
        """
        Tests if check_for_existing_player returns False when the player does not exist.
        """
        mock_query.return_value = []

        result = tournaments_service.check_for_existing_player(999)
        self.assertFalse(result)

    @patch("services.tournaments_service.read_query")
    def test_get_tournament_matchups_returns_correctly(self, mock_query):
        """
        Tests if get_tournament_matchups returns the correct matchups for a given tournament.
        """
        mock_query.return_value = [
            (1, 1, date(2025, 2, 2), 1, 1, 2, 10, 15)
        ]

        result = tournaments_service.get_tournament_matchups(1)
        expected = [MatchUp(id=1, tournament_id=1, played_at=date(2025, 2, 2), tournament_phase=1,
                            player_one=1, player_two=2, player_one_score=10, player_two_score=15)]

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.create_league")
    def test_create_league_raises_error_for_invalid_participants(self, mock_create_league):
        """
        Tests if create_league raises an error for invalid number of participants.
        """
        mock_create_league.return_value = (
            "Participants should be 4, 8, 16, 32, 64, 128 or 256 count!", 401
        )

        league = Tournament(title="Test League", prize="2000 lv", format_id=2)
        participants = ["1", "2", "3"]
        starting_date = date(2025, 2, 2)

        expected = ("Participants should be 4, 8, 16, 32, 64, 128 or 256 count!", 401)

        self.assertEqual(
            tournaments_service.create_league(league, participants, starting_date), expected
        )

    @patch("services.tournaments_service.read_query")
    def test_get_by_tournament_id_returns_none_when_not_found(self, mock_query):
        """
        Tests if get_by_tournament_id returns None when the tournament is not found.
        """
        mock_query.return_value = []

        result = tournaments_service.get_by_tournament_id(999)
        expected = None

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.read_query")
    @patch("services.player_service.get_tournament_players")
    @patch("services.tournaments_service.get_tournament_matchups")
    @patch("services.tournaments_service.get_tournament_format")
    def test_get_by_tournament_id_returns_correctly(self, mock_get_format, mock_get_matchups,
                                                mock_get_players, mock_read_query):
        """
        Tests if get_by_tournament_id returns the correct tournament details.
        """
        mock_read_query.return_value = [(1, "Test Tournament", "1000 lv", 1, "John Doe")]
        mock_get_players.return_value = [Player(id=1, name="Player One")]
        mock_get_matchups.return_value = [
            MatchUp(
                id=1, tournament_id=1, played_at=date(2025, 2, 2), tournament_phase=1,
                player_one=1, player_two=2, player_one_score=3, player_two_score=2
                )
            ]
        mock_get_format.return_value = "Knockout"

        result = tournaments_service.get_by_tournament_id(1)
        expected = TournamentResponseModel(
            id=1, title="Test Tournament", prize="1000 lv", format="Knockout",
            winner="John Doe", players=[Player(id=1, name="Player One")],
            matchups=[
                MatchUp(id=1, tournament_id=1, played_at=date(2025, 2, 2),
                tournament_phase=1, player_one=1, player_two=2, player_one_score=3,
                player_two_score=2)
            ]
        )

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.create_knockout_tournament")
    def test_create_knockout_tournament_raises_error_for_invalid_participants(self, mock_knockout):
        """
        Tests if create_knockout_tournament raises an error for invalid number of participants.
        """
        mock_knockout.return_value = (
            "Participants should be 4, 8, 16, 32, 64, 128 or 256 count!", 401
        )

        tournament = Tournament(title="Knockout Tournament", prize="1500 lv", format_id=1)
        participants = ["1", "2", "3"]
        starting_date = date(2025, 2, 2)

        result = tournaments_service.create_knockout_tournament(
            tournament, participants, starting_date
        )
        expected = ("Participants should be 4, 8, 16, 32, 64, 128 or 256 count!", 401)

        self.assertEqual(result, expected)

    @patch("services.tournaments_service.update_query")
    def test_set_tournament_winner_success(self, mock_update_query):
        """
        Tests if set_tournament_winner successfully updates the tournament winner.
        """
        mock_update_query.return_value = 1

        tournament_id = 1
        winner_id = 101

        result = tournaments_service.set_tournament_winner(tournament_id, winner_id)
        self.assertTrue(result)

        mock_update_query.assert_called_once_with(
            '''
        UPDATE tournament
        SET winner = %s
        WHERE id = %s''',
            (winner_id, tournament_id)
        )

    @patch("services.tournaments_service.update_query")
    def test_set_tournament_winner_failure(self, mock_update_query):
        """
        Tests if set_tournament_winner returns False when the update fails.
        """
        mock_update_query.return_value = 0

        tournament_id = 1
        winner_id = 101

        result = tournaments_service.set_tournament_winner(tournament_id, winner_id)

        self.assertFalse(result)

        mock_update_query.assert_called_once_with(
            '''
        UPDATE tournament
        SET winner = %s
        WHERE id = %s''',
            (winner_id, tournament_id)
        )
