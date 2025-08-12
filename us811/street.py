from helpers import Pole, parse_csv
from typing import TypedDict
import requests
import asyncio
import aiohttp


class Intersections(TypedDict):
    id: int
    lat: float
    lon: float
    distance: float
    street_count: int

class Metadata(TypedDict):
    street_name: str
    osm_id: int
    county: str
    city: str

class OverpassError(Exception):
    pass


async def fetch_metadata(session: aiohttp.ClientSession, coord: Pole) -> Metadata:
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": coord["lat"], "lon": coord["lon"], "format": "json"}

    async with session.get(base_url, params=params) as response:
        data = await response.json()
        
        return {
            "osm_id": int(data["osm_id"]),
            "county": data["address"].get("county", ""),
            "street_name": data["address"].get("road", "")
        }

async def reverse_geocode(coordinates: list[Pole]) -> list[Metadata]:
    headers = {"User-Agent": "us811/v1"}

    async with aiohttp.ClientSession(headers=headers) as session:
        task = [fetch_metadata(session, coord) for coord in coordinates]
        metadata_list = await asyncio.gather(*task)

    return metadata_list

