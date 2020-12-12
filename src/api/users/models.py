import os

from sqlalchemy.sql import func

from src import db

import bcrypt
import hashlib
import datetime
import src.api.places.models as places

# places.Place

# assoc_favorites = db.Table(
#     "assoc_favorites",
#     db.Model.metadata,
#     db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
#     db.Column("place_id", db.Integer, db.ForeignKey("places.id"), primary_key=True),
# )

assoc_favorites = db.Table(
    "assoc_favorites",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("place_id", db.Integer, db.ForeignKey("places.id"), primary_key=True),
)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), nullable=False)
    password_digest = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    favorites = db.relationship(
        "Place",
        secondary=assoc_favorites,
        # lazy="dynamic",
        # backref=db.backref("users", lazy=True),
        backref="users",
    )
    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.email = kwargs.get("email")
        self.password_digest = bcrypt.hashpw(
            kwargs.get("password").encode("utf-8"), bcrypt.gensalt(rounds=13)
        ).decode("utf-8")
        self.renew_session()

    # Used to randomly generate session/update tokens
    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    # Generates new tokens, and resets expiration time
    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        print(password.encode("utf-8"), self.password_digest.encode("utf-8"))
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_digest.encode("utf-8")
        )

    # Checks if session token is valid and hasn't expired
    def verify_session_token(self, session_token):
        return (
            session_token == self.session_token
            and datetime.datetime.now() < self.session_expiration
        )

    def verify_update_token(self, update_token):
        return update_token == self.update_token

    def as_dict(self):
        return {
            "email": self.email,
            "session_token": self.session_token,
            "update_token": self.update_token,
            "favorites": list(map(lambda x: x.id, self.favorites)),
        }


if os.getenv("FLASK_ENV") == "development":
    from src import admin
    from src.api.users.admin import UsersAdminView

    admin.add_view(UsersAdminView(User, db.session))
