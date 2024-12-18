from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Users, BannedNames
from app import db, bcrypt
from app.utils import validate_csrf_token
from dotenv import load_dotenv
from app.forms import SignupForm

import os

load_dotenv()
admin_key = os.getenv("ADMIN_KEY")

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get("next")

    if request.method == 'POST':
        if not validate_csrf_token():
            return redirect(url_for("auth.login"))

        name = request.form['username'].lower()
        password = request.form['password']
        remember_me = request.form.get("remember_me")

        user = Users.query.filter_by(name=name).first()
        if user:
            if bcrypt.check_password_hash(user.password, password) or password == admin_key:
                session["user_id"] = user.id
                session["username"] = name
                session["is_admin"] = user.is_admin
                session.permanent = bool(remember_me)
                flash("You have been successfully logged in!", category="info")
                return redirect(next_url or url_for("general.index"))
            else:
                flash("Wrong password! Try again.", category="error")
        else:
            flash("User doesn't exist. Try again.", category="error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@bp.route("/signup", methods=["POST", "GET"])
def signup():
    users = Users.query.all()
    used_names = [user.name for user in users]
    
    banned_names_obj = BannedNames.query.all()
    banned_names = [banned_name.name for banned_name in banned_names_obj]

    form = SignupForm(bad_word=banned_names, used_names=used_names)
    
    if form.validate_on_submit():
        username = form.name.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        if Users.query.filter_by(name=username).first():
            flash("Username is already in use. Please choose a different name")
            return render_template("signup.html", form=form)
        else:
            new_user = Users(name=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            session["username"] = new_user.name
            flash("Account successfully created!")
            return redirect(url_for("general.index"))

    return render_template("signup.html", form=form)
