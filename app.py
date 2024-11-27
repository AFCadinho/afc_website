from flask import Flask
import postgresqlite

app = Flask(__name__)
db = postgresqlite.connect()

@app.route('/')
def home():
    return "Welcome to PokePaste Website!"


if __name__ == "__main__":
    app.run(debug=True)
