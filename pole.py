from dataclasses import dataclass
from typing import Optional


@dataclass
class Pole:
    pole_number: str
    longitude: float
    latitude: float
    dig_longitude: Optional[float] = None
    dig_latitude: Optional[float] = None
    dig_name: Optional[str] = "<DIG ST>"
    intersection_longitude: Optional[float] = None
    intersection_latitude: Optional[float] = None
    intersection_name: Optional[str] = "<INT ST>"
    intersection_to_dig_distance: Optional[float] = None
    dig_to_pole_distance: Optional[float] = None
    # int_to_dig_dir: direction of intersection -> point in dig street
    # dig_to_pole_dir: direction of point in dig street -> pole_number
    int_to_dig_dir: Optional[str] = "<NSEW>"
    dig_to_pole_dir: Optional[str] = "<NSEW>"

    @property
    def has_dig_point(self) -> bool:
        return self.dig_longitude is not None and self.dig_latitude is not None

    @property
    def has_intersection_point(self) -> bool:
        return (
            self.intersection_longitude is not None
            and self.intersection_latitude is not None
        )

    @property
    def is_ready_for_directions(self) -> bool:
        return self.has_dig_point and self.has_intersection_point