from typing import TypedDict
import csv


class Pole(TypedDict):
    structnum: str
    lat: float
    lon: float

def parse_csv(file_path: str) -> list[Pole]:
    poles = []
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
