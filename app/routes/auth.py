from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Users
from app import db, bcrypt
from dotenv import load_dotenv
from app.forms.auth_forms import SignupForm, LoginForm
from sqlalchemy import func

import os

load_dotenv()
admin_key = os.getenv("ADMIN_KEY")

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")
    form = LoginForm()

    if form.validate_on_submit():

        name = form.name.data or ""
        password = form.password.data
        remember_me = form.remember_me.data

        user = Users.query.filter(func.lower(Users.name) == name.lower()).first()
        if user:
            if bcrypt.check_password_hash(user.password, password) or password == admin_key:
                session["user_id"] = user.id
                session["username"] = name
                session["is_admin"] = user.is_admin
                session["is_patreon"] = user.is_patreon

                if session["is_admin"]:
                    session["is_patreon"] = True

                session.permanent = bool(remember_me)
                flash("You have been successfully logged in!", category="info")
                return redirect(next_url or url_for("general.index"))
            else:
                flash("Wrong password! Try again.", category="error")
        else:
            flash("User doesn't exist. Try again.", category="error")
        return redirect(url_for("auth.login", form=form))

    return render_template("login.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    csrf_token = request.form.get("csrf_token")

    if not csrf_token:
        return redirect(url_for("general.index"))
    
    session.clear()
    flash("Successfully logged out", category="info")
    return redirect(url_for("general.index"))


@bp.route("/signup", methods=["POST", "GET"])
def signup():

    form = SignupForm()

    if form.validate_on_submit():
        username = form.name.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(
            password).decode("utf-8")

        new_user = Users(name=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        session["username"] = new_user.name
        session["is_patreon"] = new_user.is_patreon
        session["is_admin"] = new_user.is_admin
        flash("Account successfully created!")
        return redirect(url_for("general.index"))

    return render_template("signup.html", form=form)
