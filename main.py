import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()
api_key = os.getenv("API_KEY")

def get_streetnames(pole: Pole) -> Pole:
    
    params = mapbox_params(api_key)

    base_url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{pole.lon},{pole.lat}.json"


def mapbox_params(api_key: str) -> dict[str, str | Any]:
    """
    Args:
        api_key: A string containing the Mapbox API Key
    Returns:
        the complete parameter dictionary needed to query the API with proper defaults
    """
    params: dict[str, str | Any] = {
        "radius": 1000,
        "limit": 25,
        "geometry": linestring,
        "dedupe": False,
        "types": "street",
        "layers": "road",
        "access_tokens": api_key,
    }
    return params

