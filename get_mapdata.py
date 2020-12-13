import requests

location_types = [
    "Blue",
    "AllGender",
    "Water",
    "TCAT",
    "Bikes",
    "Charging",
    "FoodServices",
    "Parkmobile",
]

img_urls = {
    "Blue": "https://cornell-places-assets.s3.amazonaws.com/bluelight.jpg",
    "AllGender": "https://cornell-places-assets.s3.amazonaws.com/all_gender.jpg",
    "Water": "https://cornell-places-assets.s3.amazonaws.com/water.jpg",
    "TCAT": "https://cornell-places-assets.s3.amazonaws.com/tcat.jpg",
    "Bikes": "https://cornell-places-assets.s3.amazonaws.com/bikes.jpg",
    "Charging": "https://cornell-places-assets.s3.amazonaws.com/charging.jpeg",
    "FoodServices": "https://cornell-places-assets.s3.amazonaws.com/food_service.jpg",
    "Parkmobile": "https://cornell-places-assets.s3.amazonaws.com/park_mobile.jpg",
}


def get_locationdata(ltype):
    url = f"https://www.cornell.edu/about/maps/overlay-items.cfm?layer={ltype}&clearCache=1"

    isvalid = False
    cnt = 0
    while isvalid is False and cnt < 3:
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
        except:
            cnt += 1
            isvalid = False
        else:
            isvalid = True

    req = r.json()
    dlist = req.get("items", [])
    res = []
    for data in dlist:
        ndata = dict()
        name = str(data.get("Name"))
        if name is not None:
            ndata["lat"] = data.get("Lat")
            ndata["lon"] = data.get("Lng")
            ndata["name"] = name
            ndata["types"] = ltype
            ndata["image_url"] = img_urls[ltype]
            res.append(ndata)
    return res


def get_mapdata():
    output = []
    for tp in location_types:
        output.extend(get_locationdata(tp))
    return output
