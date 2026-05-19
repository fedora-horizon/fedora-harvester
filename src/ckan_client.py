import logging
from src.http_client import HttpClient

logger = logging.getLogger(__name__)

_ORGANIZATION_FIELDS = frozenset({"name", "title", "description", "image_url", "extras"})


class CkanClient:
    """Client for interacting with the CKAN REST API """

    API_BASE_PATH = "/api/3/action"

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialise the CKAN client.

        Args:
            base_url: Base URL of the CKAN instance.
            api_key: CKAN API key used for authenticated requests.
        """
        self.http = HttpClient(
            base_url=base_url,
            default_headers={"Authorization": api_key},
        )

    # ------------------------------------------------------------------
    # Organizations
    # ------------------------------------------------------------------

    def list_organizations(self) -> list[dict]:
        """Return a list of all organizations registered in CKAN."""
        response = self.http.get(f"{self.API_BASE_PATH}/organization_list")
        return response.json()

    def show_organization(self, org_name: str, include_datasets: bool = True) -> dict:
        """Retrieve details for an organization by name or ID.

        Args:
            org_name: Name or ID of the organization.
            include_datasets: When ``True`` (default), the response includes a list of datasets.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/organization_show",
            json={"id": org_name,
                  "include_datasets": include_datasets},
        ).json()
        
    def create_organization(self, data: dict) -> dict:
        """Create an organization in CKAN if it does not already exist.

        Args:
            data: Organization payload. Only the fields defined in
                  ``_ORGANIZATION_FIELDS`` are forwarded to the API.

        Returns:
            The API response dict, or an empty dict if the organization
            already exists.
        """
        organizations = self.list_organizations()
        owner_org = data.get("owner_org", "")

        if owner_org in organizations.get("result", []):
            logger.info("Organization '%s' already exists — skipping creation.", owner_org)
            return {}

        payload = {key: data[key] for key in _ORGANIZATION_FIELDS if key in data}
        return self.http.post(f"{self.API_BASE_PATH}/organization_create", json=payload).json()

    def delete_organization(self, org_id: str) -> dict:
        """Delete an organization by ID.

        Args:
            org_id: ID of the organization to delete.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/organization_delete",
            json={"id": org_id},
        ).json()
    
    def delete_organization_datasets(self, org_id: str) -> dict:
        """Delete all datasets belonging to an organization.

        Args:
            org_id: ID of the organization whose datasets should be deleted.
        """
        org = self.show_organization(org_id)
        datasets = org.get("result", {}).get("packages", [])
        results = []
        for dataset in datasets:
            dataset_id = dataset.get("id")
            if dataset_id:
                self.delete_package(dataset_id)
                result = self.purge_package(dataset_id)
                results.append([dataset_id, result.get("success", False)])
        return {"results": results}

    # ------------------------------------------------------------------
    # Harvest sources
    # ------------------------------------------------------------------

    def harvest_source_show(self, source_name: str, include_datasets: bool = True) -> dict:
        """Retrieve details for a harvest source by name or ID.

        Args:
            source_name: Name or ID of the harvest source.
            include_datasets: When ``True`` (default), the response includes a list of datasets.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/harvest_source_show",
            json={"id": source_name,
                  "include_datasets": include_datasets}
        ).json()

    def harvest_source_create(self, data: dict) -> dict:
        """Create a new harvest source.

        Args:
            data: Harvest source payload accepted by the CKAN harvesting extension.
        """
        return self.http.post(f"{self.API_BASE_PATH}/harvest_source_create", json=data).json()

    def harvest_source_delete(self, source_id: str) -> dict:
        """(Soft) Delete a harvest source by ID.

        Args:
            source_id: ID of the harvest source to delete.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/harvest_source_delete",
            json={"id": source_id},
        ).json()

    def harvest_source_purge(self, source_id: str) -> dict:
        """Permanently remove a harvest source from the database.

        Args:
            source_id: ID of the harvest source to purge.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/harvest_source_purge",
            json={"id": source_id},
        ).json()

    # ------------------------------------------------------------------
    # Packages
    # ------------------------------------------------------------------

    def list_packages(self) -> list[dict]:
        """Return a list of all packages registered in CKAN."""
        response = self.http.get(f"{self.API_BASE_PATH}/package_list")
        return response.json()

    def delete_package(self, package_id: str) -> dict:
        """(Soft) Delete a package by ID.

        Args:
            package_id: ID of the package to delete.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/package_delete",
            json={"id": package_id},
        ).json()

    def purge_package(self, package_id: str) -> dict:
        """Permanently remove a package from the database.

        Args:
            package_id: ID of the package to purge.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/dataset_purge",
            json={"id": package_id},
        ).json()
    # ------------------------------------------------------------------
    # Harvest jobs
    # ------------------------------------------------------------------

    def harvest_job_create(self, source_id: str, *, run: bool = True) -> dict:
        """Create (and optionally run) a harvest job for the given source.

        Args:
            source_id: ID of the harvest source to target.
            run: When ``True`` (default), the job is queued for immediate
                 execution after creation.
        """
        return self.http.post(
            f"{self.API_BASE_PATH}/harvest_job_create",
            json={"source_id": source_id, "run": run},
        ).json()
