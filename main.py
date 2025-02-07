"""
This is the main application file for the Flask web application.
It sets up the routes and registers the blueprints for different modules such 
as players, teams, and tournaments.
"""

from flask import Flask, render_template
from routers.player import player_blueprint
from routers.team import team_blueprint
from routers.user import user_blueprint
from routers.requests_router import requests_blueprint
from routers.match import match_blueprint
from routers.match_format import match_format_blueprint
from routers.tournaments import tournaments_blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/home')
def home():
    """
    The home route that renders the homepage template.
    """
    return render_template('home.html')

app.register_blueprint(player_blueprint)
app.register_blueprint(team_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(requests_blueprint)
app.register_blueprint(match_blueprint)
app.register_blueprint(match_format_blueprint)
app.register_blueprint(tournaments_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
