import os
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv


class MapboxClient:
    """
    Thin wrapper around the two Mapbox HTTP endpoints this project uses.
    Deliberately dumb: it knows how to make the requests, not what to do
    with the results. That logic lives in PoleEnricher.
    """

    TILEQUERY_URL = (
        "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{lon},{lat}.json"
    )
    DIRECTIONS_URL = (
        "https://api.mapbox.com/directions/v5/mapbox/driving/{origin_lon},{origin_lat};"
        "{dest_lon},{dest_lat}"
    )

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("A Mapbox API key is required")
        self.api_key = api_key
        self.session = requests.Session()

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "MapboxClient":
        env_path = env_path or Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        return cls(os.getenv("API_KEY"))

    def tilequery(self, lon: float, lat: float) -> dict:
        params: dict[str, Any] = {
            "radius": 1000,
            "limit": 25,
            "geometry": "linestring",
            "dedupe": False,
            "types": "street",
            "layers": "road",
            "access_token": self.api_key,
        }
        url = self.TILEQUERY_URL.format(lon=lon, lat=lat)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def directions(
        self, origin_lon: float, origin_lat: float, dest_lon: float, dest_lat: float
    ) -> dict:
        params = {"access_token": self.api_key, "steps": "true"}
        url = self.DIRECTIONS_URL.format(
            origin_lon=origin_lon,
            origin_lat=origin_lat,
            dest_lon=dest_lon,
            dest_lat=dest_lat,
        )
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()