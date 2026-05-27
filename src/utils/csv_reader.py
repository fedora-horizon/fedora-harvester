import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "url", "source_type"]


def parse_csv(path: str, row_number: int = 0) -> list[dict]:
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()

    rows: list[dict] = []
    for i, (_, series) in enumerate(df.iterrows(), start=1):
        row = {}
        for col in df.columns:
            val = series[col].strip()
            row[col] = val

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

    if row_number == 0:
        pass  # Process all rows
    elif row_number > 0 and row_number <= len(rows):
        logger.debug("Processing only row number %d", row_number)
        return [rows[row_number - 1]]
    else:
        logger.warning(
            "Invalid row number %d. It should be between 1 and %d.",
            row_number,
            len(rows),
        )
        return []
    return rows
