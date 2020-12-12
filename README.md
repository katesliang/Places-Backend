# Places Backend

## Endpoints
/register/: register a user
/login/: login
/session/: renew session
/authenticated/: check if user is logged in
/user/info/: access user profile (must be logged in)
/user/info/ (DELETE): delete user profile (must be logged in)
/saved/: access saved places (must be logged in)
/user/update/: update user info (must be logged in)
/places/ (GET): get all places
/places/ (POST): add new place
/places/<int:place_id>/ (GET): get place by id
/places/<int:place_id>/ (POST): update place info
/places/<int:place_id>/ (DELETE): delete place
/places/<int:place_id>/review/ (POST): add review to place (must be logged in)
/places/<int:place_id>/add/ (POST): add place to user's saved (must be logged in)
