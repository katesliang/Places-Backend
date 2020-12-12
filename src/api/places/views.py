from flask import request
from flask_restx import Namespace, Resource, fields, reqparse


from src.api.places.crud import (  # isort:skip
    get_all_places,
    get_place_by_id,
    get_place_by_name,
    add_place,
    update_place,
    delete_place,
    get_knearest_places,
    get_rating_by_id,
)

places_namespace = Namespace("places")


place = places_namespace.model(
    "Place",
    {
        "id": fields.Integer(readOnly=True),
        "name": fields.String(required=True),
        "types": fields.String(required=True),
        "lat": fields.Float(required=True),
        "lon": fields.Float(required=True),
        "image_url": fields.String(),
    },
)


class PlacesList(Resource):
    @places_namespace.marshal_with(place, as_list=True)
    def get(self):
        """Returns all places."""
        return get_all_places(), 200

    @places_namespace.expect(place, validate=True)
    @places_namespace.response(201, "<place_name> was added!")
    @places_namespace.response(400, "Sorry. That place already exists.")
    def post(self):
        """Creates a new place."""
        post_data = request.get_json()
        lon = post_data.get("lon")
        lat = post_data.get("lat")
        name = post_data.get("name")
        types = post_data.get("types")
        image_url = post_data.get("image_url")
        response_object = {}

        place = get_place_by_name(name)
        if place:
            response_object["message"] = "Sorry. That place already exists."
            return response_object, 400

        add_place(lat, lon, name, types, image_url)

        response_object["message"] = f"{name} was added!"
        return response_object, 201


class Places(Resource):
    @places_namespace.marshal_with(place)
    @places_namespace.response(200, "Success")
    @places_namespace.response(404, "Place <place_name> does not exist")
    def get(self, place_id):
        """Returns a single place."""
        place = get_place_by_id(place_id)
        if not place:
            places_namespace.abort(404, f"Place {place_id} does not exist")
        return place, 200

    @places_namespace.expect(place, validate=True)
    @places_namespace.response(200, "<place_id> was updated!")
    @places_namespace.response(400, "Sorry. That place already exists.")
    @places_namespace.response(404, "Place <place_id> does not exist")
    def put(self, place_id):
        """Updates a place."""
        post_data = request.get_json()
        lat = post_data.get("lat")
        lon = post_data.get("lon")
        name = post_data.get("name")
        types = post_data.get("types")
        image_url = post_data.get("image_url")
        response_object = {}

        place = get_place_by_id(place_id)
        if not place:
            places_namespace.abort(404, f"Place {place_id} does not exist")

        if get_place_by_name(name):
            response_object["message"] = "Sorry. That place already exists."
            return response_object, 400

        update_place(place, lat, lon, name, types, image_url)

        response_object["message"] = f"{place.id} was updated!"
        return response_object, 200

    @places_namespace.response(200, "<place_id> was removed!")
    @places_namespace.response(404, "Place <place_id> does not exist")
    def delete(self, place_id):
        """"Deletes a place."""
        response_object = {}
        place = get_place_by_id(place_id)

        if not place:
            places_namespace.abort(404, f"Place {place_id} does not exist")

        delete_place(place)

        response_object["message"] = f"{place.name} was removed!"
        return response_object, 200


class PlacesSearches(Resource):
    @places_namespace.marshal_with(place, as_list=True)
    def get(self, place_types):
        """Return nearby places of specific type."""
        parser = reqparse.RequestParser()
        parser.add_argument("lat", type=float, required=False)
        parser.add_argument("lon", type=float, required=False)
        parser.add_argument("m", type=int, required=False)
        parser.add_argument("k", type=int, required=False)
        args = parser.parse_args()
        lat = args.get("lat", 0)
        lon = args.get("lon", 0)
        m = args.get("m", -1)
        k = args.get("k", -1)
        if lat is None:
            lat = 0
        if lon is None:
            lon = 0
        if m is None:
            m = -1
        if k is None:
            k = -1
        # print(lat, lon, place_types, m, k)

        res = get_knearest_places(lat, lon, place_types, m, k)

        return res, 200


class PlaceRating(Resource):
    def get(self, place_id):
        """Returns average rating for given place id. 0 if there are no ratings."""
        place = get_place_by_id(place_id)

        if not place:
            places_namespace.abort(404, f"Place {place_id} does not exist")
        rating = get_rating_by_id(place_id)
        if rating is None:
            rating = 0
        return {"rating": int(rating)}, 200


places_namespace.add_resource(PlacesList, "")
places_namespace.add_resource(Places, "/<int:place_id>")
places_namespace.add_resource(PlacesSearches, "/<string:place_types>")
places_namespace.add_resource(PlaceRating, "/rating/<int:place_id>")
