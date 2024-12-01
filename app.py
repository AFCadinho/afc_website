import postgresqlite
import queries
import python_csv

from flask import Flask, render_template, request, redirect, url_for, session, flash

db = postgresqlite.connect()

app = Flask(__name__)
app.secret_key = "my_secret_key"


@app.route('/', methods=["GET", "POST"])
def index():

    if "logout" in request.form:
        session.clear()

        flash("Successfully logged out", category="info")
        return redirect(url_for("login"))

    return render_template("index.html", session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        name = request.form['username'].lower()
        password = request.form['password']

        # Check the database if these values exist
        player = queries.check_username(db, name)

        # Check if player exists
        if player:
            # Check if the password matches
            if player["password"] == password:
                session["user_id"] = player["id"]
                session["username"] = name
                session["is_admin"] = player["is_admin"]
                flash("You have been successfully logged in!", category="info")
                return redirect(url_for("index"))
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

        if queries.check_username(db, username):
            flash("Username is already in use. Please choose a different name")
            return redirect(url_for("signup"))
        else:
            queries.insert_user(db, username, password)
            session["user_id"] = queries.get_user_id(db, username)
            session["username"] = username
            flash("Account successfully Created!")
            return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/games", methods=["POST", "GET"])
def games():
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login'))

    games_list = queries.get_all_games(db)

    return render_template("games.html", games_list=games_list)


@app.route("/release_year/<game_name>", methods=["GET", "POST"])
def release_year(game_name):
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
        return redirect(url_for('login'))

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
        return redirect(url_for("login"))

    team = queries.get_team_from_id(db, team_id)
    # comments = db.query("""
    #              SELECT *
    #              FROM comments
    #              WHERE team_id = :team_id
    #              """, team_id=team_id)
    # username = db.query_value("""
    #                 SELECT name
    #                 FROM users
    #                 WHERE id = :user_id
    #                 """, user_id=session["user_id"])
    
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
