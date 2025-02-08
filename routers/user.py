"""
Module for user-related operations, including registration, login, and dashboard management.
"""

from flask import request, Blueprint, render_template, redirect, url_for, make_response, jsonify, Response
from services import user_service
from services.user_service import create_token, find_user
from data.models import LogInfo

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

def _is_valid_password(password: str) -> bool:
    """
    Validate password strength.
    """
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_+=<>?/|{}[]~`" for char in password):
        return False
    return True

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register() -> str:
    """
    Handle user registration.
    Renders the registration form and processes user registration on POST.
    """
    errors = []
    roles = ["user", "admin", "director"]
    if request.method == 'POST':
        try:
            loginfo = LogInfo(
                email=request.form['email'],
                password=request.form['password']
            )
            selected_role = request.form.get('role', 'user')

            username = request.form['name']

            if selected_role not in roles:
                errors.append(f"Invalid role selected: {selected_role}")
            if not LogInfo.is_valid_email(loginfo.email):
                errors.append("Invalid email format")
            if not _is_valid_password(loginfo.password):
                errors.append(
                    "Password must be at least 8 characters long and include a number, "
                    "an uppercase letter, a lowercase letter, and a special character"
                )

            user = user_service.create_user(loginfo, role=selected_role, name=username)
            if not user:
                errors.append("Email already registered")
                return render_template('register.html', errors=errors, roles=roles)

            return redirect(url_for('user.login'))
        except ValueError as e:
            errors.append(str(e))
    return render_template('register.html', errors=errors, roles=roles)

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    """
    Handle user login.
    Renders the login form and authenticates user credentials on POST.
    """
    errors = []
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        loginfo = LogInfo(email=email, password=password)

        user = find_user(loginfo)
        if user:
            token = create_token(user)
            role_route = f'user.dashboard_{user.role.lower()}'
            response = make_response(redirect(url_for(role_route)))
            response.set_cookie('access_token', token)
            return response
        errors.append("Invalid email or password")

    return render_template('login.html', errors=errors)

def get_logged_in_user():
    """
    Retrieve the currently logged-in user from the access token.
    Returns:
        User object or None if the token is invalid or missing.
    """
    token = request.cookies.get('access_token')

    if token:
        loginfo = user_service.from_token(token)

        if loginfo:
            return user_service.find_user(loginfo)
    return None

@user_blueprint.route('/all', methods=['GET'])
def all_users() -> Response:
    """
    Retrieve all registered users as JSON.
    Returns:
        JSON object containing a list of users.
    """
    users = user_service.all_users()
    users_data = [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]
    return jsonify({"users": users_data})

@user_blueprint.route('/dashboard_user')
def dashboard_user() -> Response:
    """
    Render the user dashboard if logged in, otherwise redirect to login.
    """
    user = get_logged_in_user()
    if user:
        return render_template('dashboard_user.html', name=user.name, role="User")
    return redirect(url_for('user.login'))

@user_blueprint.route('/dashboard_admin')
def dashboard_admin() -> Response:
    """
    Render the admin dashboard if logged in as admin, otherwise redirect to login.
    """
    user = get_logged_in_user()
    if user and user.role == 'admin':
        return render_template('dashboard_admin.html', name=user.name, role="Admin")
    return redirect(url_for('user.login'))

@user_blueprint.route('/dashboard_director')
def dashboard_director() -> Response:
    """
    Render the director dashboard if logged in as director, otherwise redirect to login.
    """
    user = get_logged_in_user()
    if user and user.role == 'director':
        return render_template('dashboard_director.html', name=user.name, role="Director")
    return redirect(url_for('user.login'))

@user_blueprint.route('/logout')
def logout() -> Response:
    """
    Log out the user by clearing the access token cookie.
    """
    response = make_response(redirect(url_for('user.login')))
    response.delete_cookie('access_token')
    return response

@user_blueprint.route('/delete_user', methods=['POST'])
def delete_user_route() -> Response:
    """
    Handle the deletion of a user based on their ID.
    """
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id:
        user_service.delete_user(user_id)
        return jsonify({"message": "User deleted successfully."}), 200
    return jsonify({"error": "No user ID provided"}), 400
