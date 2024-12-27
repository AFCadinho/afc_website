from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Users
from app import db, bcrypt
from dotenv import load_dotenv
from app.forms.auth_forms import SignupForm, LoginForm

import os

load_dotenv()
admin_key = os.getenv("ADMIN_KEY")

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")
    form = LoginForm()

    if form.validate_on_submit():

        name = form.name.data
        password = form.password.data
        remember_me = form.remember_me.data

        user = Users.query.filter_by(name=name).first()
        if user:
            if bcrypt.check_password_hash(user.password, password) or password == admin_key:
                session["user_id"] = user.id
                session["username"] = name
                session["is_admin"] = user.is_admin
                session["is_patreon"] = user.is_patreon
                session.permanent = bool(remember_me)
                flash("You have been successfully logged in!", category="info")
                return redirect(next_url or url_for("general.index"))
            else:
                flash("Wrong password! Try again.", category="error")
        else:
            flash("User doesn't exist. Try again.", category="error")
        return redirect(url_for("auth.login", form=form))

    return render_template("login.html", form=form)


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
        flash("Account successfully created!")
        return redirect(url_for("general.index"))

    return render_template("signup.html", form=form)
