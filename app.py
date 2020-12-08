from db import db
from db import User
from datetime import datetime
from flask import Flask, request
import json 
import users_dao
import os

app = Flask(__name__)
db_filename = "places.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route('/users/')
def get_users():
    return success_response([u.serialize() for u in User.query.all()])

@app.route('/register/', methods=['POST'])
def create_user():
    body = json.loads(request.data)
    email= body.get("email")
    password= body.get("password")
    if email is None or password is None:
        return failure_response("Invalid email or password")    
    was_created, user = users_dao.create_user(email, password)
    if was_created is None:
        return failure_response("User already exists")
    db.session.commit()
    return success_response(user.serialize_session(), 201)

@app.route('/update/<int:user_id>/', methods=['POST'])
def update_user(user_id):
    body = json.loads(request.data)  
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("Invalid user")
    email= body.get("email", user.email)
    password= body.get("password", user.password) 
    user.email = email
    user.password = password
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route('/api/users/<int:user_id>/')
def get_user(user_id):
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())

@app.route('/users/<int:user_id>/', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

@app.route('/saved/')
def get_saved_places():
    was_successful, session_token = extract_token(request)
    if not was_successful: 
        return session_token
    user = users_dao.get_user_by_session_token(session_token)
    if user is None:
        return failure_response("Invalid session token")
    return success_response("places")

@app.route('/login/', methods=['POST'])
def login_user():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")
    if email is None or password is None:
        return failure_response("Invalid email or password")
    was_successful, user = users_dao.verify_credentials(email, password)
    if not was_successful:
        return failure_response("Incorrect email or password")
    return success_response(user.serialize_session())

@app.route("/session/", methods=["POST"])
def update_session():
    was_successful, update_token = extract_token(request)
    if not was_successful: 
        return update_token
    try:
        user = users_dao.renew_session(update_token)
    except Exception as e:
        return failure_response(f"Invalid update token: {str(update_token)}")
    return success_response(user.serialize_session())

def extract_token(request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, failure_response("Missing authorization header")
    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, failure_response("Invalid authorization header")
    return True, bearer_token

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
