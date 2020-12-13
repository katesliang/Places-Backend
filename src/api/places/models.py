import os
from geoalchemy2 import Geography
from src import db

DEFAULT_IMG = "https://cornell-places-assets.s3.amazonaws.com/cornell_img.jpg"


class Place(db.Model):

    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    coords = db.Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    types = db.Column(db.VARCHAR(255), nullable=False)
    image_url = db.Column(db.String, default=DEFAULT_IMG)

    def __init__(self, lat, lon, name, types, image_url=DEFAULT_IMG):
        self.coords = f"POINT({lat} {lon})"
        self.name = name
        self.types = types
        self.lat = lat
        self.lon = lon
        self.image_url = image_url

    def serialize(self):
        return {
            "name": self.name,
            "latitude": self.lat,
            "longitude": self.lon,
            "types": self.types,
            "img_url": self.image_url,
        }


if os.getenv("FLASK_ENV") == "development":
    from src import admin
    from src.api.places.admin import PlacesAdminView

    admin.add_view(PlacesAdminView(Place, db.session))
