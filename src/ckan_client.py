import logging

from src.http_client import HttpClient

logger = logging.getLogger(__name__)


class CkanClient:
    def __init__(self, base_url: str, api_key: str):
        self.http = HttpClient(
            base_url=base_url,
            default_headers={"Authorization": api_key},
        )

    def _call_api(self, action: str, data: dict | None = None) -> dict:
        resp = self.http.post(f"/api/3/action/{action}", json=data or {})
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
