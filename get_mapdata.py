import requests

location_types = ["Blue", "AllGender", "Water", "TCAT", "Bikes", "Charging", "FoodServices", "Parkmobile"]


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
        ndata["lat"] = data.get("Lat")
        ndata["lon"] = data.get("Lng")
        ndata["name"] = str(data.get("Name"))
        if ndata["name"] == "None":
            ndata["name"] = ''
        ndata["types"] = ltype
        res.append(ndata)

    return res


def get_mapdata():
    output = []
    for tp in location_types:
        output.extend(get_locationdata(tp))
    return output
