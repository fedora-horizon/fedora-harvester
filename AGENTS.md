# fedora-harvester — agent guide

## Stack
- Python 3.12, package manager: **uv** (`uv sync`, `uv run`, `uv add`)
- Dependencies: `pandas`, `requests`, `python-dotenv`
- No linter, formatter, typechecker, or pre-commit config

## Key commands
```bash
uv sync                              # install deps + dev
uv sync                              # install deps + dev
uv run python -m src.cli harvest <csv>              # harvest
uv run python -m src.cli delete <csv>               # delete
uv run python -m src.cli update <csv>               # NOT IMPLEMENTED
fedora-harvester harvest <csv>                      # CLI command (after `uv sync`)
uv run pytest tests/ -v -k <name>                   # single test
```

CLI uses subcommands (`harvest` / `delete` / `update`). `update` is a stub — no code behind it.

## Architecture

| File | Role |
|---|---|
| `src/cli.py` | Argparse entry point; creates `CkanClient` from config, dispatches to features |
| `src/config/config.py` | Loads `.env`; validates `CKAN_URL` / `CKAN_API_KEY` |
| `src/ckan/features.py` | Accepts `CkanClient` + CSV path; orchestrates `Harvester`/`Cleaner` |
| `src/ckan/harvester.py` | `Harvester` — create/ensure harvest sources and trigger jobs |
| `src/ckan/cleaner.py` | `Cleaner` — delete source + org datasets + org |
| `src/ckan/ckan_client.py` | CKAN REST API wrapper (`/api/3/action/*`); all methods return parsed `dict` |
| `src/utils/http_client.py` | `requests` wrapper with SSL **disabled** |
| `src/utils/csv_reader.py` | `parse_csv()` — pandas-based CSV parser |

## Quirks & gotchas

- **SSL verification is disabled** globally (`verify=False` in `HttpClient`); `InsecureRequestWarning` suppressed. This is intentional for the target environment.
- **`.env` is loaded implicitly** by `config.py` via `dotenv.load_dotenv()`. Required vars: `CKAN_URL`, `CKAN_API_KEY`. Missing vars raise `ValueError` at import with a descriptive message.
- **CSV quirks**: `config` column must be valid JSON or row is skipped; `active` column accepts `True`/`1`/`yes` (case-insensitive); BOM is handled.
- **Tests** are pure unit tests with `unittest.mock` — no integration/network. No `requests-mock`.
- **No build/CI/lint/typecheck** — there is nothing to run beyond `pytest`.
- **`Harvester.process_row`** checks if org exists, ensures source exists (creating if needed), then triggers a harvest job. Status strings: `"existed + job triggered"`, `"created + job triggered"`, or `"error: ..."`.
- **`Cleaner.process_row`** shows the source, deletes all org datasets, deletes the harvest source, then deletes the organization. Returns `"not found"` if the source doesn't exist.
- **`CkanClient`** methods all return parsed `dict` (CKAN Action API envelope: `{"success": bool, "result": ...}`).

## CSV columns
Required: `name`, `url`, `source_type`. Optional: `title`, `owner_org`, `frequency`, `active`, `notes`, `config`.
