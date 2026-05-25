import logging
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


def harvest_from_csv(ckan_client: CkanClient, csv_path: str , row_number: int = 0) -> list:
    """Run harvest jobs for every row defined in a CSV file.

    Args:
        ckan_client: An instance of the CKAN client.
        csv_path: Path to the CSV file containing harvest source definitions.
        row_number: The specific row number to process.
    """
    harvester = Harvester(ckan_client)
    rows = parse_csv(csv_path, row_number=row_number)

    if not rows:
        logger.warning("No valid rows found in CSV.")
        return

    results = harvester.process_rows(rows)

    logger.info(_SUMMARY_BANNER)
    for res in results:
        logger.info(" - Source '%s': %s", res["name"], res["status"])
    
    return results


def delete_from_csv(ckan_client: CkanClient, csv_path: str, row_number: int = 0) -> list:
    """Delete harvest sources for every row defined in a CSV file.

    Args:
        ckan_client: An instance of the CKAN client.
        csv_path: Path to the CSV file containing harvest source definitions.
        row_number: The specific row number to process.
    """
    cleaner = Cleaner(ckan_client)
    rows = parse_csv(csv_path, row_number=row_number)

    if not rows:
        logger.warning("No valid rows found in CSV.")
        return

    results = cleaner.process_rows(rows)

    logger.info(_SUMMARY_BANNER)
    for res in results:
        logger.info(" - Source '%s': %s", res["name"], res["status"])
    
    return results
