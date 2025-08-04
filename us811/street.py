from helpers import Pole
from typing import TypedDict
import requests


class Metadata(TypedDict):
    street_name: str
    osm_id: int
    county: str
    city: str


def reverse_geocode(gps: list[Pole]) -> list[Metadata]:
    base_url = "https://nominatim.openstreetmap.org/reverse"
    url_list = []
    #TODO params loop then add to url list
    #params = {"lat": gps["lat"], "lon": gps["lon"], "format": "json"}
    headers = {"User-Agent": "us811/v1"}

    response = requests.get(base_url, params=params, headers=headers)
    json = response.json()

    pole_metadata: Metadata = {
        "osm_id": int(json["osm_id"]),
        "county": json["address"]["county"],
        "street_name": json["address"]["road"],
        "city": json["address"]["municipality"],
    }
    return pole_metadata
