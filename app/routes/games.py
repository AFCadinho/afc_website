from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Games, Teams
from app.utils import validate_csrf_token

bp = Blueprint('games', __name__)

@bp.route("/games", methods=["POST", "GET"])
def games():
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("games.games"))

    games_list = Games.query.order_by(Games.id).all()
    return render_template("games.html", games_list=games_list)


@bp.route("/release_year/<game_name>", methods=["GET", "POST"])
def release_year(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))
    game = Games.query.filter_by(name=game_name).first()
    game_id = game.id
    print(f"Game ID: {game_id}")
    all_teams = Teams.query.filter_by(game_id=game_id).all()

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("games.release_year", game_name=game_name, teams=all_teams))

        release_year = request.form["release_year"]
        return redirect(url_for("teams.teams", name=game_name, release_year=release_year))

    return render_template("release_year.html", game_name=game_name, teams=all_teams)


@bp.route("/goodbye")
def goodbye():
    return "Goodbye"
