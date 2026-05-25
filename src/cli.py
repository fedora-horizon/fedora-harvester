import sys
import argparse
import logging
from src.config.config import config
from src.ckan.ckan_client import CkanClient
from src.ckan.features import harvest_from_csv, delete_from_csv

logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point — parse CLI arguments and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(
        description="Automate CKAN harvest jobs from a CSV file."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging.",
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Sub-command"
    )

    p_harvest = subparsers.add_parser(
        "harvest", help="Create/ensure harvest sources and trigger jobs"
    )
    p_harvest.add_argument(
        "csv_path", help="Path to CSV file with harvest source definitions"
    )

    p_delete = subparsers.add_parser(
        "delete", help="Delete harvest sources, datasets, and organizations"
    )
    p_delete.add_argument(
        "csv_path", help="Path to CSV file with harvest source definitions"
    )

    p_update = subparsers.add_parser(
        "update", help="Update harvest sources (NOT IMPLEMENTED)"
    )
    p_update.add_argument(
        "csv_path", help="Path to CSV file with harvest source definitions"
    )

    parser.add_argument(
        "--row_number",
        "-n",
        type=int,
        help="Row number to process.",
        default=0,
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    client = CkanClient(config.CKAN_URL, config.CKAN_API_KEY)

    if args.command == "harvest":
        harvest_from_csv(client, args.csv_path, row_number=args.row_number)
    elif args.command == "delete":
        delete_from_csv(client, args.csv_path, row_number=args.row_number)
    elif args.command == "update":
        logger.error("update is not implemented yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()
