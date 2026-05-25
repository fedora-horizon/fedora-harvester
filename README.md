# fedora-harvester

Automate CKAN harvest jobs from a CSV definition file via the [ckanext-harvest](https://github.com/ckan/ckanext-harvest) API.

For each row in the CSV, fedora-harvester ensures the organization and harvest source exist in CKAN, then triggers a harvest job. It also supports deleting harvest sources along with their datasets and organizations.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- Python >= 3.11
- A CKAN instance with `ckanext-harvest` installed and enabled

## Installation

### Tool install (global CLI)

```bash
uv tool install git+ssh://git@gitlab.akka.eu:22522/fedora/fedora-harvester.git
```

Or install from a local checkout in editable mode:

```bash
git clone <repo-url>
cd fedora-harvester
uv tool install -e .
```

After installation the `fedora-harvester` command is available globally:

```bash
fedora-harvester --help
```

### Local development install

```bash
git clone <repo-url>
cd fedora-harvester
uv sync
```

This creates a virtual environment with all dependencies. Activate it or use `uv run` to execute commands.

## Configuration

```bash
cp .env.example .env
```

Edit `.env` with your CKAN instance details:

| Variable       | Description                     |
|----------------|---------------------------------|
| `CKAN_URL`     | Base URL of the CKAN instance   |
| `CKAN_API_KEY` | CKAN API key for authentication |

Both variables are required — the program exits with code 1 if either is missing or empty.

## Usage

```
fedora-harvester [-v] <command> <csv_path> [-n <int>]
```

### Commands

| Command    | Description                                                  |
|------------|--------------------------------------------------------------|
| `harvest`  | Create/ensure organizations and sources, then trigger jobs   |
| `delete`   | Delete datasets, harvest sources, and organizations          |
| `update`   | Not implemented                                              |

### Global flags

| Flag                 | Short | Description                            |
|----------------------|-------|----------------------------------------|
| `--verbose`          | `-v`  | Enable debug-level logging             |
| `--row-number`       | `-n`  | Process only a specific row (1-indexed) |

### Examples

```bash
# Harvest all sources defined in the CSV
fedora-harvester harvest sources/harvest_sources.csv

# Harvest a single source (row 2)
fedora-harvester harvest sources/harvest_sources.csv --row-number 2

# Delete sources, datasets, and organizations
fedora-harvester delete sources/harvest_sources.csv

# Verbose / debug output
fedora-harvester harvest sources/harvest_sources.csv --verbose
```

When using the local development install, prefix with `uv run`:

```bash
uv run fedora-harvester harvest sources/harvest_sources.csv
```

### CSV Format

The CSV is read with UTF-8 BOM encoding. Whitespace in column names and values is stripped. Rows missing a required field are skipped with a warning.

| Column       | Required | Description                                                      |
|--------------|----------|------------------------------------------------------------------|
| `name`       | Yes      | Unique identifier for the harvest source                         |
| `title`      | Yes      | Human-readable name (defaults to `name`)                         |
| `url`        | Yes      | Source URL to harvest                                            |
| `source_type`| Yes      | Harvester type: `ckan`, `dcat`, `waf`, `csw`, `dcat_rdf`, etc.  |
| `owner_org`  | Yes      | Organization name or ID                                          |
| `frequency`  | No       | `MANUAL`, `DAILY`, `WEEKLY`, `BIWEEKLY`, `ALWAYS` (default: `MANUAL`) |
| `active`     | No       | `True` or `False` (defaults to `True`)                                |
| `notes`      | No       | Description                                                      |
| `config`     | No       | JSON configuration string     |

### Example CSV

```csv
title,name,description,url,source_type,owner_org,frequency,active,notes,config
ISPRA,rep-isprambiente-it,,https://rep.isprambiente.it/file/catalog/ispra_catalog.ttl,dcat_rdf,rep-isprambiente-it,MANUAL,True,,{}
istat,istat-it,,https://www.istat.it/storage/IstatData/catalog_rev.rdf,dcat_rdf,istat-it,MANUAL,True,,{}
```

## How It Works

For each row in the CSV:

1. **Organization** — Check if the harvest organization exists; create it if missing.
2. **Source** — Check if the harvest source exists; create it if missing.
3. **Job** — Trigger a harvest job (queues it for immediate execution).

The `delete` command reverses this: it deletes the source's datasets, then the harvest source, then the organization.

## Development

### Running tests

```bash
uv run pytest tests/ -v
```

Tests use `unittest.mock` and do not require a real CKAN instance.

### Project structure

```
fedora-harvester/
├── .env.example             # Environment variable template
├── pyproject.toml           # Project metadata and dependencies
├── sources/
│   └── harvest_sources.csv  # Example CSV input
├── src/
│   ├── cli.py               # CLI entry point
│   ├── config/config.py     # Configuration and validation
│   ├── ckan/
│   │   ├── ckan_client.py   # CKAN API client
│   │   ├── harvester.py     # Harvest workflow
│   │   ├── cleaner.py       # Delete workflow
│   │   └── features.py      # Orchestration layer
│   └── utils/
│       ├── csv_reader.py    # CSV parsing
│       └── http_client.py   # HTTP client wrapper
└── tests/
    ├── test_csv_reader.py
    └── test_harvester.py
```

## Security Notes

- API credentials are stored in `.env` (gitignored) — never commit them to version control.
- SSL certificate verification is disabled on all HTTP requests (development-oriented).
