import postgresqlite

from flask import Flask, render_template, request, redirect, url_for, session, flash

db = postgresqlite.connect()

app = Flask(__name__)
app.secret_key = "my_secret_key"

@app.route('/')
def index():
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('login'))

    return render_template("index.html")


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
        name = request.form['username']
        password = request.form['password']

        # Check the database if these values exist
        player = db.query_row("""
                        SELECT *
                        FROM users
                        WHERE name = :name
                        """, name=name)

        # Check if player exists
        if player:
            # Check if the password matches
            if player["password"] == password:
                session["user_id"] = player["id"]
                flash("You have been successfully logged in!", category="info")
                return redirect(url_for("index"))
            else:
                flash("Wrong password! Try again.", category="error")
                return redirect(url_for("login"))

    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True)
