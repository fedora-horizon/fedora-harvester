import logging
from src.http_client import HttpClient

logger = logging.getLogger(__name__)

class CkanClient:
    def __init__(self, 
                 base_url: str, 
                 api_key: str):
        self.http = HttpClient(
            base_url=base_url,
            default_headers={"Authorization": api_key},
        )

    def list_organizations(self) -> list[dict]:
        organizations =  self.http.get("/api/3/action/organization_list")
        return organizations.json()

    def create_organization(self, data: dict) -> dict:
        organizations = self.list_organizations()
        if data['owner_org'] in organizations['result']:
            logger.info("Organization '%s' already exists", data['owner_org'])
            return {}
        expected_fields = ["name", "title", "description", "image_url", "extras"]
        body = {k: data[k] for k in expected_fields if k in data}
        return self.http.post("/api/3/action/organization_create", json=body)

    def harvest_source_show(self, source_name: str) -> dict:
        return self.http.post("/api/3/action/harvest_source_show", json={"id": source_name})

    def harvest_source_create(self, data: dict) -> dict:
        return self.http.post("/api/3/action/harvest_source_create", json=data)

    def harvest_job_create(self, 
                           source_id: str, 
                           run: bool = True) -> dict:
        return self.http.post("/api/3/action/harvest_job_create", json= {"source_id": source_id, "run": run})
