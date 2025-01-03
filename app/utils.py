import re

from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to log in to view this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("You do not have the required permissions to view this page.", "danger")
            return redirect(url_for("general.index"))
        return f(*args, **kwargs)
    return decorated_function


def patreon_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_patreon"):
            flash("You need to be our Patreon Member to see this page.", "warning")
            return redirect(url_for('patreon.patreon_benefits', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def validate_csrf_token():
    submitted_token = request.form.get("csrf_token")
    if not submitted_token or submitted_token != session.get("csrf_token"):
        flash("Invalid CSRF token. Please try again.", "error")
        return False
    return True


def check_bad_word(field, bad_words):
    for bad_word in bad_words:
        # Split the username by either underscore or hyphen
        username_parts = re.split("_|-", field.data.lower())

        # Check each part of the username against the bad word
        for part in username_parts:
            if bad_word.lower() in part.lower():  # Case-insensitive comparison
                return True
    return False


def check_if_name_used(field, used_names):
    for name in used_names:
        typed_name = field.data
        if field.data.lower() == name.lower():
            return typed_name
    return None


def convert_string_to_bool(string):
    if string.lower() == "true":
        return True
    else:
        return False