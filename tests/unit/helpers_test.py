import tempfile
import csv
from typing import List
from us811.helpers import parse_csv, Pole

def test_parse_csv() -> None:
    # Sample input data (as strings, matching CSV format)
    data: List[dict[str, str]] = [
        {"structnum": "tx_pole1", "lat": "42.1234567", "lon": "-92.283273"},
        {"structnum": "tx_pole2", "lat": "42.2234567", "lon": "-92.383273"},
    ]

    # Create temporary CSV file
    tmp_file_path: str
    with tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False) as tmp_file:
        writer: csv.DictWriter = csv.DictWriter(tmp_file, fieldnames=["structnum", "lat", "lon"])
        writer.writeheader()
        writer.writerows(data)
        tmp_file_path = tmp_file.name

    # Now that the file is closed (exiting the `with` block), it's safe to read
    result: List[Pole] = parse_csv(tmp_file_path)

    # Expected output with correct types
    expected: List[Pole] = [
        {"structnum": "tx_pole1", "lat": 42.1234567, "lon": -92.283273},
        {"structnum": "tx_pole2", "lat": 42.2234567, "lon": -92.383273},
    ]

    assert result == expected

