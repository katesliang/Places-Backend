from db import db
from db import User, Place, Review
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
    name = body.get("name")
    email= body.get("email")
    password= body.get("password")
    if name is None or email is None or password is None:
        return failure_response("Invalid name, email, and/or password")    
    was_created, user = users_dao.create_user(name, email, password)
    if was_created is None:
        return failure_response("User already exists")
    db.session.commit()
    return success_response(user.serialize_session(), 201)
    
def calculate_average_rating(place_id):
    place = Place.query.filter_by(id = place_id).first()
    if place is None:
        return failure_response("Place not found")
    sum = 0
    for review in place.reviews:
        sum += review.rating
    try:
        average_rating = sum / len(place.reviews)
    except Exception as e:
        average_rating = 0
    return average_rating

@app.route('/user/update/', methods=['POST'])
def update_user():
    authenticated, user = check_if_logged_in()
    if not authenticated:
        return failure_response("Invalid user or session token")
    body = json.loads(request.data)
    email= body.get("email", user.email)
    password= body.get("password", user.password) 
    user.email = email
    user.password = password
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route('/user/info/')
def get_user():
    authenticated, user = check_if_logged_in()
    if not authenticated:
        return failure_response("Invalid user or session token")
    return success_response(user.serialize())

@app.route('/authenticated/')
def is_authenticated():
    if not check_if_logged_in():
        return failure_response("Not authenticated")
    return success_response("User is logged in")

@app.route('/places/<int:place_id>/review/', methods=['POST'])
def create_review(place_id):
    authenticated, user = check_if_logged_in()
    if not authenticated:
        return failure_response("Not authenticated")
    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return failure_response("Place not found")
    body = json.loads(request.data)
    text = body.get("text")
    rating = body.get("rating") 
    if text is None or rating is None:
        return failure_response("Invalid text or rating")
    new_review= Review(
        text=body.get("text"),
        rating = body.get("rating"),
        place_id = place_id, 
        user_id = user.id
    )
    db.session.add(new_review)
    db.session.commit()
    place.average_rating = calculate_average_rating(place_id)
    db.session.commit()
    return success_response(new_review.serialize(), 201)

@app.route("/places/<int:place_id>/add/", methods=["POST"])
def add_place_to_saved(place_id):
    was_successful, session_token = extract_token(request)
    user = users_dao.get_user_by_session_token(session_token)
    if user is None:
        return failure_response("User must be logged in")
    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return failure_response("Place not found")
    user.places.append(place)
    db.session.commit()
    return success_response(user.serialize())

@app.route('/users/<int:user_id>/', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

@app.route('/places/')
def get_all_places(): # sort by most favorited/least favorited, highest/lowest rating
    return success_response([p.serialize() for p in Place.query.all()])

@app.route('/places/<int:place_id>/')
def get_place(place_id):
    place = Place.query.filter_by(id = place_id).first()
    if place is None:
        return failure_response("Place not found")
    return success_response(place.serialize())

@app.route('/places/', methods=['POST'])
def add_place():
    body = json.loads(request.data)
    name = body.get("name")
    if name is None:
        return failure_response("Missing name")
    description = body.get("description", "")
    latitude = body.get("latitude")
    longitude = body.get("longitude")
    if latitude is None or longitude is None:
        return failure_response("Invalid longitude and/or latitude")
    category = body.get("category")
    if category != "study space" and category != "bathroom" and category != "vending machine" and category != "atm":
        return failure_response("Invalid category")
    new_place = Place(name=name, average_rating = 0, description=description, category=category, latitude=latitude, longitude=longitude)
    db.session.add(new_place)
    db.session.commit()
    return success_response(new_place.serialize(), 201)

@app.route('/places/<int:place_id>/', methods=['POST'])
def update_place(place_id):
    body = json.loads(request.data)
    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return failure_response("Invalid place")
    place.name = body.get("name", place.name)
    place.description = body.get("description", place.description)
    db.session.commit()
    return success_response(place.serialize())

@app.route('/places/<int:place_id>/', methods=['DELETE'])
def delete_place(place_id):
    place = Place.query.filter_by(id=place_id).first()
    if place is None:
        return failure_response("Place not found")
    db.session.delete(place)
    db.session.commit()
    return success_response(place.serialize())

@app.route('/saved/')
def get_saved_places():
    was_successful, session_token = extract_token(request)
    if not was_successful: 
        return session_token
    user = users_dao.get_user_by_session_token(session_token)
    if user is None:
        return failure_response("Invalid session token")
    return success_response([p.serialize() for p in user.places])

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

def check_if_logged_in():
    was_successful, session_token = extract_token(request)
    if not was_successful:
        return False, failure_response("Invalid authorization header")
    user = users_dao.get_user_by_session_token(session_token)
    if user is None:
        return False, failure_response("Invalid session token")
    return True, user

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
