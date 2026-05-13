# fedora-harvester

Automate CKAN harvest jobs from a CSV definition file using the [ckanext-harvest](https://github.com/ckan/ckanext-harvest) API.

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python >= 3.11
- A CKAN instance with `ckanext-harvest` installed

## Setup

```bash
# Create venv and install dependencies
uv sync

# Configure your CKAN instance
cp .env.example .env
# Edit .env with your CKAN_URL and CKAN_API_KEY
```

## Usage

```bash
# Run against a CSV of harvest sources
uv run python -m src.cli examples/harvest_sources.csv

# With debug logging
uv run python -m src.cli examples/harvest_sources.csv --verbose
```

The CSV supports these columns:

| Column       | Required | Description |
|--------------|----------|-------------|
| `name`       | Yes | Unique identifier for the harvest source |
| `url`        | Yes | The source URL to harvest |
| `source_type`| Yes | Harvester type: `ckan`, `dcat`, `waf`, `csw`, etc. |
| `title`      | No | Human-readable name (defaults to `name`) |
| `owner_org`  | No | Organization name or ID |
| `frequency`  | No | `MANUAL`, `DAILY`, `WEEKLY`, `BIWEEKLY`, `ALWAYS` |
| `active`     | No | `True` or `False` (defaults to `True`) |
| `notes`      | No | Description |
| `config`     | No | JSON configuration string |

## How it works

For each row in the CSV:

1. **Check** if the harvest organization exist and **Create** it if missing. 
2. **Check** it the source exist and **Create** it if missing.
3. **Trigger** a harvest job.

## Running tests

```bash
uv run pytest tests/ -v
```
