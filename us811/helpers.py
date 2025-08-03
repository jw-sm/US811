from typing import TypedDict
import csv


class Poles(TypedDict):
    structnum: str
    lat: float
    lon: float


"""
file format:
colum1|column2|column3
structnum|lat|lon
"""


# Returning a list since it will be 50-100 items at most
def parse_csv(file_path: str) -> list[Poles]:
    poles = []
    with open(file_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            pole_no: Poles = {
                "structnum": row["structnum"].strip(),
                "lat": float(row["lat"].strip()),
                "lon": float(row["lon"].strip()),
            }
            poles.append(pole_no)
    return poles


list_of_poles = parse_csv("../tests/test_data.csv")
for pole in list_of_poles:
    print(f"{pole['structnum']} has gps coordinates of {pole['lat']},{pole['lon']}")
