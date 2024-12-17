from wtforms import ValidationError

def validate_username(form, field):
        if not (field.data[0].isalpha() or field.data[0].isdigit()) or not (field.data[-1].isalpha() or field.data[-1].isdigit()):
            raise ValidationError(
                f"{field.label.text} has to start and end with a letter or number")