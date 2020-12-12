import os
from geoalchemy2 import Geography
from src import db


class Place(db.Model):

    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    coords = db.Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    types = db.Column(db.VARCHAR(255), nullable=False)
    # user_favorites = db.relationship(
    #     "User",
    #     secondary=assoc_favorites,
    #     lazy="subquery",
    #     backref=db.backref("places", lazy=True),
    # )

    def __init__(self, lat, lon, name, types):
        self.coords = f"POINT({lat} {lon})"
        self.name = name
        self.types = types
        self.lat = lat
        self.lon = lon

    def serialize(self):
        return {
            "name": self.name,
            "latitude": self.lat,
            "longitude": self.lon,
            "types": self.types,
        }


if os.getenv("FLASK_ENV") == "development":
    from src import admin
    from src.api.places.admin import PlacesAdminView

    admin.add_view(PlacesAdminView(Place, db.session))
