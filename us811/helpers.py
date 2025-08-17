import csv
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any, TypedDict

import requests
from dotenv import load_dotenv


class Pole(TypedDict):
    struct: str
    lon: float
    lat: float
    dig_st: str
    int_st: str
    verbiage: str


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


def tilequery(pole: Pole) -> Pole:
    """
    Args:
    Returns:
    Raises:
    """
    base_url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{pole['lon']},{pole['lat']}.json"
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
    data = response.json()
    print(data)
    # TODO: get the appropriate values from the response value - handle edge cases
    # TODO: Make a separate function that accepts a python dic containing the response, then extract the needed values
    print(json.dumps(data))

    # TODO: return a Pole


if __name__ == "__main__":
    test = parse_csv("../tests/unit/test_data.csv")
    print(test)
