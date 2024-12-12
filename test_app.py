import sqlalchemy as sa
import os
import secrets


from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, request, render_template, flash, url_for, redirect
from dotenv import load_dotenv
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


load_dotenv()
DATABASE_URI_1 = os.getenv("DATABASE_URI_1")
DATABASE_URI_2 = os.getenv("DATABASE_URI_2")
DATABASE_URI = str(DATABASE_URI_1) + str(DATABASE_URI_2)
ADMIN_KEY = os.getenv("ADMIN_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("MY_SECRET_KEY")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
db = SQLAlchemy(app)


with app.app_context():
    db.drop_all()
    db.create_all()


# ORM
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
    created_at = sa.Column(sa.Date, default=datetime.now(timezone.utc))
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
    created_at = sa.Column(sa.DateTime, default=datetime.now(timezone.utc))


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


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("index"))
        
        if "logout" in request.form:
            session.clear()
            flash("Successfully logged out", category="info")
            return redirect(url_for("login"))

    return render_template("index.html", session=session)


if __name__ == "__main__":
    app.run(debug=True)
