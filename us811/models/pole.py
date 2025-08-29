from dataclasses import dataclass
from typing import Optional


@dataclass
class Pole:
    pole_number: str
    lon: float
    lat: float

    dig_lon: Optional[float] = None
    dig_lat: Optional[float] = None
    dig_street: Optional[str] = "<DIG ST>" 

    inter_lon_point: Optional[float] = None
    inter_lat_point: Optional[float] = None

    intersection_lon: Optional[float] = None
    intersection_lat: Optional[float] = None
    intersection: Optional[str] = "<INT ST>" 

    int_to_dig: Optional[int] = None
    dig_to_pole: Optional[int] = None

    int_to_dig_dir: Optional[str] = "<NSEW>" 
    dig_to_pole_dir: Optional[str] = "<NSEW>" 

    verbiage: Optional[str] = None
