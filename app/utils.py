from flask import session, request, flash

import re


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
