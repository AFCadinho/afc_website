import sqlalchemy as sa
from sqlalchemy.sql import func
from app import db
from sqlalchemy.orm import relationship
from datetime import datetime, UTC, timedelta


# Junction Table
favorite_teams = sa.Table(
    "favorite_teams",
    db.metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("team_id", sa.Integer, sa.ForeignKey("teams.id"), primary_key=True)
)


# Models
class Users(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    password = sa.Column(sa.Text, nullable=False)
    email = sa.Column(sa.Text)
    is_admin = sa.Column(sa.Boolean, default=False)
    is_banned = sa.Column(sa.Boolean, default=False)
    is_patreon = sa.Column(sa.Boolean, default=False)
    is_patreon_linked = sa.Column(sa.Boolean, default=False)
    patreon_user_id = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())

    # Relationships
    comments = relationship("Comments", backref="users", cascade="all, delete-orphan")
    favorite_teams = relationship("Teams", secondary=favorite_teams, back_populates="favorited_by")
    patreon_token = relationship("PatreonToken", uselist=False, back_populates="user", cascade="all, delete-orphan")
    bans_received = relationship("Bans", foreign_keys="Bans.user_id", cascade="all, delete-orphan")
    bans_issued = relationship("Bans", foreign_keys="Bans.banned_by", cascade="all, delete-orphan")


class PatreonToken(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    access_token = sa.Column(sa.Text, nullable=False)
    refresh_token = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

    user = relationship("Users", back_populates="patreon_token")

    def is_expired(self):
        return datetime.now(UTC) > self.expires_at
    
    def refresh(self, new_access_token, new_refresh_token, expires_in):
        self.access_token = new_access_token
        self.refresh_token = new_refresh_token
        self.expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        db.session.commit()


class Bans(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    reason = sa.Column(sa.Text, nullable=False, server_default="Prohibited Action")
    banned_at = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=func.now())
    banned_by = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    updated_by = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    banned_user = relationship("Users", foreign_keys=[user_id], back_populates="bans_received")
    admin_user = relationship("Users", foreign_keys=[banned_by], back_populates="bans_issued")
    updater_user = relationship("Users", foreign_keys=[updated_by])

class Games(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    teams = relationship("Teams", backref="games", cascade="all, delete-orphan")

class Teams(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    game_id = sa.Column(sa.Integer, sa.ForeignKey("games.id"), nullable=False)
    name = sa.Column(sa.Text, nullable=False, unique=True)
    pokepaste = sa.Column(sa.Text, nullable=False, unique=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    archetype = sa.Column(sa.Text, nullable=False, server_default="Unknown")
    patreon_post = sa.Column(sa.Boolean, nullable=False, default=False)
    pokemon = relationship("Pokemon", back_populates="team", cascade="all, delete-orphan")
    comments = relationship("Comments", backref="team", cascade="all, delete-orphan")
    favorited_by = relationship("Users", secondary=favorite_teams, back_populates="favorite_teams")

class Pokemon(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    team_id = sa.Column(sa.Integer, sa.ForeignKey("teams.id"), nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    team = relationship("Teams", back_populates="pokemon")

class Comments(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    team_id = sa.Column(sa.Integer, sa.ForeignKey("teams.id"), nullable=False)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    comment = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())

class BannedNames(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, unique=True)
