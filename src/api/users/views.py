from flask import request
from flask_restx import Namespace, Resource, fields, marshal
import json

# from src.api.users.models import assoc_favorites
from src.api.places.crud import get_place_by_id
from src.api.users.crud import (  # isort:skip
    get_all_users,
    get_user_by_email,
    get_user_by_session_token,
    get_user_by_username,
    # get_user_by_update_token,
    verify_credentials,
    renew_session,
    create_user,
    # update_user,
    add_favorite,
    remove_favorite,
)

users_namespace = Namespace("users")

user_fields = {
    "id": fields.Integer,
    "email": fields.String,
    "username": fields.String,
    "created_date": fields.DateTime,
}

user = users_namespace.model(
    "User",
    {
        "id": fields.Integer(readOnly=True),
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "created_date": fields.DateTime,
    },
)

user_post = users_namespace.inherit(
    "User post", user, {"password": fields.String(required=True)}
)


def extract_token(request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, json.dumps({"error": "Missing authorization header"})

    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, json.dumps({"error": "invalid auth header"})

    return True, bearer_token


class Users(Resource):
    @users_namespace.expect(user)
    @users_namespace.response(400, "Unauthroized token.")
    def get(self):
        """Returns user based on session token."""
        was_successful, session_token = extract_token(request)
        response_object = {}
        if not was_successful:
            response_object["message"] = session_token
            return response_object, 400
        request_user = get_user_by_session_token(session_token)
        if request_user is None:
            response_object["message"] = "Unauthorized user."
            return response_object, 400
        return marshal(request_user, user_fields), 200

    @users_namespace.expect(user_post, validate=True)
    @users_namespace.response(201, "<user_email> was added!")
    @users_namespace.response(400, "Sorry. That email already exists.")
    @users_namespace.response(400, "Request malformed.")
    def post(self):
        """Creates a new user."""
        post_data = request.get_json()
        email = post_data.get("email")
        username = post_data.get("username")
        password = post_data.get("password")
        response_object = {}

        if None in [email, password, username]:
            response_object["message"] = "Request malformed."
            return response_object, 400

        user = get_user_by_email(email)
        user_username = get_user_by_username(username)
        if user is not None:
            response_object["message"] = "Sorry. That email already exists."
            return response_object, 400
        elif user_username is not None:
            response_object["message"] = "Sorry. That username already exists."
            return response_object, 400

        create_user(email, username, password)

        response_object["message"] = f"User with email {email} was added!"
        return response_object, 201


class UsersAll(Resource):
    @users_namespace.expect(user)
    @users_namespace.response(400, "Unauthroized token.")
    def get(self):
        """Returns all users."""
        was_successful, session_token = extract_token(request)
        response_object = {}
        if not was_successful:
            response_object["message"] = session_token
            return response_object, 400
        request_user = get_user_by_session_token(session_token)
        if request_user is None:
            response_object["message"] = "Unauthorized user."
            return response_object, 400
        users = get_all_users()
        # return marshal(users, user_fields), 200
        return list(map(lambda x: x.as_dict(), users)), 200


class UserRegister(Resource):
    @users_namespace.response(400, "Invalid ID/PW.")
    @users_namespace.response(400, "User already exists.")
    def post(self):
        "Registers a user with email, username and password"
        post_data = request.get_json()
        email = post_data.get("email")
        username = post_data.get("username")
        password = post_data.get("password")
        response_object = {}

        if None in [email, username, password]:
            response_object["message"] = "Supply email, username and password."
            return response_object, 400

        was_created, user = create_user(email, username, password)

        if not was_created:
            response_object["message"] = "User already exists."
            return response_object, 400

        return user.as_dict(), 201


class UserSession(Resource):
    @users_namespace.response(400, "Invalid Token.")
    def post(self):
        """Renvews user session token given the update token"""
        was_successful, update_token = extract_token(request)
        response_object = {}

        if not was_successful:
            response_object["message"] = "Invalid Token."
            return response_object, 400

        try:
            user = renew_session(update_token)
        except Exception as e:
            response_object["message"] = f"{str(e)}"
            return response_object, 400

        token_set = {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        }

        return token_set, 201


class UserLogin(Resource):
    def post(self):
        """Sign in with email and password"""
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        response_object = {}

        if None in [email, password]:
            response_object["message"] = "Supply email, username and password."
            return response_object, 400

        was_successful, user = verify_credentials(email, password)

        if not was_successful:
            response_object["message"] = "Invalid credentials."
            return response_object, 400

        return {
            "user_id": user.id,
            "username": user.username,
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token,
        }, 201


class UserFavorites(Resource):
    @users_namespace.response(400, "Unauthroized token.")
    def post(self, place_id):
        """Adds place to user favorites."""
        was_successful, session_token = extract_token(request)
        response_object = {}
        if not was_successful:
            response_object["message"] = session_token
            return response_object, 400
        request_user = get_user_by_session_token(session_token)
        if request_user is None:
            response_object["message"] = "Unauthorized user."
            return response_object, 400
        place = get_place_by_id(place_id)
        if place is None:
            response_object["message"] = "Invalid place id."
            return response_object, 400
        # place_id and user is valid.
        add_favorite(request_user, place)
        response_object["message"] = "Added location as favorite!"
        return response_object, 201

    def delete(self, place_id):
        """Removes place from user favorites."""
        was_successful, session_token = extract_token(request)
        response_object = {}
        if not was_successful:
            response_object["message"] = session_token
            return response_object, 400
        request_user = get_user_by_session_token(session_token)
        if request_user is None:
            response_object["message"] = "Unauthorized user."
            return response_object, 400
        place = get_place_by_id(place_id)
        if place is None:
            response_object["message"] = "Invalid place id."
            return response_object, 400
        # place_id and user is valid.
        remove_favorite(request_user, place)
        response_object["message"] = "Removed location from favorite!"
        return response_object, 201


class UserFavoritesList(Resource):
    @users_namespace.response(400, "Unauthroized token.")
    def post(self):
        """Shows the list of user favorites given the session token."""
        was_successful, session_token = extract_token(request)
        response_object = {}
        if not was_successful:
            response_object["message"] = session_token
            return response_object, 400
        request_user = get_user_by_session_token(session_token)
        if request_user is None:
            response_object["message"] = "Unauthorized user."
            return response_object, 400

        data = []
        for pl in request_user.favorites:
            data.append(pl.serialize())
        return data, 200


users_namespace.add_resource(Users, "")
users_namespace.add_resource(UsersAll, "/all")
users_namespace.add_resource(UserLogin, "/login")
users_namespace.add_resource(UserRegister, "/register")
users_namespace.add_resource(UserSession, "/session")
users_namespace.add_resource(UserFavorites, "/favorites/<int:place_id>")
users_namespace.add_resource(UserFavoritesList, "/favorites")
