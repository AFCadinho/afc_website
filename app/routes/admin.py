from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.models import Users, BannedNames
from app.utils import validate_csrf_token
from app.forms.admin_forms import BannedNamesForm
from app import db

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


@bp.route("/admin/banned_names", methods=["GET", "POST"])
def banned_names_page():
    banned_names = BannedNames.query.all()
    users = Users.query.all()
    
    used_names = [user.name for user in users]
    form = BannedNamesForm(used_names=used_names)

    if form.validate_on_submit():
        name = form.name.data

        if name:
            new_banned_name = BannedNames(name=name)
            db.session.add(new_banned_name)
            db.session.commit()
            flash(f"{new_banned_name.name} Added to Banned Names list.")
            redirect(url_for("banned_names_page"))

    return render_template("banned_names.html", banned_names=banned_names, form=form)
