import app.validators as val
import app.utils as utils

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError


class LoginForm(FlaskForm):
    name = StringField("Username",
                       validators=[
                           DataRequired(),
                           Length(min=3, max=15),
                           Regexp(
                               regex=r"^[a-zA-Z0-9_-]+$",
                               message="Username can only contain letters, numbers, underscores, and hyphens."
                           ),
                           val.validate_username
                       ])
    password = PasswordField("Password",
                           validators=[
                               DataRequired(),
                           ])
    remember_me = BooleanField("Remember Me")

    submit = SubmitField("Log In")


class SignupForm(FlaskForm):
    name = StringField("Username",
                       validators=[
                           DataRequired(),
                           Length(min=3, max=15),
                           Regexp(
                               regex=r"^[a-zA-Z0-9_-]+$",
                               message="Username can only contain letters, numbers, underscores, and hyphens."
                           ),
                           val.validate_username
                       ])
    password = StringField("Password",
                           validators=[
                               DataRequired(),
                               Length(min=8, max=20),
                           ])

    create_user = SubmitField("Create User")

    def __init__(self, bad_word=None, used_names=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__bad_words = bad_word or []
        self.__used_names = used_names or []

    def _validate_name(self, field):
        for bad_word in self.__bad_words:
            if bad_word.lower() in field.data.lower():
                raise ValidationError(
                    "Username not available. Please choose a different one")

    def validate_name(self, field):
        if utils.check_bad_word(field, self.__bad_words):
            raise ValidationError(
                f"Username not available. Please choose another username")

        username = utils.check_if_name_used(field, self.__used_names)
        if username:
            raise ValidationError(
                f"{username} is already in use. Please choose another name")
