from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    comment = TextAreaField(
        "Add a Comment",
        validators=[
            DataRequired(message="Comment cannot be empty."),
            Length(min=1, max=500, message="Comment must be between 1 and 500 characters.")
        ]
    )
    submit = SubmitField("Comment")
