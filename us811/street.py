from helpers import Pole, parse_csv
import requests
from requests import Response


# Get the streetname of a given GPS coordinate
def reverse_geocode(gps: Pole) -> Response:
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": gps["lat"], "lon": gps["lon"], "format": "json"}
    headers = {'User-Agent': "us811/v1"}
    response = requests.get(base_url, params=params, headers=headers)
    return response.text


list_of_poles = parse_csv("../tests/test_data.csv")
response = reverse_geocode(list_of_poles[0])
print(response)
