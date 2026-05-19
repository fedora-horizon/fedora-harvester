import logging
import os
from dotenv import load_dotenv
from src.ckan_client import CkanClient
from src.csv_reader import parse_csv
from src.harvester import Harvester
from src.cleaner import Cleaner

load_dotenv()

ckan_url = os.getenv("CKAN_URL")
ckan_api_key = os.getenv("CKAN_API_KEY")

if not ckan_url or not ckan_api_key:
    raise ValueError(
        "CKAN_URL and CKAN_API_KEY must be set in .env or environment."
    )

logger = logging.getLogger(__name__)

_SUMMARY_BANNER = ( "\n\n"
    "#####################################################################\n"
    "#                            SUMMARY                                #\n"
    "#####################################################################"
)


def harvest_from_csv(csv_path: str) -> None:
    """Run harvest jobs for every row defined in a CSV file.

    Args:
        csv_path: Path to the CSV file containing harvest source definitions.
    """
    client = CkanClient(ckan_url, ckan_api_key)
    harvester = Harvester(client)
    rows = parse_csv(csv_path)

    if not rows:
        logger.warning("No valid rows found in CSV.")
        return

    results = harvester.process_rows(rows)

    logger.info(_SUMMARY_BANNER)
    for res in results:
        logger.info(" - Source '%s': %s", res["name"], res["status"])


def delete_from_csv(csv_path: str) -> None:
    """Delete harvest sources for every row defined in a CSV file.

    Args:
        csv_path: Path to the CSV file containing harvest source definitions.
    """
    client = CkanClient(ckan_url, ckan_api_key)
    cleaner = Cleaner(client)
    rows = parse_csv(csv_path)

    if not rows:
        logger.warning("No valid rows found in CSV.")
        return

    results = cleaner.process_rows(rows)

    logger.info(_SUMMARY_BANNER)
    for res in results:
        logger.info(" - Source '%s': %s", res["name"], res["status"])