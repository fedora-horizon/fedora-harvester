import os
from functools import lru_cache


@lru_cache
def get_settings():
    return {
        "ckan_url": os.environ["CKAN_URL"].rstrip("/"),
        "ckan_api_key": os.environ["CKAN_API_KEY"],
    }
