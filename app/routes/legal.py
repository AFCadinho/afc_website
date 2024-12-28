from flask import Blueprint, render_template

bp = Blueprint('legal', __name__)

@bp.route("/privacy")
def privacy_policy():
    return render_template("privacy_policy.html")

@bp.route("/terms")
def terms_of_service():
    return render_template("terms_of_service.html")
