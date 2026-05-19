import logging

from src.ckan_client import CkanClient

logger = logging.getLogger(__name__)


class Harvester:
    def __init__(self, client: CkanClient):
        self.client = client

    def add_source(self, row: dict) -> tuple[str, str]:
        name = row["name"]
        try:
            existing = self.client.harvest_source_show(name)
            logger.info("Source '%s' already exists (id=%s)", name, existing["id"])
            return existing["id"], "existed"
        except RuntimeError as e:
            if "404" not in str(e) and "Not found" not in str(e) and "not found" not in str(e):
                raise
        data = {
            "name": row["name"],
            "url": row["url"],
            "source_type": row["source_type"],
            "title": row.get("title", row["name"]),
            "owner_org": row.get("owner_org", ""),
            "frequency": row.get("frequency", "MANUAL"),
            "active": row.get("active", "True").lower() in ("true", "1", "yes"),
            "notes": row.get("notes", ""),
            "config": row.get("config", "{}"),
        }
        try :
            created = self.client.harvest_source_create(data)
            logger.info("Source created (id=%s)", name)
            # return created.json().get("id").get("result").get("id"), "created"
            return row["name"], "created"
        except Exception as e:
            logger.error("Failed to create source '%s': %s", name, e)
            return name, f"not created: {e}"

    def process_row(self, row: dict) -> dict:
        result: dict = {
            "name": row["name"], 
            "status": "error"
        }
        try:
            resp = self.client.create_organization(row)  # Ensure org exists, if specified
            if resp:
                logger.info("Organization '%s' created successfully", row["owner_org"])
            logger.debug("Processing source '%s' with URL '%s'", row["name"], row["url"])
            source_id, action = self.add_source(row)
            logger.info("Source '%s' created successfully", row["name"])
            result["status"] = f"{action}"
        except Exception as e:
            logger.error("Failed to process '%s': %s", row["name"], e)
            result["status"] = f"error: {e}"
        return result

    def process_rows(self, rows: list[dict]) -> list[dict]:
        results = []
        for row in rows:
            resp = self.process_row(row)
            results.append(resp)
        return results