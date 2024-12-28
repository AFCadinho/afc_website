import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("MY_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    TEMPLATES_AUTO_RELOAD = True
    PERMANENT_SESSION_LIFETIME = 30

    # Patreon OAuth Configuration
    PATREON_CLIENT_ID = os.getenv("PATREON_CLIENT_ID")
    PATREON_CLIENT_SECRET = os.getenv("PATREON_CLIENT_SECRET")
    PATREON_REDIRECT_URI = "https://afcadinho.com/oauth/callback"
    PATREON_REFRESH_TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
    PRIVACY_POLICY_URL = "https://afcadinho.com/privacy-policy"
    TERMS_OF_SERVICE_URL = "https://afcadinho.com/terms-of-service"
