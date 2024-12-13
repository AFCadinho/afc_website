from flask import session, request, flash
import secrets

def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

def validate_csrf_token():
    submitted_token = request.form.get("csrf_token")
    print("Submitted CSRF Token:", submitted_token)
    print("Session CSRF Token:", session.get("csrf_token"))
    if not submitted_token or submitted_token != session.get("csrf_token"):
        flash("Invalid CSRF token. Please try again.", "error")
        return False
    return True
