from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Teams, Comments, Games
from app import db
from app.utils import validate_csrf_token
from datetime import datetime
from sqlalchemy import extract

bp = Blueprint('teams', __name__)


@bp.route("/team/<team_id>", methods=["GET", "POST"])
def view_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    team = Teams.query.filter_by(id=team_id).first()
    comments = Comments.query.filter_by(team_id=team_id).all()

    if request.method == "POST":
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

    return render_template("view_team.html", team=team, comments=comments)


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

        team = Teams(
            game_id=game_id,
            name=team_name,
            pokepaste=pokepaste,
            created_at=datetime.strptime(
                created_at, "%Y-%m-%d").date() if created_at else None
        )
        db.session.add(team)
        db.session.commit()
        flash(f"Team {team_name} successfully created!")
        return redirect(url_for("games.release_year", game_name=game_name))

    return render_template("add_team.html", game_name=game_name)


@bp.route("/<name>/<release_year>", methods=["GET", "POST"])
def teams(name, release_year):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("teams.teams", name=name, release_year=release_year))

    # Fetch game_id by name
    game = Games.query.filter_by(name=name).first()
    if not game:
        flash("Game not found!", "error")
        return redirect(url_for("games.index"))

    game_id = game.id

    # Get all teams for the game and release year
    teams = Teams.query.filter(extract("YEAR", Teams.created_at) == int(
        release_year), Teams.game_id == game_id).all()

    return render_template("teams.html", teams=teams)


@bp.route("/delete_team/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    team = Teams.query.filter_by(id=team_id).first()
    if not team:
        return "404 Not Found", 404

    game_name = team.games.name
    team_name = team.name
    db.session.delete(team)
    db.session.commit()
    print("deleted game")

    flash(f"Team {team_name} Successfully Deleted!", category="info")
    return redirect(url_for("games.release_year", game_name=game_name))


@bp.route("/delete_comment/<int:team_id>/<int:comment_id>", methods=["POST"])
def delete_team_comment(team_id, comment_id):
    comment = Comments.query.filter(Comments.id == comment_id, Comments.team_id == team_id).first()
    db.session.delete(comment)
    db.session.commit()
    flash("Comment Deleted.", category="info")
    return redirect(url_for("teams.view_team", team_id=team_id))
