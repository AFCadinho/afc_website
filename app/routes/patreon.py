from flask import Blueprint, redirect, session, url_for, flash, request
from app import db
from app.models import Users
from app.config import Config
import requests

bp = Blueprint('patreon', __name__)

@bp.route("/patreon/login")
def patreon_login():
    patreon_auth_url = (
        f"https://www.patreon.com/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={Config.PATREON_CLIENT_ID}"
        f"&redirect_uri={Config.PATREON_REDIRECT_URI}"
    )
    return redirect(patreon_auth_url)


@bp.route("/oauth/callback")
def patreon_callback():
    code = request.args.get("code")
    if not code:
        flash("Authorization failed", "danger")
        return redirect(url_for("profile.view_profile", user_id=session.get("user_id")))
    
    token_url = "https://www.patreon.com/api/oauth2/token"
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": Config.PATREON_CLIENT_ID,
        "client_secret": Config.PATREON_CLIENT_SECRET,
        "redirect_uri": Config.PATREON_REDIRECT_URI
    }
    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Save tokens and mark Patreon as linked
        user = Users.query.filter_by(id=session["user_id"]).first()
        if user:
            user.patreon_access_token = access_token
            user.patreon_refresh_token = refresh_token
            user.is_patreon_linked = True  # Mark Patreon as linked
            db.session.commit()

            # Check if user is a paying member right after linking
            check_patreon_membership(user)

        flash("Patreon account linked successfully!", "success")
        return redirect(url_for("profile.view_profile", user_id=user.id))
    
    flash("Failed to connect to Patreon", "danger")
    return redirect(url_for("profile.view_profile", user_id=session.get("user_id")))


def check_patreon_membership(user):
    if not user.patreon_access_token:
        flash("No Patreon access token found.", "danger")
        return None

    api_url = "https://www.patreon.com/api/oauth2/v2/identity?include=memberships.campaign&fields[member]=patron_status"
    headers = {
        "Authorization": f"Bearer {user.patreon_access_token}"
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        patreon_data = response.json()
        memberships = patreon_data.get("included", [])
        YOUR_CAMPAIGN_ID = Config.PATREON_CAMPAIGN_ID

        # Check if the user is an active member
        is_active_patron = False
        for member in memberships:
            campaign_data = member.get("relationships", {}).get("campaign", {}).get("data", {})
            patron_status = member.get("attributes", {}).get("patron_status", "none")
            
            if campaign_data.get("id") == YOUR_CAMPAIGN_ID and patron_status == "active_patron":
                is_active_patron = True
                break

        # Update both fields
        user.is_patreon = is_active_patron
        db.session.commit()

        if is_active_patron:
            flash("You are an active Patreon member!", "success")
        else:
            flash("You are not an active Patreon member.", "warning")

        return patreon_data
    else:
        flash("Failed to fetch Patreon data.", "danger")
        return None
    

@bp.route("/patreon/disconnect")
def patreon_disconnect():
    user = Users.query.filter_by(id=session.get("user_id")).first()
    if user:
        # Clear Patreon tokens and unlink the account
        user.patreon_access_token = None
        user.patreon_refresh_token = None
        user.patreon_user_id = None
        user.is_patreon = False
        user.is_patreon_linked = False
        db.session.commit()
        flash("Your Patreon account has been disconnected.", "success")
    
    return redirect(url_for("profile.view_profile", user_id=user.id))

