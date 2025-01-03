from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import Games, Teams
from app.utils import login_required
from sqlalchemy import func
from app.forms.team_forms import FilterTeamForm
from app.queries.team_queries import get_distinct_pokemon_names

bp = Blueprint('games', __name__)


@bp.route("/games", methods=["POST", "GET"])
@login_required
def games():
    games_list = Games.query.order_by(Games.id).all()

    return render_template("games.html", games_list=games_list)


@bp.route("/filter/<game_name>", methods=["GET"])
@login_required
def filter_page(game_name):
    game = Games.query.filter(func.lower(Games.name)
                              == func.lower(game_name)).first()
    
    if not game:
        flash(f"Game '{game_name}' not found.", "danger")
        return redirect(url_for('general.index'))

    all_teams = Teams.query.filter(Teams.patreon_post == False, Teams.game_id == game.id).order_by(Teams.created_at.desc()).all()

    if session.get("is_patreon", False):
        all_teams = Teams.query.filter_by(
        game_id=game.id).order_by(Teams.created_at.desc()).all()


    pokemon_names = [p[0] for p in get_distinct_pokemon_names(game.id)]

    form = FilterTeamForm(game.id)

    return render_template("filter.html", game_name=game_name, teams=all_teams, form=form, pokemon_names=pokemon_names, patreon_only=False)
