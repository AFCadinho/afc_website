from app import db
from app.models import *

def get_distinct_archetypes():
    return db.session.query(Teams.archetype).distinct().all()

def get_distinct_pokemon_names(game_id):
    return (
        db.session.query(Pokemon.name)
        .join(Teams)  # Join Pokemon to Teams
        .filter(Teams.game_id == game_id)  # Filter by game_id
        .distinct()
        .all()
    )
