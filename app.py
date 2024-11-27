from flask import Flask, render_template, request, session, flash, redirect, url_for
import postgresqlite

app = Flask(__name__)
db = postgresqlite.connect()
app.secret_key = "my_secret_key"

@app.route('/')
def index():
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
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        query = "SELECT id, password FROM users WHERE username = %s;"
        result = db.execute(query, (username,)).fetchone()

        if result:
            user_id, hashed_password = result
            # Check password hash
            if check_password_hash(hashed_password, password):
                session['user_id'] = user_id
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid password.", "danger")
        else:
            flash("User not found.", "danger")

    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True)
