import csv
import json
import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "url", "source_type"]


def parse_csv(path: str) -> list[dict]:
    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, raw in enumerate(reader, start=1):
            row = {}
            for k, v in raw.items():
                if v is None:
                    continue
                key = k.strip()
                val = v.strip()
                if not val:
                    continue
                row[key] = val

            missing = [f for f in REQUIRED_FIELDS if f not in row]
            if missing:
                logger.warning("Row %d: missing required fields %s — skipped", i, missing)
                continue

            if "config" in row:
                try:
                    json.loads(row["config"])
                except json.JSONDecodeError as e:
                    logger.warning("Row %d: invalid JSON in config — skipped: %s", i, e)
                    continue

            rows.append(row)

    return rows
