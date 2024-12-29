from flask import Blueprint, redirect, session, url_for, flash, request
from app import db
from app.models import Users, PatreonToken
from app.config import Config
from datetime import datetime, timedelta, UTC

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
    # Receive code from patreon after redirect
    code = request.args.get("code")
    if not code:
        flash("Authorization failed", "danger")
        return redirect(url_for("profile.view_profile", user_id=session.get("user_id")))

    # Build up request for token
    token_url = "https://www.patreon.com/api/oauth2/token"
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": Config.PATREON_CLIENT_ID,
        "client_secret": Config.PATREON_CLIENT_SECRET,
        "redirect_uri": Config.PATREON_REDIRECT_URI
    }
    response = requests.post(token_url, data=data)
    tokens = response.json()
    expires_in = tokens["expires_in"]
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)


    # Stores variables in database
    user = Users.query.filter_by(id=session["user_id"]).first()
    if user:
        user.is_patreon_linked = True # Mark Patreon as linked
        user.patreon_user_id = fetch_patreon_id(tokens["access_token"])

    new_patreon_token = PatreonToken(
        user_id = user.id,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_at=expires_at
    )
    db.session.add(new_patreon_token)
    db.session.commit()
    
    # Implement: Check if a user is a paid member.
    if check_if_paid_user(user.id):
        user.is_patreon = True
        db.session.commit()


    flash("Patreon account linked successfully!", "success")
    return redirect(url_for("profile.view_profile", user_id=user.id))


@bp.route("/patreon/<int:user_id>/disconnect")
def patreon_disconnect(user_id):
    user = Users.query.filter_by(id=user_id).first()
    patreon_token = PatreonToken.query.filter_by(user_id=user_id).first()
    if user and patreon_token:
        # Clear Patreon tokens and unlink the account

        user.patreon_user_id = None
        user.is_patreon = False
        user.is_patreon_linked = False
        db.session.delete(patreon_token)
        db.session.commit()
        flash("Your Patreon account has been disconnected.", "success")

    return redirect(url_for("profile.view_profile", user_id=user.id))


def check_if_paid_user(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return
    access_token = user.patreon_token.access_token
    
    campaign_id = fetch_patreon_campaign_id(access_token)

    paid_members = fetch_paid_patron_ids(access_token, campaign_id)

    patron_id = fetch_patreon_id(access_token)
    if not patron_id:
        return False

    if paid_members:
        if patron_id in paid_members:
            return True
    
    return False

def fetch_patreon_campaign_id(access_token):
    """Return Patreon campaign ID"""
    url = "https://www.patreon.com/api/oauth2/v2/campaigns"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
    }

    response = requests.get(url=url, headers=headers, params=params)
    campaign_data = response.json()

    return campaign_data["data"][0]["id"] # campaign ID


def fetch_paid_patron_ids(access_token, campaign_id):
    url = f"""https://www.patreon.com/api/oauth2/v2/campaigns/{
        campaign_id}/members"""
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "include": "user",
        "fields[member]": "patron_status",
        "page[count]": 100
    }

    paid_members_ids = set()
    cursor = None

    while True:
        if cursor:
            params["page[cursor]"] = cursor

        response = requests.get(url=url, headers=headers, params=params)
        campaign_data = response.json()

        members = campaign_data["data"]

        for member in members:
            status = member["attributes"]["patron_status"]
            if status == "active_patron":
                patron_id = member["relationships"]["user"]["data"]["id"]
                paid_members_ids.add(patron_id)

        cursor = campaign_data["meta"]["pagination"]["cursors"].get("Next")
        if not cursor:
            break

    return paid_members_ids


def fetch_patreon_id(access_token):
    """Return patreon user id"""

    url = "https://www.patreon.com/api/oauth2/v2/identity"
    params =  {
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers, params=params)
    user_data = response.json()
    return user_data["data"]["id"] # patreon_user_id