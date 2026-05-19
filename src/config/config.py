import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


def validate_config(cls):
    """Class decorator to validate that all uppercase attributes are set."""
    for key, val in vars(cls).items():
        if key.isupper() and val is None:
            raise ValueError(
                f"{key} is not set. Define it in .env or the environment."
            )
    return cls


@validate_config
class Config:
    CKAN_URL = os.getenv("CKAN_URL")
    CKAN_API_KEY = os.getenv("CKAN_API_KEY")


config = Config()
