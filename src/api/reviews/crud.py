from src import db
from src.api.reviews.models import Review


def get_all_reviews():
    return Review.query.all()


def get_review_by_id(review_id):
    return Review.query.filter_by(id=review_id).first()


def get_reviews_by_place(place_id):
    return Review.query.filter_by(place_id=place_id).all()


def get_reviews_by_user(user_id):
    return Review.query.filter_by(user_id=user_id).all()


def get_reviews_composite(user_id, place_id):
    return Review.query.filter_by(user_id=user_id, place_id=place_id).all()


def add_review(user_id, place_id, rating, text):
    review = Review(user_id=user_id, place_id=place_id, rating=rating, text=text)
    db.session.add(review)
    db.session.commit()
    return review


def update_review(review, rating, text):
    review.rating = rating
    review.text = text
    db.session.commit()
    return review


def delete_review(review):
    db.session.delete(review)
    db.session.commit()
    return review
