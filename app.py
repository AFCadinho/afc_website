import postgresqlite
import queries
import python_csv
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

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


@app.route('/', methods=["GET", "POST"])
def index():

    if "logout" in request.form:
        session.clear()

        flash("Successfully logged out", category="info")
        return redirect(url_for("login"))

    return render_template("index.html", session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")

    if request.method == 'POST':
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

    games_list = queries.get_all_games(db)

    return render_template("games.html", games_list=games_list)


@app.route("/release_year/<game_name>", methods=["GET", "POST"])
def release_year(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login', next=request.url))

    if request.method == "POST":
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

    game_id = queries.get_game_id(db, name)
    release_year = int(release_year)

    teams = queries.get_all_teams_from_game_release(db, game_id, release_year)

    return render_template("teams.html", teams=teams)


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if not session["is_admin"]:
        return redirect(url_for("index"))

    if request.method == "POST":
        if "save_teams" in request.form:
            python_csv.create_csv_from_teams(db)
        elif "restore_teams" in request.form:
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
        user_id = session["user_id"]
        comment_text = request.form["comment"]

        if comment_text:
            db.execute("""
                INSERT INTO comments(team_id, user_id, comment)
                VALUES (:team_id, :user_id, :comment_text)
                """, {"team_id": team_id, "user_id": user_id, "comment_text": comment_text})
            return redirect(url_for("view_team", team_id=team_id))

    return render_template("view_team.html", team=team, comments=comments)


if __name__ == "__main__":

    app.run(debug=True)
