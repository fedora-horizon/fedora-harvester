import logging

import requests

logger = logging.getLogger(__name__)


class CkanClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": api_key})

    def _call_api(self, action: str, data: dict | None = None) -> dict:
        url = f"{self.base_url}/api/3/action/{action}"
        try:
            resp = self.session.post(url, json=data or {})
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise RuntimeError(f"CKAN HTTP error ({action}): {e}")

        payload = resp.json()
        if not payload.get("success"):
            msg = payload.get("error", {}).get("message", "Unknown error")
            raise RuntimeError(f"CKAN API error ({action}): {msg}")

        return payload["result"]

    def harvest_source_show(self, source_name: str) -> dict:
        return self._call_api("harvest_source_show", {"id": source_name})

    def harvest_source_create(self, data: dict) -> dict:
        return self._call_api("harvest_source_create", data)

    def harvest_job_create(self, source_id: str, run: bool = True) -> dict:
        return self._call_api("harvest_job_create", {"source_id": source_id, "run": run})
