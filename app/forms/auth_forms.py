import app.validators as val
import app.utils as utils

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from app.queries.admin_queries import fetch_banned_names
from app.queries.auth_queries import fetch_used_names, check_if_banned

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

    def validate_name(self, field):
        input_name = field.data

        if check_if_banned(input_name):
            raise ValidationError(
                f"Username '{input_name}' is banned. Unable to login."
            )


class SignupForm(FlaskForm):
    name = StringField("Username",
                       validators=[
                           DataRequired(),
                           Length(min=3, max=15),
                           Regexp(
                               regex=r"^[a-zA-Z0-9]+$",
                               message="Username can only contain letters, numbers."
                           ),
                           val.validate_username
                       ])
    password = StringField("Password",
                           validators=[
                               DataRequired(),
                               Length(min=8, max=20),
                           ])

    create_user = SubmitField("Create User")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__banned_names = fetch_banned_names() or []
        self.__used_names = fetch_used_names() or []

    def validate_name(self, field):
        
        if utils.check_bad_word(field, self.__banned_names):
            raise ValidationError(
                f"Username not available. Please choose another username")

        username = utils.check_if_name_used(field, self.__used_names)
        if username:
            raise ValidationError(
                f"{username} is already in use. Please choose another name")
