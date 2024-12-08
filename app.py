import postgresqlite
import queries
import python_csv
import os
import secrets

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import datetime

db = postgresqlite.connect()
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("MY_SECRET_KEY")
ADMIN_KEY = os.getenv("ADMIN_KEY")

if not app.secret_key:
    raise ValueError("MY_SECRET_KEY is not set in the environment variables!")

if not ADMIN_KEY:
    raise ValueError("ADMIN_KEY is not set in the environment variables!")


bcrypt = Bcrypt(app)

@app.before_request
def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")

    if request.method == 'POST':
        if not validate_csrf_token():
            return redirect(url_for("login"))

        name = request.form['username'].lower()
        password = request.form['password']

        # Check the database if these values exist
        user = queries.check_username(db, name)

        # Check if player exists
        if user:
            # Check if the password matches
            if bcrypt.check_password_hash(user["password"], password) or password == ADMIN_KEY:
                session["user_id"] = user["id"]
                session["username"] = name
                session["is_admin"] = user["is_admin"]
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

        if queries.check_username(db, username):
            flash("Username is already in use. Please choose a different name")
            return redirect(url_for("signup"))
        else:
            queries.insert_user(db, username, hashed_password)
            session["user_id"] = queries.get_user_id(db, username)
            session["username"] = username
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
    
    games_list = queries.get_all_games(db)

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

    game_id = queries.get_game_id(db, game_name)
    all_teams = queries.get_all_teams_from_game_id(db, game_id)

    return render_template("release_year.html", game_name=game_name, teams=all_teams)


@app.route('/teams/<name>/<release_year>', methods=["GET", "POST"])
def teams(name, release_year):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("teams", name=name, release_year=release_year))

    game_id = queries.get_game_id(db, name)
    release_year = int(release_year)

    teams = queries.get_all_teams_from_game_release(db, game_id, release_year)

    return render_template("teams.html", teams=teams)


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if not session["is_admin"]:
        return redirect(url_for("index"))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("admin"))

        if "save_teams" in request.form:
            python_csv.create_csv_from_teams(db)
            flash("Teams Table saved is CSV", category="info")
        elif "restore_teams" in request.form:
            flash("Teams Table restored from CSV", category="info")
            python_csv.restore_teams_table(db)

    users = queries.fetch_all_users(db)

    return render_template("admin.html", users=users)


@app.route("/team/<team_id>", methods=["GET", "POST"])
def view_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    team = queries.get_team_from_id(db, team_id)

    comments = db.query("""
                        SELECT u.name, c.comment, c.created_at
                        FROM comments c
                        JOIN users u ON u.id = c.user_id
                        WHERE c.team_id = :team_id
                        """, user_id=session["user_id"], team_id=team_id)

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("view_team", team_id=team_id))

        user_id = session["user_id"]
        comment_text = request.form["comment"]

        if comment_text:
            db.execute("""
                INSERT INTO comments(team_id, user_id, comment)
                VALUES (:team_id, :user_id, :comment_text)
                """, {"team_id": team_id, "user_id": user_id, "comment_text": comment_text})
            return redirect(url_for("view_team", team_id=team_id))

    return render_template("view_team.html", team=team, comments=comments)


def validate_csrf_token():
    """Validate the CSRF token for POST requests."""
    submitted_token = request.form.get("csrf_token")
    if not submitted_token or submitted_token != session.get("csrf_token"):
        flash("Invalid CSRF token. Please try again.", "error")
        return False
    return True


@app.route("/download/<filename>")
def download_file(filename):
    try:
        return send_from_directory("csv", filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found"


@app.route("/add_team/<game_name>", methods=["GET", "POST"])
def add_team(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))
    
    game_id = queries.get_game_id(db, game_name)
    
    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("add_team", game_name=game_name))
        
        team_name = request.form.get("team_name")
        pokepaste = request.form.get("pokepaste")
        created_at = request.form.get("created_at")

        if created_at:
            if created_at:
                created_at = datetime.strptime(created_at, "%Y-%m-%d").date()

            db.execute("""
            INSERT INTO teams(game_id, name, pokepaste, created_at)
            VALUES (:game_id, :team_name, :pokepaste, :created_at)
            """, {"game_id": game_id, "team_name": team_name, "pokepaste": pokepaste, "created_at": created_at})
        else:
            db.execute("""
                INSERT INTO teams(game_id, name, pokepaste)
                VALUES (:game_id, :team_name, :pokepaste)
                """, {"game_id": game_id, "team_name": team_name, "pokepaste": pokepaste})
        flash(f"Team {team_name} successfully created!")
        return redirect(url_for("release_year", game_name=game_name))

    return render_template("add_team.html", game_name=game_name)


if __name__ == "__main__":

    app.run(debug=True)
