from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.models import Users, BannedNames, Bans
from app.utils import validate_csrf_token
from app.forms.admin_forms import BannedNamesForm
from app import db
from app.forms.admin_forms import BanForm
from datetime import datetime

bp = Blueprint('admin', __name__)


@bp.route("/admin", methods=["POST", "GET"])
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("general.index"))

    if request.method == "POST":
        if not validate_csrf_token():
            return redirect(url_for("admin.admin"))

    users = Users.query.order_by(
        Users.is_admin.desc(),  # Admins first
        Users.name.asc()        # Then sort alphabetically
    ).all()

    ban_form = BanForm()

    return render_template("admin.html", users=users, ban_form=ban_form)


@bp.route("/admin/dashboard")
def admin_dashboard():
    user_count = Users.query.count()  # Count total users
    admin_count = Users.query.filter_by(is_admin=True).count()  # Count admins
    banned_count = Users.query.filter_by(is_banned=True).count()  # Count banned users

    return render_template(
        "admin_dashboard.html",
        user_count=user_count,
        admin_count=admin_count,
        banned_count=banned_count
    )


@bp.route("/admin/banned_names", methods=["GET", "POST"])
def banned_names_page():
    form = BannedNamesForm()

    if form.validate_on_submit():
        name = form.name.data

        if name:
            new_banned_name = BannedNames(name=name)
            db.session.add(new_banned_name)
            db.session.commit()
            flash(f"{new_banned_name.name} Added to Banned Names list.")


    banned_names = BannedNames.query.all()
    return render_template("banned_names.html", banned_names=banned_names, form=form)


@bp.route("/ban_user/<int:user_id>", methods=["GET","POST"])
def ban_user(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return redirect(url_for("admin.admin"))
    
    form = BanForm()
    
    ban_record = Bans.query.filter_by(user_id=user.id).first()
    if ban_record:
        form = BanForm(obj=ban_record)

    if form.validate_on_submit():
        action = None
        if form.ban.data and not user.is_banned:
            # Ban the user
            user.is_banned = True
            ban_record = Bans(
                user_id=user.id,
                reason=form.reason.data,
                banned_by=session.get("user_id")
            )
            db.session.add(ban_record)
            action = "banned"

        elif form.edit.data and user.is_banned:
            # Update the existing ban reason
            ban_record.reason = form.reason.data
            ban_record.updated_by = session.get("user_id")
            ban_record.updated_at = datetime.now()
            action = "updated"
    
        elif form.unban.data and user.is_banned:
            # Unban the user
            user.is_banned = False
            action = "unbanned"
            if ban_record:
                db.session.delete(ban_record)
        
        db.session.commit()
        flash(f"{user.name} was {action} successfully. {'Ban reason updated.' if action == 'updated' else ''}", "success")
        return redirect(url_for("admin.admin"))

    return render_template("ban_user.html", user=user, form=form, ban_record=ban_record)