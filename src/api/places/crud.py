# import json

from src import db
from src.api.places.models import Place
from sqlalchemy import func

# from geoalchemy2.shape import to_shape


def get_all_places():
    return Place.query.all()


def get_place_by_id(place_id):
    return Place.query.filter_by(id=place_id).first()


def get_place_by_name(place_name):
    # exact name search
    return Place.query.filter_by(name=place_name).first()


def add_place(lat, lon, name, types):
    place = Place(lat=lat, lon=lon, name=name, types=types)
    db.session.add(place)
    db.session.commit()
    return place


def update_place(place, lat, lon, name, types):
    place.coords = f"POINT({lon} {lat})"
    place.name = name
    place.types = types
    db.session.commit()
    return place


def delete_place(place):
    db.session.delete(place)
    db.session.commit()
    return place


def get_knearest_places(lat, lon, types, m=-1, k=5):
    if k < 0:
        k = 0
    if m <= 0:
        pllist = Place.query.filter_by(types=types).all()
        return pllist

    temp = Place(lat=lat, lon=lon, name="temp_place", types="temp_type")
    db.session.add(temp)
    db.session.commit()
    m = int(m)

    try:
        placesnearby = (
            Place.query.filter(
                func.ST_DistanceSphere(
                    func.ST_Point(Place.lat, Place.lon), func.ST_Point(lat, lon)
                )
                < m
            )
            .order_by(
                func.ST_DistanceSphere(
                    func.ST_Point(Place.lat, Place.lon), func.ST_Point(lat, lon)
                )
            )
            .limit(k)
        )

        res = []
        for temppl in placesnearby:
            if temppl != temp:
                res.append(temppl)
        # print(res)
    # except:
    except Exception as e:
        print("exception: ", e)

        db.session.delete(temp)
        db.session.commit()
    else:
        db.session.delete(temp)
        db.session.commit()

    return res
