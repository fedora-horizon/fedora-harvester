import logging

from src.ckan.ckan_client import CkanClient

logger = logging.getLogger(__name__)


class Cleaner:
    def __init__(self, ckan_client: CkanClient):
        self.client = ckan_client

    def process_row(self, row: dict) -> dict:
        result: dict = {"name": row["name"], "status": ""}
        try:
            logger.info("Deleting '%s'...", row["name"])
            source = self.client.harvest_source_show(row["name"])
            source_id = source.get("result", {}).get("id")
            if not source_id:
                logger.warning(
                    "Source '%s' not found — skipping deletion.", row["name"]
                )
                result["status"] = "not found"
                return result
            self.client.delete_organization_datasets(row.get("owner_org", ""))
            logger.info(
                "Datasets for organization '%s' deleted successfully",
                row.get("owner_org", ""),
            )
            self.client.harvest_source_delete(source_id)
            logger.info("Source '%s' deleted successfully", row["name"])
            self.client.delete_organization(row.get("owner_org", ""))
            logger.info(
                "Organization '%s' deleted successfully", row.get("owner_org", "")
            )
            result["status"] = "deleted"
        except RuntimeError as e:
            logger.error("Failed to process '%s': %s", row["name"], e)
            result["status"] = f"not deleted: {e}"
        return result

    def process_rows(self, rows: list[dict]) -> list[dict]:
        results = []
        for row in rows:
            resp = self.process_row(row)
            results.append(resp)
        return results
