from typing import TypedDict
from dotenv import load_dotenv
from pathlib import Path
import csv
import json
import os
import requests


class Pole(TypedDict):
    structnum: str
    lat: float
    lon: float


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("API_KEY")


def parse_csv(file_path: str) -> list[Pole]:
    poles: list[Pole] = []
    with open(file_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            pole_no: Pole = {
                "structnum": row["structnum"].strip(),
                "lat": float(row["lat"].strip()),
                "lon": float(row["lon"].strip()),
            }
            poles.append(pole_no)
    return poles


# https://api.mapbox.com/search/searchbox/v1/reverse?longitude={longitude}&latitude={latitude}
"""
def searchbox():
    base_url = "https://api.mapbox.com/search/searchbox/v1/reverse?longitude=-92.316870&latitude=34.727450"
    params: dict[str, str] = {"types": "street", "access_token": api_key}

    response = requests.get(base_url, params=params)
    print(json.dumps(response.json()))
"""

# https://api.mapbox.com/v4/{tileset_id}/tilequery/{lon},{lat}.json
"""
def tilequery():
    base_url: str = "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/-92.316870,34.727450.json"
    params: dict[str, str | int] = {
        "radius": 500,
        "limit": 10,
        "types": "street",
        "layers": "road",
        "access_token": api_key
    }

    response = requests.get(base_url, params=params)
    print(json.dumps(response.json()))
"""


# https://api.mapbox.com/search/geocode/v6/reverse?longitude={longitude}&latitude={latitude}
"""
def geocodev6():
    base_url: str = "https://api.mapbox.com/search/geocode/v6/reverse?longitude=-92.316870&latitude=34.727450"
    params: dict[str, str] = {"types": "street", "access_token": api_key}
    response = requests.get(base_url, params=params)
    print(json.dumps(response.json()))
"""


# https://api.mapbox.com/matching/v5/{profile}/{coordinates}.json
def mapmatch():
    base_url: str = (
        "https://api.mapbox.com/matching/v5/mapbox/driving/-92.316870,34.727450;-92.316870,34.727450.json"
    )
    params: dict[str, str] = {"access_token": api_key}
    response = requests.get(base_url, params=params)
    print(response.status_code)
    print(json.dumps(response.json()))


if __name__ == "__main__":
    mapmatch()
