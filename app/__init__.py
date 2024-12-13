from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import secrets
from datetime import timedelta

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("MY_SECRET_KEY")
    app.permanent_session_lifetime = timedelta(days=30)
    DATABASE_URI_1 = os.getenv("DATABASE_URI_1")
    DATABASE_URI_2 = os.getenv("DATABASE_URI_2")
    database_uri = os.getenv("DATABASE_URI")
    if not database_uri:
        database_uri = str(DATABASE_URI_1) + str(DATABASE_URI_2)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Set CSRF token before each request
    @app.before_request
    def set_csrf_token(): # type: ignore
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
            print("New CSRF Token Set:", session["csrf_token"])
        else:
            print("Existing CSRF Token:", session["csrf_token"])

    with app.app_context():
        # Import and register each Blueprint directly
        from app.routes import general, auth, admin, games, teams
        app.register_blueprint(general.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(games.bp)
        app.register_blueprint(teams.bp)

    return app
