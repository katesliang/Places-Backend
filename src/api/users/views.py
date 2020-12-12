from flask import request
from flask_restx import Namespace, Resource, fields

from src.api.users.crud import (  # isort:skip
    get_all_users,
    get_user_by_email,
    get_user_by_session_token,
    get_user_by_update_token,
    verify_credentials,
    renew_session,
    create_user,
    update_user,
)

users_namespace = Namespace("users")


user = users_namespace.model(
    "User",
    {
        "id": fields.Integer(readOnly=True),
        # "username": fields.String(required=True),
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
    @users_namespace.marshal_with(user, as_list=True)
    def get(self):
        """Returns all users."""
        return get_all_users(), 200

    @users_namespace.expect(user_post, validate=True)
    @users_namespace.response(201, "<user_email> was added!")
    @users_namespace.response(400, "Sorry. That email already exists.")
    @users_namespace.response(400, "Request malformed.")
    def post(self):
        """Creates a new user."""
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        response_object = {}

        if None in [email, password]:
            response_object["message"] = "Request malformed."
            return response_object, 400

        user = get_user_by_email(email)
        if user:
            response_object["message"] = "Sorry. That email already exists."
            return response_object, 400

        create_user(email, password)

        response_object["message"] = f"User with email {email} was added!"
        return response_object, 201


class UserRegister(Resource):
    @users_namespace.response(400, "Invalid ID/PW.")
    @users_namespace.response(400, "User already exists.")
    def post(self):
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        response_object = {}

        if email is None or password is None:
            response_object["message"] = "Invalid ID/PW."
            return response_object, 400

        was_created, user = create_user(email, password)

        if not was_created:
            response_object["message"] = "User already exists."
            return response_object, 400

        return user.as_dict(), 200


class UserSession(Resource):
    @users_namespace.response(400, "Invalid Token.")
    def post(self):
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

        token_set = json.dumps(
            {
                "session_token": user.session_token,
                "session_expiration": str(user.session_expiration),
                "update_token": user.update_token,
            }
        )

        return token_set, 200


class UserLogin(Resource):
    @users_namespace.marshal_with(user, as_list=True)
    def post(self):
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        response_object = {}

        if email is None or password is None:
            response_object["message"] = "Request malformed."
            return response_object, 400

        was_successful, user = verify_credentials(email, password)

        if not was_successful:
            response_object["message"] = "Invalid credentials."
            return response_object, 400

        return json.dumps(
            {
                "session_token": user.session_token,
                "session_expiration": str(user.session_expiration),
                "update_token": user.update_token,
            }
        )


users_namespace.add_resource(Users, "")
users_namespace.add_resource(UserLogin, "/login")
users_namespace.add_resource(UserRegister, "/register")
users_namespace.add_resource(UserSession, "/session")
