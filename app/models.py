import sqlalchemy as sa
from sqlalchemy.sql import func
from app import db
from sqlalchemy.orm import relationship

class Users(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    password = sa.Column(sa.Text, nullable=False)
    is_admin = sa.Column(sa.Boolean, default=False)
    is_banned = sa.Column(sa.Boolean, default=False)
    comments = relationship("Comments", backref="users", cascade="all, delete-orphan")

class Games(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    teams = relationship("Teams", backref="games", cascade="all, delete-orphan")

class Teams(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    game_id = sa.Column(sa.Integer, sa.ForeignKey("games.id"), nullable=False)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    pokepaste = sa.Column(sa.Text, nullable=False, unique=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now())
    pokemon = relationship("Pokemon", backref="team", cascade="all, delete-orphan")
    comments = relationship("Comments", backref="team", cascade="all, delete-orphan")

class Pokemon(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    team_id = sa.Column(sa.Integer, sa.ForeignKey("teams.id"), nullable=False)
    name = sa.Column(sa.Text, nullable=False)

class Comments(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    team_id = sa.Column(sa.Integer, sa.ForeignKey("teams.id"), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    comment = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime, server_default=func.now())
