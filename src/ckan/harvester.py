import logging

from src.ckan.ckan_client import CkanClient

logger = logging.getLogger(__name__)


class Harvester:
    def __init__(self, client: CkanClient, no_queue_run: bool = False) -> None:
        self.client = client
        self.no_queue_run = no_queue_run

    def add_source(self, row: dict) -> tuple[str, str]:
        name = row["name"]

        try:
            existing = self.client.harvest_source_show(name)
            source_id = existing.get("result", {}).get("id")
            logger.info("Source '%s' already exists (id=%s)", name, source_id)
            return source_id, "existed"
        except RuntimeError as e:
            if not any(keyword in str(e) for keyword in ("404", "Not found", "not found")):
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

        try:
            created = self.client.harvest_source_create(data)
            source_id = created.get("result", {}).get("id", row["name"])
            logger.info("Source created (id=%s)", source_id)
            return source_id, "created"
        except RuntimeError as e:
            logger.error("Failed to create source '%s': %s", name, e)
            return name, f"not created: {e}"

    def process_row(self, row: dict) -> dict:
        result: dict = {"name": row["name"], "status": ""}

        try:
            resp = self.client.create_organization(row)
            if resp:
                logger.info("Organization '%s' created successfully", row.get("owner_org", ""))

            logger.debug("Processing source '%s' with URL '%s'", row["name"], row["url"])

            source_id, action = self.add_source(row)
            result["status"] = action

            if action in ("existed", "created"):
                self._trigger_harvest_job(row, source_id, action, result)

        except RuntimeError as e:
            logger.error("Failed to process '%s': %s", row["name"], e)
            result["status"] = f"error: {e}"

        return result

    def _trigger_harvest_job(
        self, row: dict, source_id: str, action: str, result: dict
    ) -> None:
        """Create and optionally run a harvest job for the given source."""
        name = row["name"]

        try:
            # Queue the job, or run it immediately depending on the flag.
            job = self.client.harvest_job_create(source_id, run=not self.no_queue_run)

            if self.no_queue_run:
                logger.info("Harvest job for source '%s' triggered immediately", name)
                self.client.no_queue_harvest_run_job(source_id)
                logger.info("Harvest job for source '%s' completed", name)

            result["job_id"] = job.get("result", {}).get("id", "")
            result["status"] = f"{action} + job triggered"

        except RuntimeError as e:
            logger.error("Failed to trigger harvest job for '%s': %s", name, e)
            result["status"] = f"{action} + job failed: {e}"

    def process_rows(self, rows: list[dict]) -> list[dict]:
        results = []
        for row in rows:
            resp = self.process_row(row)
            results.append(resp)
        return results
