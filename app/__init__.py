from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    csrf.init_app(app)
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

    with app.app_context():
        # Import and register each Blueprint directly
        from app.routes import general, auth, admin, games, teams, profile, legal, patreon, youtube
        app.register_blueprint(general.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(games.bp)
        app.register_blueprint(teams.bp)
        app.register_blueprint(profile.bp)
        app.register_blueprint(patreon.bp)
        app.register_blueprint(legal.bp)
        app.register_blueprint(youtube.bp)

    return app
