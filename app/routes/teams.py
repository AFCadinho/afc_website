from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Teams, Comments, Games
from app import db
from app.utils import validate_csrf_token
from datetime import datetime

bp = Blueprint('teams', __name__)

@bp.route("/team/<team_id>", methods=["GET", "POST"])
def view_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    team = Teams.query.filter_by(id=team_id).first()
    comments = Comments.query.filter_by(user_id=session["user_id"], team_id=team_id).all()

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("teams.view_team", team_id=team_id))

        user_id = session["user_id"]
        comment_text = request.form["comment"]

        if comment_text:
            comment = Comments(team_id=team_id, user_id=user_id, comment=comment_text)
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
            created_at=datetime.strptime(created_at, "%Y-%m-%d").date() if created_at else None
        )
        db.session.add(team)
        db.session.commit()
        flash(f"Team {team_name} successfully created!")
        return redirect(url_for("games.release_year", game_name=game_name))

    return render_template("add_team.html", game_name=game_name)
