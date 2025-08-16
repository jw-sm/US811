import csv
import json
import os
from pathlib import Path
from typing import Any, TypedDict

import requests
from dotenv import load_dotenv


class Pole(TypedDict):
    structnum: str
    lat: float
    lon: float
    street: str
    intersection: str
    county: str
    verbiage: str


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("API_KEY")


def parse_csv(file_path: str) -> list[Pole]:
    poles: list[Pole] = []
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            pole_no: Pole = {
                "structnum": row["structnum"].strip(),
                "lat": float(row["lat"].strip()),
                "lon": float(row["lon"].strip()),
            }
            poles.append(pole_no)
    return poles


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
def tilequery(poles: list[Poles]) -> list[Poles]:
    base_url: str = "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/-92.311262,34.738984.json"
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
    print(json.dumps(data))
    return data


if __name__ == "__main__":
    data = parse_csv("../tests/unit/test_data.csv")
    print(data)
