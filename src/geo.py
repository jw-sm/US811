import math

from geopy.distance import geodesic

METERS_TO_FEET = 3.28084

_COMPASS_DIRECTIONS = [
    "NORTH",
    "NORTHEAST",
    "EAST",
    "SOUTHEAST",
    "SOUTH",
    "SOUTHWEST",
    "WEST",
    "NORTHWEST",
]


def distance_feet(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Straight-line (geodesic) distance between two points, in feet."""
    meters = geodesic((lat1, lon1), (lat2, lon2)).meters
    return math.trunc(meters * METERS_TO_FEET)


def meters_to_feet(meters: float) -> int:
    return math.trunc(meters * METERS_TO_FEET)


def get_direction(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Compass direction from point 1 to point 2."""
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    angle = math.degrees(math.atan2(delta_lon, delta_lat)) % 360  # 0deg = N, 90deg = E
    idx = round(angle / 45) % 8
    return _COMPASS_DIRECTIONS[idx]