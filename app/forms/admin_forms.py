import app.validators as val
import app.utils as utils

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class BannedNamesForm(FlaskForm):
    name = StringField("Banned Name",
                       validators=[
                           DataRequired(),
                           val.validate_username
                       ])

    submit = SubmitField("Add Banned Name")

    def __init__(self, used_names=None, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.__used_names = used_names or []

    def validate_name(self):
        username = utils.check_if_name_used(self, self.__used_names)
        if username:
            raise ValidationError(
                f"{username} is already in use. Please choose another name")
