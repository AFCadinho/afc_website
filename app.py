import postgresqlite
import queries

from flask import Flask, render_template, request, redirect, url_for, session, flash

db = postgresqlite.connect()

app = Flask(__name__)
app.secret_key = "my_secret_key"

@app.route('/', methods=["GET", "POST"])
def index():
    if "logout" in request.form:
        session.clear()
        print(session)

        flash("Successfully logged out", category="info")
        return redirect(url_for("login"))

    return render_template("index.html", session=session)


@app.route('/teams')
def teams():
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login'))
    
    teams = db.query("""
            SELECT *
            FROM pokemmo_teams
        """)

    return render_template("teams.html", teams=teams)


# Login route
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

if __name__ == "__main__":
    app.run(debug=True)
