from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Games, Teams
from app.utils import validate_csrf_token
from sqlalchemy import func
from app.forms.team_forms import FilterTeamForm
from app.queries.team_queries import get_distinct_pokemon_names

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


@bp.route("/filter/<game_name>", methods=["GET"])
def filter_page(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    game = Games.query.filter(func.lower(Games.name)
                              == func.lower(game_name)).first()
    
    if not game:
        flash(f"Game '{game_name}' not found.", "danger")
        return redirect(url_for('general.index'))

    game_id = game.id

    all_teams = Teams.query.filter(Teams.patreon_post == False,).order_by(Teams.created_at.desc()).all()

    if session["is_patreon"]:
        all_teams = Teams.query.filter_by(
            game_id=game_id).order_by(Teams.created_at.desc()).all()

    pokemon_names = [p[0] for p in get_distinct_pokemon_names(game.id)]

    form = FilterTeamForm(game.id)

    return render_template("filter.html", game_name=game_name, teams=all_teams, form=form, pokemon_names=pokemon_names, patreon_only=False)
