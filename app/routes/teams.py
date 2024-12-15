from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Teams, Comments, Games, Pokemon
from app import db
from app.utils import validate_csrf_token
from app.pokemon_requests import fetch_pokepaste_names, fetch_pokemon_images
from datetime import datetime
from sqlalchemy import extract
from app.constants import VALID_ARCHETYPES

bp = Blueprint('teams', __name__)


@bp.route("/team/<team_id>")
def view_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    team = Teams.query.filter_by(id=team_id).first()
    comments = Comments.query.filter_by(team_id=team_id).all()

    if not team and not team.pokepaste:
        flash("No Team information available.", category="error")
        return render_template(url_for("index"))

    pokepaste = team.pokepaste
    pokemon_names = fetch_pokepaste_names(pokepaste)
    pokemon_image_dict = fetch_pokemon_images(pokemon_names)

    return render_template("view_team.html", team=team, comments=comments, pokemon_image_dict=pokemon_image_dict)


@bp.route("/post_comment/<int:team_id>", methods=["POST"])
def post_team_comment(team_id):

    if not validate_csrf_token():
        return redirect(url_for("teams.view_team", team_id=team_id))

    user_id = session["user_id"]
    comment_text = request.form["comment"]

    if comment_text:
        comment = Comments(
            team_id=team_id, user_id=user_id, comment=comment_text)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for("teams.view_team", team_id=team_id))


@bp.route("/add_team/<game_name>", methods=["GET", "POST"])
def add_team(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    game = Games.query.filter_by(name=game_name).first()
    game_id = game.id

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("teams.add_team", game_name=game_name))

        team_name = request.form.get("team_name")
        pokepaste = request.form.get("pokepaste")
        created_at = request.form.get("created_at")
        archetype = request.form.get("archetype")

        team = Teams(
            game_id=game_id,
            name=team_name,
            pokepaste=pokepaste,
            created_at=datetime.strptime(
                created_at, "%Y-%m-%d").date() if created_at else None,
            archetype=archetype
        )
        db.session.add(team)
        db.session.commit()
        flash(f"Team {team_name} successfully created!")

        pokepaste_names = fetch_pokepaste_names(team.pokepaste)
        pokemon_names = []
        for name in pokepaste_names:
            pokemon = Pokemon(team_id=team.id, name=name)
            pokemon_names.append(pokemon)

        db.session.add_all(pokemon_names)
        db.session.commit()
        flash(f"""Each Pokemon from team {
              team.name} have been added to the Pokemon Table.""")
        
        return redirect(url_for("games.filter_page", game_name=game_name))
    
    return render_template("add_team.html", game_name=game_name, archetypes=VALID_ARCHETYPES)


@bp.route("/<game_name>/filtered_teams")
def filtered_teams(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    # Fetch filtered teams from session
    team_ids = session.get("filtered_teams")
    if not team_ids:
        flash("No teams found for the applied filters.", "error")
        return redirect(url_for("games.filter_page", game_name=game_name))

    # Re-query to fetch full team objects
    teams = Teams.query.filter(Teams.id.in_(team_ids)).all()

    return render_template("teams.html", teams=teams, game_name=game_name)


@bp.route("/filter_teams/<game_name>", methods=["POST"])
def filter_teams(game_name):
    if not validate_csrf_token():
        return redirect(url_for("general.index"))

    release_year = request.form.get("release_year")
    pokemon_name = request.form.get("pokemon_name")
    pokemon_archetype = request.form.get("archetype")
    print(pokemon_archetype)

    if not release_year:
        flash("Teams not found", "error")
        return redirect(url_for("general.index"))

    game = Games.query.filter_by(name=game_name).first()
    if not game:
        flash("Game not found!", "error")
        return redirect(url_for("general.index"))

    game_id = game.id

    # Start Building the query to fetch teams
    query = Teams.query.filter(
        Teams.game_id == game_id,
        extract("YEAR", Teams.created_at) == int(release_year)
    ).order_by(Teams.created_at.desc())

    # Apply pokemon name filter
    if pokemon_name:
        query = query.filter(Teams.pokemon.any(
            Pokemon.name.ilike(f"%{pokemon_name}%")))
        
    # Apply archetype filter
    if pokemon_archetype:
        query = query.filter(Teams.archetype == pokemon_archetype)

    # Get all teams from the query
    teams = query.all()

    # Save filtered team IDs in session
    team_id_list = []
    for team in teams:
        team_id_list.append(team.id)
    session["filtered_teams"] = team_id_list

    # Redirect to the teams route
    return redirect(url_for("teams.filtered_teams", game_name=game_name))


@bp.route("/delete_team/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    team = Teams.query.filter_by(id=team_id).first()
    if not team:
        flash("No Team to delete", category="error")
        return redirect(url_for("index"))

    game_name = team.games.name
    team_name = team.name
    db.session.delete(team)
    db.session.commit()
    print("deleted game")

    flash(f"Team {team_name} Successfully Deleted!", category="info")
    return redirect(url_for("games.filter_page", game_name=game_name))


@bp.route("/delete_comment/<int:team_id>/<int:comment_id>", methods=["POST"])
def delete_team_comment(team_id, comment_id):
    comment = Comments.query.filter(
        Comments.id == comment_id, Comments.team_id == team_id).first()
    db.session.delete(comment)
    db.session.commit()
    flash("Comment Deleted.", category="info")
    return redirect(url_for("teams.view_team", team_id=team_id))
