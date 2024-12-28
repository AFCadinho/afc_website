from app.models import Users

def fetch_used_names():
    users = Users.query.all()
    return [user.name for user in users]


def fetch_banned_users_names():
    users = Users.query.filter_by(is_banned=True).all()
    return [user.name for user in users]


def check_if_banned(name):
    user = Users.query.filter(Users.name.ilike(name)).first()
    if user:
        return user.is_banned
    return False

