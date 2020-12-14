import os

from sqlalchemy.sql import func

from src import db


class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey("places.id"), nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=True)

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.place_id = kwargs.get("place_id")
        self.rating = kwargs.get("rating")
        self.text = kwargs.get("text")


if os.getenv("FLASK_ENV") == "development":
    from src import admin
    from src.api.reviews.admin import ReviewsAdminView

    admin.add_view(ReviewsAdminView(Review, db.session))
