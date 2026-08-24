from csv_io import parse_csv, print_poles_to_file
from enrichment import PoleEnricher
from mapbox_client import MapboxClient


def main() -> None:
    client = MapboxClient.from_env()
    enricher = PoleEnricher(client)

    poles = parse_csv("tests/unit/test_file.csv")
    final_poles = [enricher.enrich(pole) for pole in poles]

    print_poles_to_file(final_poles, "test_file.txt")
    print(f"All {len(final_poles)} processed poles have been written to 'test_file.txt'!")


if __name__ == "__main__":
    main()
