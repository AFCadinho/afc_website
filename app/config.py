import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("MY_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    TEMPLATES_AUTO_RELOAD = True
    PERMANENT_SESSION_LIFETIME = 30
