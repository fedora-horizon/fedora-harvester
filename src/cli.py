import sys
import argparse
import logging
from src.config.config import config
from src.ckan.ckan_client import CkanClient
from src.ckan.features import harvest_from_csv, delete_from_csv

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point — parse CLI arguments and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(description="CKAN harvest jobs from a CSV file.")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging.",
    )
    main_features = parser.add_mutually_exclusive_group(required=True)
    main_features.add_argument(
        "--harvest-from-csv",
        dest="harvest_from_csv",
        help="Path to CSV file with harvest source definitions to create.",
    )
    main_features.add_argument(
        "--delete-from-csv",
        dest="delete_from_csv",
        help="Path to CSV file with harvest source definitions to delete.",
    )
    main_features.add_argument(
        "--update-from-csv",
        dest="update_from_csv",
        help="Path to CSV file with harvest source definitions to update. (Not implemented yet)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    client = CkanClient(config.CKAN_URL, config.CKAN_API_KEY)

    if args.harvest_from_csv:
        harvest_from_csv(client, args.harvest_from_csv)
    elif args.delete_from_csv:
        delete_from_csv(client, args.delete_from_csv)
    elif args.update_from_csv:
        logger.error("--update-from-csv is not implemented yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()