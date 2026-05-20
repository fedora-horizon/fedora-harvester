import logging
import os
from src.ckan.ckan_client import CkanClient
from src.utils.csv_reader import parse_csv
from src.ckan.harvester import Harvester
from src.ckan.cleaner import Cleaner

logger = logging.getLogger(__name__)

_SUMMARY_BANNER = ( "\n\n"
    "#####################################################################\n"
    "#                            SUMMARY                                #\n"
    "#####################################################################"
)


def harvest_from_csv(ckan_client: CkanClient, csv_path: str) -> None:
    """Run harvest jobs for every row defined in a CSV file.

    Args:
        ckan_client: An instance of the CKAN client.
        csv_path: Path to the CSV file containing harvest source definitions.
    """
    harvester = Harvester(ckan_client)
    rows = parse_csv(csv_path)

    if not rows:
        logger.warning("No valid rows found in CSV.")
        return

    results = harvester.process_rows(rows)

    logger.info(_SUMMARY_BANNER)
    for res in results:
        logger.info(" - Source '%s': %s", res["name"], res["status"])


def delete_from_csv(ckan_client: CkanClient, csv_path: str) -> None:
    """Delete harvest sources for every row defined in a CSV file.

    Args:
        ckan_client: An instance of the CKAN client.
        csv_path: Path to the CSV file containing harvest source definitions.
    """
    cleaner = Cleaner(ckan_client)
    rows = parse_csv(csv_path)

    if not rows:
        logger.warning("No valid rows found in CSV.")
        return

    results = cleaner.process_rows(rows)

    logger.info(_SUMMARY_BANNER)
    for res in results:
        logger.info(" - Source '%s': %s", res["name"], res["status"])