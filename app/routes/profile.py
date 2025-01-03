from flask import Blueprint, render_template, redirect, url_for, flash
from app.models import Users
from app.forms.profile_forms import UpdateProfileForm
from app import db, bcrypt
from app.utils import login_required


bp = Blueprint('profile', __name__)


@bp.route("/profile/<int:user_id>")
@login_required
def view_profile(user_id):    
    user = Users.query.filter_by(id=user_id).first()
    
    return render_template("profile.html", user=user)


@bp.route("/profile/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    user = Users.query.filter_by(id=user_id).first()
    form = UpdateProfileForm(obj=user)

    if form.validate_on_submit():
        password = form.password.data
        if password:
            hashed_password = bcrypt.generate_password_hash(
                password).decode("utf-8")
            user.password = hashed_password
        
        user.name = str(form.name.data).lower()
        user.email = str(form.email.data).lower()
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.view_profile", user_id=user.id))
    
    return render_template("edit_profile.html", form=form , user=user)
    
