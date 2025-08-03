from helpers import Pole, parse_csv
from typing import TypedDict
import requests


class Metadata(TypedDict):
    street_name: str
    osm_id: int
    county: str
    city: str


"""
This will return a dictionary with the needed data for other usages 
Needed data:
street name
osm_id (to get the intersecition using the OVERPASS API)
county
name: city
"""


def reverse_geocode(gps: Pole) -> Metadata:
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": gps["lat"], "lon": gps["lon"], "format": "json"}
    headers = {"User-Agent": "us811/v1"}

    response = requests.get(base_url, params=params, headers=headers)
    json = response.json()
    print(json)

    pole_metadata: Metadata = {
        "osm_id": int(json["osm_id"]),
        "county": json["address"]["county"],
        "city": json["address"]["road"],
    }
    return pole_metadata


list_of_poles = parse_csv("../tests/test_data.csv")
response = reverse_geocode(list_of_poles[0])
print(response)
