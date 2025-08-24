import csv
import math
import os
import re
from dataclasses import dataclass
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
    intersection_lon: Optional[float] = None
    intersection_lat: Optional[float] = None
    intersection: Optional[str] = None
    int_to_dig: Optional[int] = None
    dig_to_pole: Optional[int] = None
    # -----------------------
    int_to_dig_dir: Optional[str] = None
    dig_to_pole_dir: Optional[str] = None
    verbiage: Optional[str] = None

    def __repr__(self):
        return (
            f"Pole(pole_number={self.pole_number!r}, lon={self.lon}, lat={self.lat}, "
            f"dig_lon={self.dig_lon}, dig_lat={self.dig_lat}, dig_street={self.dig_street!r}, "
            f"inter_lon_point={self.inter_lon_point}, inter_lat_point={self.inter_lat_point}, "
            f"intersection_lon={self.intersection_lon}, intersection_lat={self.intersection_lat}, "
            f"intersection={self.intersection!r}, int_to_dig={self.int_to_dig}, "
            f"dig_to_pole={self.dig_to_pole}, int_to_dig_dir={self.int_to_dig_dir!r}, "
            f"dig_to_pole_dir={self.dig_to_pole_dir!r}, verbiage={self.verbiage!r})"
        )


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
        pole: Pole object from parse_csv
    Returns:
        enriched Pole object with street information
    Raises:
    """
    params: dict[str, str | Any] = {
        "radius": 500,
        "limit": 15,
        "geometry": "linestring",
        "dedupe": False,
        "types": "street",
        "layers": "road",
        "access_token": api_key,
    }
    base_url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{pole.lon},{pole.lat}.json"
    response = requests.get(base_url, params=params)
    response_data = response.json()

    # Get all valid streets with names/refs
    valid_streets = []
    seen_names = set()

    all_features = response_data.get("features", [])
    print(f"Processing {len(all_features)} features from API")

    """
    # First, let's see all features for debugging
    for i, item in enumerate(all_features):
        if isinstance(item, dict):
            props = item.get("properties", {})
            street_class = props.get("class")
            name = props.get("name")
            ref = props.get("ref")
            feature_id = item.get("id")
            print(
                f"Feature {i} (id: {feature_id}): class='{street_class}', name='{name}', ref='{ref}'"
            )
    """

    # Priority order: streets with names, streets with refs, primary with names, primary with refs
    search_priorities = [
        ("street", "name"),
        ("street", "ref"),
        ("primary", "name"),
        ("primary", "ref"),
    ]

    for class_type, street_name in search_priorities:
        if len(valid_streets) >= 2:
            break

        print(f"Looking for {class_type} roads with {street_name}...")

        for i, item in enumerate(all_features):
            if (
                isinstance(item, dict)
                and item.get("properties", {}).get("class") == class_type
            ):
                properties = item.get("properties", {})
                identifier = properties.get(street_name)
                feature_id = item.get("id")
                if identifier:
                    print(
                        f"{class_type.title()} feature {i} (id: {feature_id}): {street_name}='{identifier}'"
                    )
                    if identifier not in seen_names:
                        seen_names.add(identifier)
                        valid_streets.append(item)
                        print(f"  ✓ Added as valid {class_type} #{len(valid_streets)}")
                        if len(valid_streets) >= 2:
                            print("  Stopping - found 2 roads")
                            break
                    else:
                        print(f"  ✗ Skipped (duplicate identifier: '{identifier}')")

        print(f"After {class_type}/{street_name}: {len(valid_streets)} roads found")

    print(f"Final count: {len(valid_streets)} valid streets")

    # Extract coordinates and names
    if len(valid_streets) >= 1:
        geometry = valid_streets[0].get("geometry", {})
        coords = geometry.get("coordinates")

        if coords and isinstance(coords, list) and len(coords) >= 2:
            pole.dig_lon = coords[0]
            pole.dig_lat = coords[1]
            print(f"Set dig coords: lon={pole.dig_lon}, lat={pole.dig_lat}")
        else:
            print(f"Invalid coordinates for first street: {coords}")

        properties = valid_streets[0].get("properties", {})
        street_name = properties.get("name") or properties.get("ref", "")
        pole.dig_street = normalize(street_name)
        print(f"Set dig_street: '{pole.dig_street}'")

    if len(valid_streets) >= 2:
        geometry = valid_streets[1].get("geometry", {})
        coords = geometry.get("coordinates")

        if coords and isinstance(coords, list) and len(coords) >= 2:
            pole.inter_lon_point = coords[0]
            pole.inter_lat_point = coords[1]
            print(
                f"Set inter coords: lon={pole.inter_lon_point}, lat={pole.inter_lat_point}"
            )
        else:
            print(f"Invalid coordinates for second street: {coords}")

        inter_properties = valid_streets[1].get("properties", {})
        inter_name = inter_properties.get("name") or inter_properties.get("ref", "")
        pole.intersection = normalize(inter_name)
        print(f"Set intersection: '{pole.intersection}'")

    return pole


# https://api.mapbox.com/directions/v5/{profile}/{coordinates}
def directions(pole: Pole) -> dict:
    base_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{pole.inter_lon_point},{pole.inter_lat_point};{pole.dig_lon},{pole.dig_lat}"
    params: dict[str, str | Any] = {"access_token": api_key, "steps": "true"}

    response = requests.get(base_url, params=params)
    response_data = response.json()

    return response_data


def distance_from_inter_to_dig(pole: Pole) -> Pole:
    response_data = directions(pole)
    route = response_data["routes"][0]
    legs = route["legs"]
    print(f"Looking for dig_street: '{pole.dig_street}'")

    for leg in legs:
        steps = leg["steps"]
        print(f"Found {len(steps)} steps in directions")

        for i, step in enumerate(steps):
            # Get both name and ref, similar to the street finding logic
            step_name = step.get("name", "")
            step_ref = step.get("ref", "")

            # Use name or ref, prioritizing name if available
            step_identifier = step_name or step_ref
            normalized_step_identifier = normalize(step_identifier)

            print(
                f"  Step {i}: name='{step_name}', ref='{step_ref}', using='{step_identifier}', normalized='{normalized_step_identifier}'"
            )

            # Try multiple matching strategies
            is_match = False

            # Strategy 1: Exact match
            if normalized_step_identifier == pole.dig_street:
                print(f"  ✓ EXACT MATCH at step {i}")
                is_match = True

            # Strategy 2: Check if dig_street is contained in step identifier
            elif pole.dig_street in normalized_step_identifier:
                print(
                    f"  ✓ CONTAINS MATCH at step {i} ('{pole.dig_street}' in '{normalized_step_identifier}')"
                )
                is_match = True

            # Strategy 3: Check if step identifier is contained in dig_street
            elif normalized_step_identifier in pole.dig_street:
                print(
                    f"  ✓ REVERSE CONTAINS MATCH at step {i} ('{normalized_step_identifier}' in '{pole.dig_street}')"
                )
                is_match = True

            # Strategy 4: For ref codes like E0960, try matching the number part
            elif re.match(r"[NSEW]\d+", pole.dig_street):
                # Extract direction and number from dig_street (e.g., "E0960" -> "E", "0960")
                dig_match = re.match(r"([NSEW])(\d+)", pole.dig_street)
                if dig_match:
                    dig_dir, dig_num = dig_match.groups()
                    # Look for the number in the step identifier
                    if (
                        dig_num.lstrip("0") in normalized_step_identifier
                        or dig_num in normalized_step_identifier
                    ):
                        # Also check if direction matches (E->EAST, W->WEST, etc.)
                        direction_map = {
                            "E": "EAST",
                            "W": "WEST",
                            "N": "NORTH",
                            "S": "SOUTH",
                        }
                        full_direction = direction_map.get(dig_dir, dig_dir)
                        if (
                            full_direction in normalized_step_identifier
                            or dig_dir in normalized_step_identifier
                        ):
                            print(
                                f"  ✓ REF CODE MATCH at step {i} (direction: {dig_dir}/{full_direction}, number: {dig_num})"
                            )
                            is_match = True

            if is_match:
                # Calculate basic distances
                pole.dig_to_pole = distance_feet(
                    pole.lat, pole.lon, pole.dig_lat, pole.dig_lon
                )

                # Try to find intersection info from previous step
                if i > 0:
                    prev = steps[i - 1]
                    # Check both name and ref for intersection too
                    prev_name = prev.get("name", "")
                    prev_ref = prev.get("ref", "")
                    intersection = (prev_name or prev_ref).upper()
                    if intersection:
                        pole.intersection = intersection
                        print(f"  Set intersection to: '{intersection}'")

                # Use step's coordinates if available
                if "intersections" in step and step["intersections"]:
                    intersection_coords = step["intersections"][0]["location"]
                    pole.intersection_lon = intersection_coords[0]
                    pole.intersection_lat = intersection_coords[1]
                    print(f"  Set intersection coords: {intersection_coords}")

                # Calculate distance from step info
                distance_meters = step.get("distance", 0)
                pole.int_to_dig = math.trunc(distance_meters * 3.28084)
                print(f"  Set int_to_dig: {pole.int_to_dig} ft")

                # Calculate directions
                pole.dig_to_pole_dir = get_direction(
                    pole.dig_lat, pole.dig_lon, pole.lat, pole.lon
                )
                if pole.intersection_lat and pole.intersection_lon:
                    pole.int_to_dig_dir = get_direction(
                        pole.intersection_lat,
                        pole.intersection_lon,
                        pole.dig_lat,
                        pole.dig_lon,
                    )
                return pole


def distance_feet(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance_meters = geodesic(point1, point2).meters
    distance_feet = math.trunc(distance_meters * 3.28084)
    return distance_feet


def get_direction(lat1, lon1, lat2, lon2) -> str:
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    angle = math.degrees(math.atan2(delta_lon, delta_lat)) % 360  # 0°=N, 90°=E

    directions = [
        "NORTH",
        "NORTHEAST",
        "EAST",
        "SOUTHEAST",
        "SOUTH",
        "SOUTHWEST",
        "WEST",
        "NORTHWEST",
    ]
    idx = round(angle / 45) % 8
    return directions[idx]


def print_poles_to_file(poles, filename="poles_output.txt"):
    """
    Prints multiple Pole objects to a single text file with formatted headers.

    Args:
        poles: List of Pole objects to print
        filename: Name of the output file (default: "poles_output.txt")
    """
    with open(filename, "w", encoding="utf-8") as f:
        # Create multiline string with all poles information
        all_poles_info = ""

        for pole in poles:
            all_poles_info += f"""==================

POLE RESTORATION
HAND DIGGING...

FROM THE INTERSECTION, POLE IS APPROX {pole.int_to_dig} FT {pole.int_to_dig_dir}
OF {pole.intersection} AND APPROX {pole.dig_to_pole} FT {pole.dig_to_pole_dir} OF {pole.dig_street}


POLE MARKINGS....

STRUCTNUM: {pole.pole_number}
GPS: {pole.lat},{pole.lon}
==================

"""

        f.write(all_poles_info)


if __name__ == "__main__":
    poles = parse_csv("../tests/unit/del.csv")
    final_poles = []
    for pole in poles:
        enriched_pole = tilequery(pole)
        final_pole = distance_from_inter_to_dig(enriched_pole)
        final_poles.append(final_pole)

    print_poles_to_file(final_poles, "processed_poles_output.txt")
    print(
        f"All {len(final_poles)} processed poles have been written to 'processed_poles_output.txt'!"
    )
