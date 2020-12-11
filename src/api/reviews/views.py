from flask import request
from flask_restx import Namespace, Resource, fields, reqparse

from src.api.reviews.crud import (
    get_all_reviews,
    get_review_by_id,
    get_reviews_by_place,
    get_reviews_by_user,
    get_reviews_composite,
    add_review,
    update_review,
    delete_review,
)

reviews_namespace = Namespace("reviews")

review = reviews_namespace.model(
    "Review",
    {
        "id": fields.Integer(readOnly=True),
        "user_id": fields.Integer(required=True),
        "place_id": fields.Integer(required=True),
        "rating": fields.Integer(required=True),
        "text": fields.String(required=True),
        "created_date": fields.DateTime,
    },
)


class ReviewsList(Resource):
    @reviews_namespace.marshal_with(review, as_list=True)
    def get(self):
        """Return query result on reviews based on place/user id"""
        parser = reqparse.RequestParser()
        parser.add_argument("user", type=int, required=False)
        parser.add_argument("place", type=int, required=False)
        args = parser.parse_args()
        user_id = args.get("user")
        place_id = args.get("place")
        if user_id is None and place_id is None:
            reviews = get_all_reviews()
        elif user_id is None:
            reviews = get_reviews_by_place(place_id)
        elif place_id is None:
            print(user_id)
            reviews = get_reviews_by_user(user_id)
        else:
            reviews = get_reviews_composite(user_id=user_id, place_id=place_id)
        return (reviews, [])[reviews is None]

    @reviews_namespace.response(200, "Review updated successfully!")
    @reviews_namespace.response(400, "Request body malformed.")
    @reviews_namespace.response(400, "Invalid rating value.")
    def post(self):
        """Creates a new review."""
        post_data = request.get_json()
        user_id = post_data.get("user_id")
        place_id = post_data.get("place_id")
        rating = post_data.get("rating")
        text = post_data.get("text")
        response_object = {}
        if None in [user_id, place_id, rating, text]:
            response_object["message"] = "Request body malformed."
            return response_object, 400
        elif (type(rating) != int) or not (0 <= rating <= 5):
            response_object["message"] = "Request body malformed."
            return response_object, 400
        else:
            add_review(user_id, place_id, rating, text)
            response_object["message"] = "Review posted successfully!"
            return response_object, 201


class Reviews(Resource):
    @reviews_namespace.marshal_with(review)
    @reviews_namespace.response(200, "Success")
    @reviews_namespace.response(404, "Review <review_id> does not exist")
    def get(self, review_id):
        """Returns a single review."""
        review = get_review_by_id(review_id)
        if review is None:
            reviews_namespace.abort(404, f"Review {review_id} does not exist")
        return review, 200

    @reviews_namespace.expect(review, validate=True)
    @reviews_namespace.response(200, "Review updated successfully!")
    @reviews_namespace.response(404, "Review <review_id> does not exist.")
    def put(self, review_id):
        """Updates the star rating / text of a review."""
        post_data = request.get_json()
        rating = post_data.get("rating")
        text = post_data.get("text")
        response_object = {}

        review = get_review_by_id(review_id)
        if not review:
            reviews_namespace.abort(404, f"Review {review_id} does not exist.")

        update_review(review, rating, text)

        response_object["message"] = f"Review {review.id} was updated!"
        return response_object, 200

    @reviews_namespace.response(200, "<review_id> was removed successfully!")
    @reviews_namespace.response(404, "Review <review_id> does not exist.")
    def delete(self, review_id):
        """Deletes a review."""
        review = get_review_by_id(review_id)
        response_object = {}

        if not review:
            reviews_namespace.abort(404, f"Review {review_id} does not exist.")

        delete_review(review)
        response_object["message"] = f"Review {review.id} was deleted."
        return response_object, 200


reviews_namespace.add_resource(ReviewsList, "")
reviews_namespace.add_resource(Reviews, "/<int:review_id>")