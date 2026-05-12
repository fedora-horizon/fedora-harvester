import argparse
import logging
import sys

from dotenv import load_dotenv

from src.config import get_settings
from src.ckan_client import CkanClient
from src.csv_reader import parse_csv
from src.harvester import Harvester


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Trigger CKAN harvest jobs from a CSV file")
    parser.add_argument("csv_path", help="Path to CSV file with harvest source definitions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    settings = get_settings()
    client = CkanClient(settings["ckan_url"], settings["ckan_api_key"])
    harvester = Harvester(client)

    rows = parse_csv(args.csv_path)
    if not rows:
        logging.warning("No valid rows found in CSV")
        sys.exit(1)

    results = harvester.process_rows(rows)

    print()
    header = f"{'Source':<30} {'Status':<35} {'Job ID':<40}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['name']:<30} {r['status']:<35} {r['job_id'] or '-':<40}")

    errors = [r for r in results if r["status"].startswith("error")]
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
