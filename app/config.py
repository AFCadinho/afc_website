import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("MY_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    TEMPLATES_AUTO_RELOAD = True
    PERMANENT_SESSION_LIFETIME = 30

    IS_LOCAL = os.getenv("FLASK_ENV", "production") == "development"

    # Separate Patreon clients for local vs production
    PATREON_CLIENT_ID = (
    os.getenv("PATREON_CLIENT_ID_DEV") if IS_LOCAL else os.getenv("PATREON_CLIENT_ID")
    )
    PATREON_CLIENT_SECRET = (
        os.getenv("PATREON_CLIENT_SECRET_DEV") if IS_LOCAL else os.getenv("PATREON_CLIENT_SECRET")
    )

    PATREON_REFRESH_TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
    PATREON_CAMPAIGN_ID = os.getenv("PATREON_CAMPAIGN_ID")

    # Redirect URI changes for local vs production
    PATREON_REDIRECT_URI = (
        "https://2ffe-2a02-a449-8136-0-e868-490-b284-df99.ngrok-free.app/oauth/callback"
        if IS_LOCAL
        else "https://afcadinho.com/oauth/callback"
    )
