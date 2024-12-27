from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Teams, Comments, Games, Pokemon
from app import db
from app.pokemon_requests import fetch_names_from_pokepaste, fetch_pokemon_sprites
from app.forms.team_forms import TeamForm, FilterTeamForm, DeleteTeamForm
from app.forms.comments_form import CommentForm, DeleteCommentForm
from app.queries.team_queries import get_distinct_pokemon_names

bp = Blueprint('teams', __name__)


@bp.route("/team/<team_id>")
def view_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    team = Teams.query.filter_by(id=team_id).first()
    comments = Comments.query.filter_by(team_id=team_id).all()

    if not team and not team.pokepaste:
        flash("No Team information available.", category="error")
        return render_template(url_for("index"))

    pokepaste = team.pokepaste
    pokemon_names = fetch_names_from_pokepaste(pokepaste)
    pokemon_image_dict = fetch_pokemon_sprites(pokemon_names)

    comment_form = CommentForm()
    delete_comment_form = DeleteCommentForm()
    delete_team_form = DeleteTeamForm()

    return render_template("view_team.html", team=team, comments=comments, 
                           pokemon_image_dict=pokemon_image_dict, 
                           comment_form=comment_form, delete_comment_form=delete_comment_form, delete_team_form=delete_team_form)


@bp.route("/post_comment/<int:team_id>", methods=["GET","POST"])
def post_team_comment(team_id):
    comment_form = CommentForm()

    if comment_form.validate_on_submit():

        user_id = session["user_id"]
        comment = Comments(
            team_id=team_id, user_id=user_id, comment=comment_form.comment.data)
        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
        return redirect(url_for("teams.view_team", team_id=team_id))
    
    team = Teams.query.filter_by(id=team_id).first()
    comments = Comments.query.filter_by(team_id=team_id).all()

    if not team and not team.pokepaste:
        flash("No Team information available.", category="error")
        return render_template(url_for("index"))
    
    pokepaste = team.pokepaste
    pokemon_names = fetch_names_from_pokepaste(pokepaste)
    pokemon_image_dict = fetch_pokemon_sprites(pokemon_names)
    delete_team_form = DeleteTeamForm()
    
    return render_template("view_team.html", team=team, comments=comments, pokemon_image_dict=pokemon_image_dict, 
                           comment_form=comment_form, delete_form=delete_team_form)


@bp.route("/add_team/<game_name>", methods=["GET", "POST"])
def add_team(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    game = Games.query.filter_by(name=game_name).first()
    if not game:
        flash("Game not found.", category="error")
        return redirect(url_for('games.games'))

    
    form = TeamForm()

    if form.validate_on_submit():
        new_team = Teams(
            game_id=game.id,
            name=form.name.data,
            pokepaste=form.pokepaste.data,
            archetype=form.archetype.data,
            created_at=form.created_at.data,
            patreon_post=form.patreon_post.data
        )
        db.session.add(new_team)
        db.session.commit()
        flash(f"Team {form.name.data} successfully created!")

        # Add Each Pokemon individually to Database.
        pokepaste_names = fetch_names_from_pokepaste(new_team.pokepaste)     
        pokemon_names = []
        for name in pokepaste_names:
            pokemon = Pokemon(team_id=new_team.id, name=name)
            pokemon_names.append(pokemon)

        db.session.add_all(pokemon_names)
        db.session.commit()
        flash(f"""Each Pokemon from team {
              new_team.name} have been added to the Pokemon Table.""")

        return redirect(url_for("games.filter_page", game_name=game_name))

    return render_template("add_team.html", form=form, game_name=game_name, edit=False)


@bp.route("/edit_team/<int:team_id>", methods=["GET", "POST"])
def edit_team(team_id):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login'))
    
    team = Teams.query.filter_by(id=team_id).first()
    if not team:
        flash("Team does not exist")
        return redirect(url_for("index.html"))

    form = TeamForm(obj=team)

    if form.validate_on_submit():
        form.populate_obj(team)
        db.session.commit()
        flash(f"{team.name} has been successfully updated.", "success")
        return redirect(url_for("teams.view_team", team_id=team.id))

    return render_template("add_team.html", form=form, edit=True)


@bp.route("/<game_name>/filtered_teams")
def filtered_teams(game_name):
    if "user_id" not in session:
        flash("You need to log in to view this page.", "warning")
        return redirect(url_for('auth.login', next=request.url))

    # Fetch filtered teams from session
    team_ids = session.get("filtered_teams")
    if not team_ids:
        flash("No teams found for the applied filters.", "error")
        return redirect(url_for("games.filter_page", game_name=game_name))

    # Re-query to fetch full team objects
    teams = Teams.query.filter(Teams.id.in_(team_ids)).all()

    return render_template("teams.html", teams=teams, game_name=game_name)


@bp.route("/filter_teams/<game_name>", methods=["GET","POST"])
def filter_teams(game_name):
    game = Games.query.filter_by(name=game_name).first()
    if not game:
        flash("Game not found!", "error")
        return redirect(url_for("general.index"))
    
    form = FilterTeamForm(game.id)

    if form.validate_on_submit():

        created_after = form.created_at.data
        pokemon_name = form.pokemon_name.data
        pokemon_archetype = form.archetype.data

        game_id = game.id

        # Start Building the query to fetch teams
        query = Teams.query.filter(
            Teams.game_id == game_id
        )

        # Apply release year filter
        if created_after:
            query = query.filter(Teams.created_at >= created_after).order_by(Teams.created_at.desc())

        # Apply pokemon name filter
        if pokemon_name:
            query = query.filter(Teams.pokemon.any(
                Pokemon.name.ilike(f"%{pokemon_name}%")))

        # Apply archetype filter
        if pokemon_archetype:
            query = query.filter(Teams.archetype == pokemon_archetype)

        # Get all teams from the query
        teams = query.all()

        # Save filtered team IDs in session
        team_id_list = []
        for team in teams:
            team_id_list.append(team.id)
        session["filtered_teams"] = team_id_list

        # Redirect to the teams route
        return redirect(url_for("teams.filtered_teams", game_name=game_name))
    

    all_teams = Teams.query.filter_by(
    game_id=game.id).order_by(Teams.created_at.desc()).all()

    # Get distinct Pokemon names
    pokemon_names = [p[0] for p in get_distinct_pokemon_names(game.id)]

    return render_template("filter.html", game_name=game_name, teams=all_teams, form=form, pokemon_names=pokemon_names)


@bp.route("/delete_team/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    form = DeleteTeamForm()
    team = Teams.query.filter_by(id=team_id).first()
    if not team:
        flash("No Team to delete", category="error")
        return redirect(url_for("index"))
    
    game_name = team.games.name or None

    if form.validate_on_submit():

        team_name = team.name
        db.session.delete(team)
        db.session.commit()
        print("deleted game")

        flash(f"Team {team_name} Successfully Deleted!", category="info")
    
    return redirect(url_for("games.filter_page", game_name=game_name))


@bp.route("/delete_comment/<int:team_id>/<int:comment_id>", methods=["POST"])
def delete_team_comment(team_id, comment_id):
    form = DeleteCommentForm()

    if form.validate_on_submit():
    
        comment = Comments.query.filter(
            Comments.id == comment_id, Comments.team_id == team_id).first()
        db.session.delete(comment)
        db.session.commit()
        flash("Comment Deleted.", category="info")

    
    return redirect(url_for("teams.view_team", team_id=team_id))
