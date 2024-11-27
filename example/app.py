import postgresqlite

from flask import Flask, render_template, request, redirect, url_for, session, flash
from random import randint

### poetry run postgresqlite pgcli

# Connect to the database
db = postgresqlite.connect()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = "Adinho_is_awesome"


with open('words.txt', encoding='utf-8') as file:
    words = file.read().strip().split("\n")


def start_new_game(player_id):
    # global secret_word, guessed_words
    secret_word = words[randint(0, len(words) - 1)]
    print(secret_word)
    return db.query_value("""
            INSERT INTO game (player_id, secret)
            VALUES (:player_id, :secret_word)
            RETURNING id;
    """, player_id=player_id, secret_word=secret_word)


def guess_to_hint(guess, secret):
    """Given a `guess` and a `secret` word as strings, it returns a list with one tuple for
    each letter in the guess, where the first item is the letter, and the second item is one
    of the strings `correct`, `wrong` or `misplaced`, describing what applies for that letter.
    """
    result = []
    for idx, letter in enumerate(guess):
        actual = secret[idx]
        if actual == letter:
            result.append((letter, 'correct'))
        elif letter in secret:
            result.append((letter, 'misplaced'))
        else:
            result.append((letter, 'wrong'))
    return result


@app.route("/", methods=['GET', 'POST'])
def index():

    # Keeping track of all the guessed words
    guessed_words = []

    # Check if the user is logged in
    if "player_id" not in session:
        return redirect(url_for("login"))

    # Add a logout link to the header of the page
    if "logout" in request.form:
        session.pop("player_id", None)
        flash("Successfully logged out", category="info")
        return redirect(url_for("login"))

    player_id = session["player_id"]

    # Check if there is an existing active game
    game = db.query_row("""
                SELECT *
                FROM game
                WHERE player_id = :player_id AND result IS NULL
                ORDER BY time DESC
                LIMIT 1;
                """, player_id=player_id)

    # Create new game if no game exists
    if not game:
        game_id = start_new_game(player_id)
        game = db.query_row("""
                    SELECT *
                    FROM game
                    WHERE id = :game_id
                    """, game_id=game_id)
        return render_template("index.html")

    else:
        game_id = game["id"]
        secret_word = game["secret"]

        # Fetch guessed words for the current game
        guessed_words = db.query_column("""
            SELECT word
            FROM guess
            WHERE game_id = :game_id
        """, game_id=game_id) or []

        message = ""
        game_over = False

        if request.method == "POST":
            if 'reset' in request.form:
                game_id = start_new_game(player_id)
                return redirect(url_for('index'))

            # When the user is POSTing a new guess, add it to the list
            guess = request.form.get("word")
            if guess:
                if guess not in words:
                    print(guess)
                    message = f"{guess} is not a valid word you moron!"
                else:
                    db.execute("""
                        INSERT INTO guess (game_id, word)
                        VALUES(:game_id, :guess);
                        """, {"game_id": game_id, "guess": guess})

                    # Get the list of guessed words
                    guessed_words = db.query_column("""
                                        SELECT word
                                        FROM guess
                                        WHERE game_id = :game_id;
                                        """, game_id=game_id)

                    if guess == secret_word:
                        message = "Congratulations! You've guessed the word!"
                        game_over = True
                        db.execute("""
                            UPDATE game
                            SET result = :result
                            WHERE id = :game_id;
                            """, {"game_id": game_id, "result": len(guessed_words)})

                    elif len(guessed_words) > 14:
                        message = f"Too many tries, are you an idiot?! GAME OVER! The correct word was: {
                            secret_word}"
                        game_over = True
                        db.execute("""
                            UPDATE game
                            SET result = :result
                            WHERE id = :game_id
                            """, {"game_id": game_id, "result": -1})

        # Render a template, passing it the list of guessed words converted to hints (`guess_to_hint`)
        hints = [guess_to_hint(guess, secret_word) for guess in guessed_words]

        return render_template("index.html", hints=hints, message=message, game_over=game_over)


@app.route("/history", methods=['GET'])
def show_history():
    """Show history of the attempts the user made."""
    if "player_id" not in session:
        return redirect(url_for("login"))
    
    ## All Game Rows
    games = db.query("""
            SELECT game.id, game.secret, game.result, player.name
            FROM game
            JOIN player ON game.player_id = player.id
            WHERE game.player_id = :player_id
            """, player_id=session["player_id"])
    
    ## Current secret word
    current_secret_word = db.query_value("""
                            SELECT game.secret
                            FROM game
                            JOIN player ON game.player_id = player.id
                            WHERE player.id = :player_id
                            ORDER BY time DESC
                            LIMIT 1
                            """, player_id=session["player_id"])
    
    return render_template("history.html", games=games, current_secret_word=current_secret_word)


@app.route("/games/<int:game_id>")
def view_game(game_id):
    game = db.query_row("""
                SELECT *
                FROM game
                WHERE id = :game_id
                """, game_id=game_id)
    if not game:
        flash("Game not found", category="error")
        return redirect(url_for("show_history"))

    guesses = db.query_column("""
                SELECT word
                FROM guess
                WHERE game_id = :game_id
                """, game_id=game_id)
    
    return render_template("view_game.html", game=game, guesses=guesses)



@app.route("/login", methods=["POST", "GET"])
def login():
    # Get information from the form.
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        # Check the database if these values exist
        player = db.query_row("""
                        SELECT *
                        FROM player
                        WHERE name = :name
                        """, name=name)

        # Check if player exists
        if player:
            # Check if the password matches
            if player["password"] == password:
                session["player_id"] = player["id"]
                flash("You have been successfully logged in!", category="info")
                return redirect(url_for("index"))
            else:
                flash("Wrong password! Try again.", category="error")
                return redirect(url_for("login"))

        # Insert new player into database
        else:
            player_id = db.query_value("""
                    INSERT INTO player(name, password)
                    VALUES(:name, :password)
                    RETURNING id
                    """, name=name, password=password)
            session["player_id"] = player_id
            flash("Registration successful! You are now logged in",
                  category="information")
            return redirect(url_for("index"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
