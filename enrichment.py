from typing import Optional

from geo import distance_feet, get_direction, meters_to_feet
from mapbox_client import MapboxClient
from matching import find_matching_step
from models.pole import Pole
from normalize import normalize

_SEARCH_PRIORITIES = [
    ("street", "name"),
    ("street", "ref"),
    ("primary", "name"),
    ("primary", "ref"),
]


class PoleEnricher:
    """
    Orchestrates the two-call Mapbox pipeline for a single Pole:
      1. tilequery -> nearest two streets (dig street + intersection street)
      2. directions -> real routed distance from intersection to the dig point

    This is a class (not free functions) because every step needs the same
    MapboxClient, and because "enrich a pole" is naturally a sequence of
    dependent operations you call together, not independent utilities.
    """

    def __init__(self, client: MapboxClient):
        self.client = client

    def enrich(self, pole: Pole) -> Pole:
        self._find_nearby_streets(pole)
        self._measure_intersection_to_dig(pole)
        return pole

    # -- step 1: nearest streets -------------------------------------------------

    def _find_nearby_streets(self, pole: Pole) -> Pole:
        data = self.client.tilequery(pole.longitude, pole.latitude)
        all_features = data.get("features", [])

        valid_streets = self._select_two_streets(all_features)
        if len(valid_streets) != 2:
            return pole

        dig_feature, inter_feature = valid_streets
        self._apply_dig_street(pole, dig_feature)
        self._apply_intersection_street(pole, inter_feature)
        return pole

    @staticmethod
    def _select_two_streets(features: list[dict]) -> list[dict]:
        valid_streets: list[dict] = []
        seen_names: set[str] = set()

        for class_type, key in _SEARCH_PRIORITIES:
            if len(valid_streets) >= 2:
                break
            for item in features:
                if len(valid_streets) >= 2:
                    break
                if not isinstance(item, dict):
                    continue
                properties = item.get("properties", {})
                if properties.get("class") != class_type:
                    continue
                identifier = properties.get(key)
                if identifier and identifier not in seen_names:
                    seen_names.add(identifier)
                    valid_streets.append(item)

        return valid_streets

    @staticmethod
    def _apply_dig_street(pole: Pole, feature: dict) -> None:
        coords = feature.get("geometry", {}).get("coordinates")
        if coords and isinstance(coords, list) and len(coords) >= 2:
            pole.dig_longitude, pole.dig_latitude = coords[0], coords[1]

        properties = feature.get("properties", {})
        name = properties.get("name") or properties.get("ref", "")
        pole.dig_name = normalize(name)

    @staticmethod
    def _apply_intersection_street(pole: Pole, feature: dict) -> None:
        coords = feature.get("geometry", {}).get("coordinates")
        if coords and isinstance(coords, list) and len(coords) >= 2:
            pole.intersection_longitude, pole.intersection_latitude = (
                coords[0],
                coords[1],
            )

        properties = feature.get("properties", {})
        name = properties.get("name") or properties.get("ref", "")
        pole.intersection_name = normalize(name)

    # -- step 2: routed distance -------------------------------------------------

    def _measure_intersection_to_dig(self, pole: Pole) -> Pole:
        if not pole.is_ready_for_directions:
            return pole

        data = self.client.directions(
            pole.intersection_longitude,
            pole.intersection_latitude,
            pole.dig_longitude,
            pole.dig_latitude,
        )
        routes = data.get("routes")
        if not routes:
            return pole

        for leg in routes[0].get("legs", []):
            steps = leg.get("steps", [])
            match = find_matching_step(steps, pole.dig_name)
            if match is None:
                continue

            index, step = match
            self._apply_match(pole, steps, index, step)
            return pole

        return pole

    @staticmethod
    def _apply_match(pole: Pole, steps: list[dict], index: int, step: dict) -> None:
        pole.dig_to_pole_distance = distance_feet(
            pole.latitude, pole.longitude, pole.dig_latitude, pole.dig_longitude
        )

        if index > 0:
            prev = steps[index - 1]
            prev_name = (prev.get("name", "") or prev.get("ref", "")).upper()
            if prev_name:
                pole.intersection_name = prev_name

        if step.get("intersections"):
            lon, lat = step["intersections"][0]["location"]
            pole.intersection_longitude, pole.intersection_latitude = lon, lat

        pole.intersection_to_dig_distance = meters_to_feet(step.get("distance", 0))

        pole.dig_to_pole_dir = get_direction(
            pole.dig_latitude, pole.dig_longitude, pole.latitude, pole.longitude
        )
        if pole.intersection_latitude and pole.intersection_longitude:
            pole.int_to_dig_dir = get_direction(
                pole.intersection_latitude,
                pole.intersection_longitude,
                pole.dig_latitude,
                pole.dig_longitude,
            )