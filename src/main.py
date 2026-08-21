from csv_io import parse_csv, print_poles_to_file
from enrichment import PoleEnricher
from mapbox_client import MapboxClient


def main() -> None:
    client = MapboxClient.from_env()
    enricher = PoleEnricher(client)

    poles = parse_csv("../tests/unit/mesia14.csv")
    final_poles = [enricher.enrich(pole) for pole in poles]

    print_poles_to_file(final_poles, "14.txt")
    print(f"All {len(final_poles)} processed poles have been written to '14.txt'!")


if __name__ == "__main__":
    main()
