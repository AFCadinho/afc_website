import app.validators as val
import app.utils as utils

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length, Optional
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


class BanForm(FlaskForm):
    reason = TextAreaField("Reason for Ban/Unban",
                           validators=[
                               Optional(),
                               Length(min=5, max=200)
                           ])
    ban = SubmitField("Ban")
    unban = SubmitField("Unban")
    edit = SubmitField("Edit Ban")


class DeleteUserForm(FlaskForm):
    submit = SubmitField("Delete User")