import logging

from src.ckan.ckan_client import CkanClient

logger = logging.getLogger(__name__)


class Updater:
    def __init__(self, ckan_client: CkanClient):
        self.client = ckan_client

    def process_row(self, row: dict) -> dict:
        result: dict = {"name": row["name"], "status": ""}
        try:
            logger.info("Updating '%s'...", row["name"])
            source = self.client.harvest_source_show(row["name"])
            source_id = source.get("result", {}).get("id")
            if not source_id:
                logger.warning(
                    "Source '%s' not found — skipping update.", row["name"]
                )
                result["status"] = "not found"
                return result
            self.client.harvest_source_update(source_id, row)
            logger.info("Source '%s' updated successfully", row["name"])
            result["status"] = "updated"
        except RuntimeError as e:
            logger.error("Failed to process '%s': %s", row["name"], e)
            result["status"] = f"not updated: {e}"
        return result

    def process_rows(self, rows: list[dict]) -> list[dict]:
        results = []
        for row in rows:
            resp = self.process_row(row)
            results.append(resp)
        return results
