import sqlalchemy as sa
import os
import secrets

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, request, render_template, flash, url_for, redirect
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from datetime import timedelta
from sqlalchemy.sql import func
from flask_migrate import Migrate


load_dotenv()
DATABASE_URI_1 = os.getenv("DATABASE_URI_1")
DATABASE_URI_2 = os.getenv("DATABASE_URI_2")
database_uri = os.getenv("DATABASE_URI")
if not database_uri:
    database_uri = str(DATABASE_URI_1) + str(DATABASE_URI_2)

ADMIN_KEY = os.getenv("ADMIN_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("MY_SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=30)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)


class Users(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    password = sa.Column(sa.Text, nullable=False)
    is_admin = sa.Column(sa.Boolean, default=False)
    is_banned = sa.Column(sa.Boolean, default=False)
    comments = relationship(
        "Comments", backref="users", cascade="all, delete-orphan")


class Games(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    teams = relationship("Teams", backref="games",
                         cascade="all, delete-orphan")


class Teams(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    game_id = sa.Column(sa.Integer, sa.ForeignKey("games.id"), nullable=False)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    pokepaste = sa.Column(sa.Text, nullable=False, unique=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now())
    pokemon = relationship(
        "Pokemon", backref="team", cascade="all, delete-orphan")
    comments = relationship(
        "Comments", backref="team", cascade="all, delete-orphan")


class Pokemon(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    team_id = sa.Column(sa.Integer, sa.ForeignKey("teams.id"), nullable=False)
    name = sa.Column(sa.Text, nullable=False)


class Comments(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    team_id = sa.Column(sa.Integer, sa.ForeignKey("teams.id"), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    comment = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime, server_default=func.now())


# with app.app_context():
#     # db.drop_all()
#     db.create_all()
#     current_database = database_uri[-10:]
#     print(f"Current Database: {current_database}")


@app.before_request
def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


def validate_csrf_token():
    """Validate the CSRF token for POST requests."""
    submitted_token = request.form.get("csrf_token")
    if not submitted_token or submitted_token != session.get("csrf_token"):
        flash("Invalid CSRF token. Please try again.", "error")
        return False
    return True


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("index"))

        if "logout" in request.form:
            session.clear()
            flash("Successfully logged out", category="info")
            return redirect(url_for("login"))

    return render_template("index.html", session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")

    if request.method == 'POST':
        if not validate_csrf_token():
            return redirect(url_for("login"))

        name = request.form['username'].lower()
        password = request.form['password']
        remember_me = request.form.get("remember_me")

        # Check if user exists
        user = Users.query.filter_by(name=name).first()
        if user:
            # Check if the password matches
            if bcrypt.check_password_hash(user.password, password) or password == ADMIN_KEY:
                session["user_id"] = user.id
                session["username"] = name
                session["is_admin"] = user.is_admin

                if remember_me:
                    session.permanent = True
                else:
                    session.permanent = False

                flash("You have been successfully logged in!", category="info")
                return redirect(next_url or url_for("index"))
            else:
                flash("Wrong password! Try again.", category="error")
                return redirect(url_for("login"))
        else:
            flash("User doesn't exist. Try again")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("signup"))

        username = request.form["username"].lower()
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(
            password).decode("utf-8")

        user = Users.query.filter_by(name=username).first()
        if user:
            flash("Username is already in use. Please choose a different name")
            return redirect(url_for("signup"))
        else:
            new_user = Users(name=username, password=hashed_password)
            session["user_id"] = new_user.id
            session["username"] = new_user.name
            flash("Account successfully Created!")
            return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/games", methods=["POST", "GET"])
def games():
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("games"))

    games_list = Games.query.order_by(Games.id).all()

    return render_template("games.html", games_list=games_list)


@app.route("/release_year/<game_name>", methods=["GET", "POST"])
def release_year(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("release_year", game_name=game_name))

        release_year = request.form["release_year"]
        return redirect(url_for("teams", name=game_name,
                                release_year=release_year))

    print(f"ATTENTION----------: {game_name}")
    game = Games.query.filter_by(name=game_name).first()
    game_id = game.id

    all_teams = Teams.query.filter_by(game_id=game_id).all()

    return render_template("release_year.html", game_name=game_name, teams=all_teams)


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if not session["is_admin"]:
        return redirect(url_for("index"))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("admin"))

    users = Users.query.all()

    return render_template("admin.html", users=users)


@app.route("/team/<team_id>", methods=["GET", "POST"])
def view_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    team = Teams.query.filter_by(id=team_id).first()

    comments = Comments.query.filter_by(
        user_id=session["user_id"], team_id=team_id).all()

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("view_team", team_id=team_id))

        user_id = session["user_id"]
        comment_text = request.form["comment"]

        if comment_text:
            comment = Comments(
                team_id=team_id, user_id=user_id, comment=comment_text)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for("view_team", team_id=team_id))

    return render_template("view_team.html", team=team, comments=comments)


@app.route("/add_team/<game_name>", methods=["GET", "POST"])
def add_team(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    game = Games.query.filter_by(name=game_name).first()
    game_id = game.id

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("add_team", game_name=game_name))

        team_name = request.form.get("team_name")
        pokepaste = request.form.get("pokepaste")
        created_at = request.form.get("created_at")

        if created_at:
            if created_at:
                created_at = datetime.strptime(created_at, "%Y-%m-%d").date()

            team = Teams(game_id=game_id, name=team_name,
                         pokepaste=pokepaste, created_at=created_at)
            db.session.add(team)
            db.session.commit()

        else:
            team = Teams(game_id=game_id, name=team_name, pokepaste=pokepaste)
            db.session.add(team)
            db.session.commit()
        flash(f"Team {team_name} successfully created!")
        return redirect(url_for("release_year", game_name=game_name))

    return render_template("add_team.html", game_name=game_name)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()
