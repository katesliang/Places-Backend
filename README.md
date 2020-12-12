# Places Backend

## Endpoints
/register/: register a user <br />
/login/: login <br />
/session/: renew session <br />
/authenticated/: check if user is logged in <br />
/user/info/ (GET): access user profile (must be logged in) <br />
/user/info/ (DELETE): delete user profile (must be logged in) <br />
/user/info/ (POST): update user info (must be logged in) <br />
/saved/: access saved places (must be logged in) <br />
/places/ (GET): get all places <br />
/places/ (POST): add new place <br />
/places/<int:place_id>/ (GET): get place by id <br />
/places/<int:place_id>/ (POST): update place info <br />
/places/<int:place_id>/ (DELETE): delete place <br />
/places/<int:place_id>/review/ (POST): add review to place (must be logged in) <br />
/places/<int:place_id>/add/ (POST): add place to user's saved (must be logged in) <br />
