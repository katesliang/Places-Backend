from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import os
import bcrypt

db = SQLAlchemy()
association_table = db.Table(
    'association', 
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("place_id", db.Integer, db.ForeignKey("place.id"))
)

# your classes here
class Place(db.Model):
    __tablename__ = "place"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    users = db.relationship("User", secondary=association_table, back_populates='places')
    description = db.Column(db.String, nullable = False)
    average_rating = db.Column(db.Float, nullable = False)
    reviews = db.relationship("Review", cascade = "delete") 
    latitude = db.Column(db.Float, nullable = False)
    longitude = db.Column(db.Float, nullable = False)
    category = db.Column(db.String, nullable = False)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.average_rating = kwargs.get("average_rating")
        self.description = kwargs.get("description")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")
        self.category = kwargs.get("category")

    def serialize(self):
        return{
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "times saved": len(self.users), 
            "name": self.name, 
            "average rating": str(self.average_rating),
            "description": self.description, 
            "reviews": [r.serialize() for r in self.reviews]
        }
    def subserialize(self):
        return{ 
            "name": self.name
        }


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    places = db.relationship("Place", secondary=association_table, back_populates='users')
    reviews = db.relationship("Review", cascade = "delete")

    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        self.email = kwargs.get('email')
        self.name = kwargs.get('name')
        self.password = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.renew_session()

    def serialize(self):
        return{
            "name": self.name,
            "email": self.email,
            'saved_places': [p.subserialize() for p in self.places],
            "reviews_written": [r.serialize() for r in self.reviews]
        }
    
    def serialize_session(self):
        return {
            "session_token": self.session_token,
            "session_expiration": str(self.session_expiration),
            "update_token": self.update_token
        }      

    def _urlsafe_base_64(self):
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode("utf8"), self.password)

    def verify_session_token(self, session_token):
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        return update_token == self.update_token

class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, nullable = False)
    rating = db.Column(db.Float, nullable = False)
    place_id = db.Column(db.Integer, db.ForeignKey("place.id"), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)

    def __init__(self, **kwargs):
        self.text = kwargs.get('text')
        self.rating = kwargs.get('rating')
        self.place_id = kwargs.get("place_id")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        return{
            "author": User.query.filter_by(id=self.user_id).first().name,
            "text": self.text,
            "rating": self.rating
        }