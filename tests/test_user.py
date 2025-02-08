"""
Unit tests for the user-related functionality, including validation,
registration, login, user retrieval, and logout in the application.
"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
from flask import Flask
from routers.user import (
    _is_valid_password, register, all_users,
    logout, user_blueprint
)

class UserBlueprintTests(TestCase):
    """
    Tests for the user blueprint, ensuring routes and functions related to user
    operations (such as registration, login, and logout) behave as expected.
    """
    def setUp(self):
        """Sets up the test environment before each test."""
        self.app = Flask(__name__, template_folder="templates")
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app.register_blueprint(user_blueprint)

    def test_is_valid_password_valid(self):
        """Test that a valid password is accepted."""
        valid_password = "Strong@123"
        self.assertTrue(_is_valid_password(valid_password))

    def test_is_valid_password_invalid(self):
        """Test that invalid passwords are rejected."""
        invalid_passwords = [
            "short", "nouppercase123@", "NOLOWERCASE123@", "NoSpecial123", "NoNumber@"
        ]
        for password in invalid_passwords:
            with self.subTest(password=password):
                self.assertFalse(_is_valid_password(password))

    @patch("services.user_service.create_user")
    @patch("data.models.LogInfo.is_valid_email", return_value=True)
    def test_register_valid_user(self, _, mock_create_user):
        """Test that a valid user can register successfully."""
        mock_create_user.return_value = MagicMock()
        with self.app.test_request_context(
            "/user/register", method="POST", data={
                "email": "test@example.com", "password": "Valid@123",
                "role": "user", "name": "User1"
            }
        ):
            response = register()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/user/login", response.location)

    @patch("routers.user.url_for", return_value="/user/dashboard_user")
    @patch("routers.user.render_template")
    @patch("services.user_service.find_user")
    @patch("services.user_service.create_token", return_value="fake_token")
    def test_login_valid_user(self, _, mock_find_user, mock_render, __):
        """Test that a user can log in successfully."""
        mock_find_user.return_value = MagicMock(role="user")
        mock_render.return_value = "Mocked Login Page"

        with self.app.test_client() as client:
            response = client.post(
                "/user/login",
                data={"email": "test@example.com", "password": "Valid@123"},
                follow_redirects=False,
            )
            self.assertEqual(response.status_code, 200)

    @patch("services.user_service.all_users", return_value=[
        MagicMock(id=1, email="user1@example.com", role="user"),
        MagicMock(id=2, email="admin@example.com", role="admin")
    ])
    def test_all_users(self, _):
        """Test retrieving all users."""
        with self.app.test_request_context("/user/all", method="GET"):
            response = all_users()
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertEqual(len(json_data["users"]), 2)

    def test_logout(self):
        """
        Test logging out a user.
        """
        with self.app.test_request_context("/user/logout", method="GET"):
            response = logout()
            self.assertEqual(response.status_code, 302)
            self.assertIn("/user/login", response.location)
