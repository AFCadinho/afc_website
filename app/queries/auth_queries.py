from app.models import *

def fetch_used_names():
    users = Users.query.all()
    return [user.name for user in users]