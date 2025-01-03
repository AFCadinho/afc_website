import random

from flask import Blueprint, render_template, session, send_from_directory, redirect, url_for, flash
from app.models import Teams, Pokemon, LatestVideo
from app.pokemon_requests import fetch_sprite_for_name
from app import db
from app.youtube_requests import get_latest_video

bp = Blueprint('general', __name__)


@bp.route("/", methods=["GET", "POST"])
def index():
    # Make sure every Pokemon has sprite before rendering page
    pokemon = Pokemon.query.filter(Pokemon.sprite == "default").all()
    if len(pokemon) > 0:
        add_sprites_to_all_pokemon()

    video_url = None
    video_title = None

    latest_video = LatestVideo.query.order_by(
        LatestVideo.updated.desc()).first()

    if not latest_video:
        video_url, video_title = get_latest_video()
        if video_url:
            latest_video = LatestVideo(
                video_id=video_url.split("/")[-1],
                title=video_title,
                url=video_url
            )
            db.session.add(latest_video)
            db.session.commit()
    else:
        video_url = latest_video.url
        video_title = latest_video.title

    pokemon_teams = Teams.query.filter(Teams.patreon_post == False).order_by(
        Teams.created_at.desc()).limit(3).all()

    # For count All Current Patreon Only Teams
    patreon_teams = Teams.query.filter(Teams.patreon_post == True).all()
    patreon_teams_count = len(patreon_teams)

    if session.get("is_patreon"):
        pokemon_teams = Teams.query.order_by(
            Teams.created_at.desc()).limit(3).all()

    if pokemon_teams:
        for team in pokemon_teams:
            random.shuffle(team.pokemon)
        return render_template("index.html", session=session, pokemon_teams=pokemon_teams, video_url=video_url, 
                               video_title=video_title, patreon_teams_count=patreon_teams_count)

    flash("No Pokemon Teams available.", category="error")
    return redirect(url_for("general.index"))


def add_sprites_to_all_pokemon():
    print("ADD SPRITES TO AL POKEMON FUNCTION")
    pokemon = Pokemon.query.filter(
        Pokemon.sprite == "default").all()

    for poke in pokemon:
        poke.sprite = fetch_sprite_for_name(poke.name) or ""

    db.session.commit()


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route('/logo')
def serve_logo():
    return send_from_directory('static/images', 'logo.png')
