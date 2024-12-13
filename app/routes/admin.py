from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models import Users
from app.utils import validate_csrf_token

bp = Blueprint('admin', __name__)

@bp.route("/admin", methods=["POST", "GET"])
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("general.index"))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("admin.admin"))

    users = Users.query.all()
    return render_template("admin.html", users=users)
