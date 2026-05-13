from unittest.mock import Mock

from src.harvester import Harvester


def test_ensure_source_exists():
    client = Mock()
    client.harvest_source_show.return_value = {"id": "src-1", "name": "s1"}
    harv = Harvester(client)

    source_id, action = harv.ensure_source({"name": "s1"})

    assert source_id == "src-1"
    assert action == "existed"
    client.harvest_source_create.assert_not_called()


def test_ensure_source_creates():
    client = Mock()
    client.harvest_source_show.side_effect = RuntimeError("404 Not Found")
    client.harvest_source_create.return_value = {"id": "src-new", "name": "s1"}
    harv = Harvester(client)

    source_id, action = harv.ensure_source({
        "name": "s1",
        "url": "http://ex.com",
        "source_type": "ckan",
    })

    assert source_id == "src-new"
    assert action == "created"
    client.harvest_source_create.assert_called_once()


def test_process_row_success():
    client = Mock()
    client.harvest_source_show.return_value = {"id": "src-1"}
    client.harvest_job_create.return_value = {"id": "job-1", "status": "New"}
    harv = Harvester(client)

    result = harv.process_row({"name": "s1"})

    assert result["name"] == "s1"
    assert result["source_id"] == "src-1"
    assert result["job_id"] == "job-1"
    assert "job triggered" in result["status"]


def test_process_rows():
    client = Mock()
    client.harvest_source_show.side_effect = [
        {"id": "src-1"},
        RuntimeError("404 Not Found"),
    ]
    client.harvest_source_create.return_value = {"id": "src-new"}
    client.harvest_job_create.return_value = {"id": "job-1", "status": "New"}
    harv = Harvester(client)

    results = harv.process_rows([
        {"name": "s1", "url": "http://a.com", "source_type": "ckan"},
        {"name": "s2", "url": "http://b.com", "source_type": "dcat"},
    ])

    assert len(results) == 2
    assert results[0]["status"] == "existed + job triggered"
    assert results[1]["status"] == "created + job triggered"
