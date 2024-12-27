from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL, Optional, ValidationError
from app.constants import VALID_ARCHETYPES
from app.queries.team_queries import get_distinct_archetypes, get_distinct_pokemon_names


class TeamForm(FlaskForm):
    name = StringField("Team Name",
                       validators=[
                           DataRequired()
                       ])
    pokepaste = StringField("Pokepaste Link",
                            validators=[
                                DataRequired(),
                                URL()
                            ])
    archetype = SelectField("Archetype",
                            choices=[(archetype, archetype) for archetype in VALID_ARCHETYPES ],
                            validators=[
                                DataRequired()
                            ])
    created_at = DateField("Created at", format="%Y-%m-%d",
                           validators=[
                               Optional()
                           ])
    patreon_post = BooleanField("Patreon Exclusive")
    submit = SubmitField("Create Team")
    edit_submit = SubmitField("Edit Team")


class FilterTeamForm(FlaskForm):
    archetype = SelectField("Archetype",
                            validators=[
                                Optional()
                            ])
    created_at = DateField("Created After", format="%Y-%m-%d",
                           validators=[
                               Optional()
                           ])
    pokemon_name = StringField("Pokemon",
                               validators=[Optional()],
                               render_kw={"list": "pokemon_list"})
    submit = SubmitField("Filter Teams")

    def __init__(self, game_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically add Archetype Choices
        archetypes = get_distinct_archetypes()
        self.archetype.choices = [("", "All Archetypes")] + [(archetype[0], archetype[0]) for archetype in archetypes] # type: ignore
        self.__pokemon_names = get_distinct_pokemon_names(game_id)


    def validate_pokemon_name(self, field):
        # Extract list of Pokémon names (case insensitive)
        pokemon_names = [name[0].lower() for name in self.__pokemon_names]

        # Validate if the Pokémon exists (case insensitive match)
        if field.data and not any(name.lower() == field.data.lower() for name in pokemon_names):
            raise ValidationError("No teams with this Pokémon exist. Please choose another Pokémon name.")
