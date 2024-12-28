from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_from_directory
from app.utils import validate_csrf_token

bp = Blueprint('general', __name__)

@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("general.index"))

        if "logout" in request.form:
            session.clear()
            flash("Successfully logged out", category="info")
            return redirect(url_for("auth.login"))

    return render_template("index.html", session=session)


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route('/logo')
def serve_logo():
    return send_from_directory('static/images', 'logo.png')
