import requests
import random

# location_types = [
#     "Blue",
#     "AllGender",
#     "Water",
# ]

type_dict = {
    "Blue": "Blue Light",
    "AllGender": "Bathroom",
    "Water": "Water",
}


def get_img_url(ltype):
    img_idx = random.randint(0, 2)
    url_dict = {
        "Blue": f"https://cornell-places-assets.s3.amazonaws.com/bluelight{img_idx}.jpg",
        "AllGender": f"https://cornell-places-assets.s3.amazonaws.com/all_gender{img_idx}.jpg",
        "Water": f"https://cornell-places-assets.s3.amazonaws.com/water{img_idx}.jpg",
    }
    return url_dict[ltype]


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
        if (name is not None) and (ltype in type_dict):
            ndata["lat"] = data.get("Lat")
            ndata["lon"] = data.get("Lng")
            ndata["name"] = name
            ndata["types"] = type_dict[ltype]
            ndata["image_url"] = get_img_url(ltype)
            res.append(ndata)
    return res


def get_mapdata():
    output = []
    for tp in type_dict.keys():
        output.extend(get_locationdata(tp))
    return output
