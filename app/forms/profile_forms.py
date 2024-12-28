from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Email
from flask_wtf.file import FileAllowed

class UpdateProfileForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email Address (Optional)",
                        validators=[
                            Optional(),
                            Email()
                        ])
    profile_picture = FileField('Profile Picture (Optional)', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    password = PasswordField("New Password (Optional)", validators=[
        Optional(),
        Length(min=6),
        EqualTo("confirm_password", message="Passwords must match.")
    ])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[
                                         Optional()
                                     ])
    submit = SubmitField("Update Profile")
