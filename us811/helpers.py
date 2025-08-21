import csv
import math
import os
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from normalize import normalize


@dataclass
class Pole:
    # -----------------------
    pole_number: str
    lon: float
    lat: float
    # -----------------------
    dig_lon: Optional[float] = None
    dig_lat: Optional[float] = None
    dig_street: Optional[str] = None
    # -----------------------
    inter_lon_point: Optional[float] = None
    inter_lat_point: Optional[float] = None
    # -----------------------
    inter_lon: Optional[float] = None
    inter_lon: Optional[float] = None
    intersection: Optional[str] = None
    int_to_dig: Optional[int] = None
    dig_to_pole: Optional[int] = None
    # -----------------------
    verbiage: Optional[str] = None


env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("API_KEY")


def parse_csv(file_path: str) -> list[Pole]:
    if not isinstance(file_path, str):
        raise TypeError(f"Expected str, got {type(file_path)}")

    poles: list[Pole] = []

    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            pole = Pole(
                pole_number=row["structnum"],
                lon=float(row["lon"]),
                lat=float(row["lat"]),
            )
            poles.append(pole)
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


def tilequery(pole: Pole) -> Pole:
    """
    Args:
        list of Poles from parse_csv
    Returns:
        enriched list of Poles
    Raises:
    """
    params: dict[str, str | Any] = {
        "radius": 1000,
        "limit": 10,
        "geometry": "linestring",
        "dedupe": False,
        "types": "street",
        "layers": "road",
        "access_token": api_key,
    }

    base_url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{pole.lon},{pole.lat}.json"

    response = requests.get(base_url, params=params)
    response_data = response.json()

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
    pole.dig_lon = result[0].get("geometry", {}).get("coordinates", [])[0]
    pole.dig_lat = result[0].get("geometry", {}).get("coordinates", [])[1]
    pole.dig_street = result[0].get("properties", {}).get("name").upper()
    pole.inter_lon_point = result[1].get("geometry", {}).get("coordinates", [])[0]
    pole.inter_lat_point = result[1].get("geometry", {}).get("coordinates", [])[1]

    return pole


# https://api.mapbox.com/directions/v5/{profile}/{coordinates}
def directions(pole: Pole) -> dict:
    base_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{pole.inter_lon_point},{pole.inter_lat_point};{pole.dig_lon},{pole.dig_lat}"

    params: dict[str, str | Any] = {"access_token": api_key, "steps": "true"}

    response = requests.get(base_url, params=params)
    response_data = response.json()

    # pole.int_to_dig = distance_from_inter_to_dig(response_data, pole.dig_street)

    # return pole
    return response_data


def distance_from_inter_to_dig(pole: Pole) -> Pole:
    response_data = directions(pole)
    route = response_data["routes"][0]
    legs = route["legs"]

    normalized_dig_st = normalize(pole.dig_street)

    for leg in legs:
        steps = leg["steps"]
        for i, step in reversed(list(enumerate(steps))):
            step_name = step.get("name", "")
            if (
                "maneuver" in step
                and step["maneuver"]["type"] == "turn"
                and normalize(step_name).lower() == normalized_dig_st.lower()
            ):
                prev = steps[i - 1]
                intersection = prev.get("name", "").upper()
                distance_meters = step["distance"]

                pole.intersection = intersection
                pole.int_to_dig = distance_meters * 3.28084
                breakpoint()
                return pole
    return Pole


def distance_feet(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance_meters = geodesic(point1, point2).meters
    distance_feet = distance_meters * 3.28084
    print(f"Distance: {math.trunc(distance_feet)} feet")
    return distance_feet


def get_screen_direction_detailed(lat1, lon1, lat2, lon2) -> str:
    """
    Args:
        lat1,lat2 = structnum gps
        lat2,lon2 = a point in dig street
    Return:
        Direction on which the structnum is located
        perpendicular to the point in dig street
    """
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    angle = math.degrees(math.atan2(delta_lon, delta_lat)) % 360  # 0°=N, 90°=E

    directions = [
        "NORTH",
        "NORTHEAST",
        "EAST",
        "SOUTHEAST",
        "SOUT",
        "SOUTHWEST",
        "WEST",
        "NORTHWEST",
    ]
    idx = round(angle / 45) % 8
    return directions[idx]


if __name__ == "__main__":
    poles = parse_csv("../tests/unit/test_data.csv")
    enriched_tile = [tilequery(p) for p in poles]
    with_distance = [distance_from_inter_to_dig(p) for p in poles]
