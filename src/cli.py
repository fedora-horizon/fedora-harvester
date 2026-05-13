import argparse
import logging
import sys

from dotenv import load_dotenv

import os
from src.ckan_client import CkanClient
from src.csv_reader import parse_csv
from src.harvester import Harvester


load_dotenv()

ckan_url = os.getenv("CKAN_URL")
ckan_api_key = os.getenv("CKAN_API_KEY")

def main() -> None:
    parser = argparse.ArgumentParser(description="CKAN harvest jobs from a CSV file")
    parser.add_argument("csv_path", help="Path to CSV file with harvest source definitions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    client = CkanClient(ckan_url, ckan_api_key)
    harvester = Harvester(client)

    rows = parse_csv(args.csv_path)
    if not rows:
        logging.warning("No valid rows found in CSV")
        sys.exit(1)

    results = harvester.process_rows(rows)
    logging.info("Processing completed. Summary:")
    for res in results:
        logging.info(" - Source '%s': %s", res["name"], res["status"])

if __name__ == "__main__":
    main()
