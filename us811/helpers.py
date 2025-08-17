import csv
import json
import os
from itertools import islice
from pathlib import Path
from typing import Any, TypedDict

import requests
from dotenv import load_dotenv


class Pole(TypedDict):
    struct: str
    dig_lon: float
    dig_lat: float
    dig_street: str
    inter_lon: float
    inter_lat: float
    intersection: str


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("API_KEY")


def parse_csv(file_path: str) -> list[dict]:
    if not isinstance(file_path, str):
        raise TypeError(f"Expected str, got {type(file_path)}")

    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        result = list(reader)

    if not isinstance(result, list):
        raise TypeError(f"Expected to return list, got {type(result)}")

    return result


# Full solution:
# query tileset using the gps coordinate
# get the 2 first indices of feature[] list IF AND ONLY IF key "name" exists inside property dict/json.
# get the "name" key inside dict "property" for street names
# get the gps coordinates of the 2 indices
#    - geometry{[coordinates]}
# query the directions api using the 2 indices (lonlat origin; lotlat dest)
# get the first index of "routes",  -> "legs" -> "steps" ->
# check the "steps"{"name": "str"}
# if "steps" name != street name, get value of "name" and "distance"

# https://api.mapbox.com/v4/{tileset_id}/tilequery/{lon},{lat}.json


def tilequery(csv: dict) -> Pole:
    """
    Args:
    Returns:
    Raises:
    """
    base_url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{csv['lon']},{csv['lat']}.json"
    params: dict[str, str | Any] = {
        "radius": 500,
        "limit": 10,
        "geometry": "linestring",
        "dedupe": False,
        "types": "street",
        "layers": "road",
        "access_token": api_key,
    }
    response = requests.get(base_url, params=params)
    response_data = response.json()
    # print(json.dumps(response_data))

    seen_names = set()
    valid_streets = (
        item
        for item in response_data.get("features", [])
        if isinstance(item, dict)
        and (name := item.get("properties", {}).get("name"))
        and name not in seen_names
        and not seen_names.add(name)
    )
    result = list(islice(valid_streets, 2))

    return {
        "struct": csv["structnum"],
        "dig_lon": result[0].get("geometry", {}).get("coordinates", [])[0],
        "dig_lat": result[0].get("geometry", {}).get("coordinates", [])[1],
        "dig_street": result[0].get("properties", {}).get("name"),
        "inter_lon": result[1].get("geometry", {}).get("coordinates", [])[0],
        "inter_lat": result[1].get("geometry", {}).get("coordinates", [])[1],
        "intersection": result[1].get("properties", {}).get("name"),
    }


if __name__ == "__main__":
    test = parse_csv("../tests/unit/test_data.csv")
    first_pole = test[0]
    print(json.dumps(tilequery(first_pole)))
