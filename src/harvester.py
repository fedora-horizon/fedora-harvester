import logging

from src.ckan_client import CkanClient

logger = logging.getLogger(__name__)


class Harvester:
    def __init__(self, client: CkanClient):
        self.client = client

    def ensure_source(self, row: dict) -> tuple[str, str]:
        name = row["name"]
        try:
            existing = self.client.harvest_source_show(name)
            logger.info("Source '%s' already exists (id=%s)", name, existing["id"])
            return existing["id"], "existed"
        except RuntimeError as e:
            if "404" not in str(e) and "Not found" not in str(e) and "not found" not in str(e):
                raise

        create_data = {
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
        created = self.client.harvest_source_create(create_data)
        logger.info("Source '%s' created (id=%s)", name, created["id"])
        return created["id"], "created"

    def trigger_job(self, source_id: str) -> str:
        job = self.client.harvest_job_create(source_id)
        logger.info("Harvest job created (id=%s, status=%s)", job["id"], job.get("status"))
        return job["id"]

    def process_row(self, row: dict) -> dict:
        result: dict = {"name": row["name"], "source_id": None, "job_id": None, "status": "error"}
        try:
            source_id, action = self.ensure_source(row)
            result["source_id"] = source_id
            job_id = self.trigger_job(source_id)
            result["job_id"] = job_id
            result["status"] = f"{action} + job triggered"
        except Exception as e:
            logger.error("Failed to process '%s': %s", row["name"], e)
            result["status"] = f"error: {e}"
        return result

    def process_rows(self, rows: list[dict]) -> list[dict]:
        return [self.process_row(row) for row in rows]
