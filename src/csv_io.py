import csv

from models.pole import Pole


def parse_csv(file_path: str) -> list[Pole]:
    poles: list[Pole] = []
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            poles.append(
                Pole(
                    pole_number=row["structnum"],
                    longitude=float(row["lon"]),
                    latitude=float(row["lat"]),
                )
            )
    return poles


def print_poles_to_file(poles: list[Pole], filename: str = "poles_output.txt") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        for pole in poles:
            f.write(
                f"==================\n"
                f"POLE IS APPROX {pole.intersection_to_dig_distance} FT {pole.int_to_dig_dir} "
                f"OF {pole.intersection_name} AND APPROX {pole.dig_to_pole_distance} FT "
                f"{pole.dig_to_pole_dir} OF {pole.dig_name}\n\n"
                f"{pole.pole_number}\n"
                f"{pole.latitude} {pole.longitude}\n"
                f"==================\n\n"
            )