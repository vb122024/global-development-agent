"""Export a source-labelled, secret-free World Bank snapshot for GitHub Pages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import connect  # noqa: E402


def export(destination: Path = ROOT / "frontend" / "public" / "data" / "world-bank-2019-2024.json") -> dict:
    with connect("structured") as db:
        sources = db.execute(
            "SELECT source_id, url, retrieved_at FROM sources WHERE status='api_refresh' ORDER BY retrieved_at DESC"
        ).fetchall()
        if not sources:
            raise RuntimeError("No live World Bank refresh exists yet; run the refresh action first")
        country_rows = db.execute("SELECT iso3, name, region, income_group FROM countries ORDER BY name").fetchall()
        indicator_rows = db.execute("SELECT indicator_id, name, unit, definition FROM indicators ORDER BY indicator_id").fetchall()
        observation_rows = db.execute(
            """SELECT country_iso3, indicator_id, year, value, unit, source_id
               FROM observations WHERE year BETWEEN 2019 AND 2024
               ORDER BY country_iso3, indicator_id, year"""
        ).fetchall()
    expected_countries = 17
    expected_observations = expected_countries * 2 * 6
    if len(country_rows) != expected_countries or len(observation_rows) != expected_observations:
        raise RuntimeError("Expected a complete 17-country, two-indicator, six-year refresh")
    payload = {
        "source_ids": sorted({row[5] for row in observation_rows}),
        "sources": [dict(zip(("source_id", "source_url", "retrieved_at"), row)) for row in sources if row[0] in {item[5] for item in observation_rows}],
        "retrieved_at": max(row[2] for row in sources),
        "range": {"start_year": 2019, "end_year": 2024},
        "countries": [dict(zip(("iso3", "name", "region", "income_group"), row)) for row in country_rows],
        "indicators": [dict(zip(("indicator_id", "name", "unit", "definition"), row)) for row in indicator_rows],
        "observations": [dict(zip(("country", "indicator", "year", "value", "unit", "source_id"), row)) for row in observation_rows],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return {"path": str(destination), "countries": len(country_rows), "observations": len(observation_rows), "source_ids": payload["source_ids"]}


if __name__ == "__main__":
    print(export())
