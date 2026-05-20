from unittest.mock import Mock

import pytest

from src.ckan.cleaner import Cleaner
from src.ckan.harvester import Harvester


class TestHarvesterAddSource:
    def test_returns_existing_source_id(self):
        client = Mock()
        client.harvest_source_show.return_value = {"result": {"id": "src-1"}}
        harv = Harvester(client)

        source_id, action = harv.add_source({"name": "s1"})

        assert source_id == "src-1"
        assert action == "existed"
        client.harvest_source_create.assert_not_called()

    def test_creates_source_when_not_found(self):
        client = Mock()
        client.harvest_source_show.side_effect = RuntimeError("404 Not Found")
        client.harvest_source_create.return_value = {"result": {"id": "src-new"}}
        harv = Harvester(client)

        source_id, action = harv.add_source({
            "name": "s1",
            "url": "http://ex.com",
            "source_type": "ckan",
        })

        assert source_id == "src-new"
        assert action == "created"
        client.harvest_source_create.assert_called_once()

    def test_re_raises_non_404_error(self):
        client = Mock()
        client.harvest_source_show.side_effect = RuntimeError("500 Server Error")
        harv = Harvester(client)

        with pytest.raises(RuntimeError):
            harv.add_source({"name": "s1"})

    def test_returns_error_on_create_failure(self):
        client = Mock()
        client.harvest_source_show.side_effect = RuntimeError("404 Not Found")
        client.harvest_source_create.side_effect = RuntimeError("403 Forbidden")
        harv = Harvester(client)

        source_id, action = harv.add_source({
            "name": "s1",
            "url": "http://ex.com",
            "source_type": "ckan",
        })

        assert "not created" in action


class TestHarvesterProcessRow:
    def test_triggers_job_for_existing_source(self):
        client = Mock()
        client.harvest_source_show.return_value = {"result": {"id": "src-1"}}
        client.harvest_job_create.return_value = {"result": {"id": "job-1"}}
        client.create_organization.return_value = {}
        harv = Harvester(client)

        result = harv.process_row({"name": "s1", "url": "http://ex.com", "source_type": "ckan"})

        assert result["name"] == "s1"
        assert result["status"] == "existed + job triggered"
        assert result["job_id"] == "job-1"
        client.harvest_job_create.assert_called_once_with("src-1")

    def test_triggers_job_for_new_source(self):
        client = Mock()
        client.harvest_source_show.side_effect = RuntimeError("404 Not Found")
        client.harvest_source_create.return_value = {"result": {"id": "src-new"}}
        client.harvest_job_create.return_value = {"result": {"id": "job-1"}}
        client.create_organization.return_value = {}
        harv = Harvester(client)

        result = harv.process_row({
            "name": "s1", "url": "http://ex.com", "source_type": "ckan",
        })

        assert result["name"] == "s1"
        assert result["status"] == "created + job triggered"
        assert result["job_id"] == "job-1"

    def test_handles_job_failure(self):
        client = Mock()
        client.harvest_source_show.return_value = {"result": {"id": "src-1"}}
        client.harvest_job_create.side_effect = RuntimeError("500 Job Error")
        client.create_organization.return_value = {}
        harv = Harvester(client)

        result = harv.process_row({"name": "s1", "url": "http://ex.com", "source_type": "ckan"})

        assert result["name"] == "s1"
        assert "job failed" in result["status"]

    def test_handles_owner_org_absent(self):
        client = Mock()
        client.harvest_source_show.return_value = {"result": {"id": "src-1"}}
        client.harvest_job_create.return_value = {"result": {"id": "job-1"}}
        client.create_organization.return_value = {}
        harv = Harvester(client)

        result = harv.process_row({"name": "s1", "url": "http://ex.com", "source_type": "ckan"})

        assert result["status"] == "existed + job triggered"


class TestHarvesterProcessRows:
    def test_returns_results_for_all_rows(self):
        client = Mock()
        client.harvest_source_show.side_effect = [
            {"result": {"id": "src-1"}},
            RuntimeError("404 Not Found"),
        ]
        client.harvest_source_create.return_value = {"result": {"id": "src-new"}}
        client.harvest_job_create.return_value = {"result": {"id": "job-1"}}
        client.create_organization.return_value = {}
        harv = Harvester(client)

        results = harv.process_rows([
            {"name": "s1", "url": "http://a.com", "source_type": "ckan"},
            {"name": "s2", "url": "http://b.com", "source_type": "dcat"},
        ])

        assert len(results) == 2
        assert results[0]["status"] == "existed + job triggered"
        assert results[1]["status"] == "created + job triggered"


class TestCleanerProcessRow:
    def test_deletes_source_and_org(self):
        client = Mock()
        client.harvest_source_show.return_value = {"result": {"id": "src-1"}}
        client.delete_organization_datasets.return_value = {"results": []}
        client.harvest_source_delete.return_value = {"success": True}
        client.delete_organization.return_value = {"success": True}
        cleaner = Cleaner(client)

        result = cleaner.process_row({"name": "s1", "owner_org": "org1"})

        assert result["status"] == "deleted"
        client.harvest_source_delete.assert_called_once_with("src-1")
        client.delete_organization.assert_called_once_with("org1")

    def test_skips_when_source_not_found(self):
        client = Mock()
        client.harvest_source_show.return_value = {"result": {}}
        cleaner = Cleaner(client)

        result = cleaner.process_row({"name": "s1"})

        assert result["status"] == "not found"
        client.harvest_source_delete.assert_not_called()
        client.delete_organization.assert_not_called()

    def test_handles_api_error(self):
        client = Mock()
        client.harvest_source_show.side_effect = RuntimeError("404 Not Found")
        cleaner = Cleaner(client)

        result = cleaner.process_row({"name": "s1"})

        assert "not deleted" in result["status"]
