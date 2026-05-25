import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


def validate_config(cls):
    """Class decorator to validate that all uppercase attributes are set."""
    status = True
    for key, val in vars(cls).items():
        if key.isupper() and (val is None or val == ""):
            logger.warning(
                f"""
                {key} is not set. 
                In Windows PowerShell : $env:{key}=<your_value>
                In Linux : export {key}=<your_value>""".strip()
            )
            status = False
    if not status:
        # raise ValueError("Configuration validation failed. Please set the missing environment variables.")
        exit(1)
    return cls


@validate_config
class Config:
    CKAN_URL = os.getenv("CKAN_URL")
    CKAN_API_KEY = os.getenv("CKAN_API_KEY")


config = Config()
