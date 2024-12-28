from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
import requests

bp = Blueprint("patreon", __name__)

@bp.route("/oauth/callback")
def patreon_callback():
    code = request.args.get("code")
    if not code:
        flash("Authorization failed.")
        return redirect(url_for("index"))

    data = {
        "client_id": current_app.config["PATREON_CLIENT_ID"],
        "client_secret": current_app.config["PATREON_CLIENT_SECRET"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": current_app.config["PATREON_REDIRECT_URI"],
    }

    token_response = requests.post(
        current_app.config["PATREON_REFRESH_TOKEN_URL"], data=data
    )

    if token_response.status_code == 200:
        session["patreon_token"] = token_response.json().get("access_token")
        flash("Patreon account linked successfully!")
    else:
        flash("Failed to link Patreon account.")

    return redirect(url_for("profile.view_profile"))


@bp.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@bp.route("/terms-of-service")
def terms_of_service():
    return render_template("terms_of_service.html")
