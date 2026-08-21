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

    # first_direction is direction of intersection to a point in dig street
    # second direction is direction of point in dig street to pole_number
    int_to_dig_dir: Optional[str] = "<NSEW>"
    dig_to_pole_dir: Optional[str] = "<NSEW>"