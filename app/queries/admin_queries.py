from app.models import BannedNames

def fetch_banned_names():
    banned_names_obj = BannedNames.query.all()
    return [name.name for name in banned_names_obj]