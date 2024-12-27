import app.validators as val
import app.utils as utils

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from app.queries.admin_queries import fetch_banned_names


class BannedNamesForm(FlaskForm):
    name = StringField("Banned Name",
                       validators=[
                           DataRequired(),
                           val.validate_username
                       ])

    submit = SubmitField("Add Banned Name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.__banned_names = fetch_banned_names() or []

    def validate_name(self, field):
        username = utils.check_if_name_used(field, self.__banned_names)
        if username:
            raise ValidationError(
                f"{username} is already in use. Please choose another name")
