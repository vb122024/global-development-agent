"""Bounded World Bank ingestion and a read-only data-quality preview."""

from __future__ import annotations

import math
import json
from datetime import datetime, timezone
from uuid import uuid4

import httpx

from .db import connect
from .repository import ALLOWED_COUNTRIES, ALLOWED_INDICATORS
from .settings import ROOT

API_ROOT = "https://api.worldbank.org/v2"


def _scope(countries: list[str], start_year: int | None = None, end_year: int | None = None) -> list[str]:
    selected = sorted({country.upper() for country in countries}) if countries else sorted(ALLOWED_COUNTRIES)
    if not selected or any(country not in ALLOWED_COUNTRIES for country in selected):
        raise ValueError("Countries must be selected from the supported list")
    if start_year is not None and end_year is not None and (start_year > end_year or end_year - start_year > 30):
        raise ValueError("Invalid or excessive year range")
    return selected


def _world_bank_rows(payload: object, indicator: str, selected: set[str], first: int, last: int) -> tuple[list[tuple], int]:
    if not isinstance(payload, list) or len(payload) != 2 or not isinstance(payload[1], list):
        raise ValueError("World Bank returned an unexpected response")
    rows: list[tuple] = []
    missing = 0
    for item in payload[1]:
        country = item.get("countryiso3code")
        year_text = item.get("date")
        if country not in selected or not isinstance(year_text, str) or not year_text.isdigit():
            continue
        year = int(year_text)
        if not first <= year <= last:
            continue
        value = item.get("value")
        if value is None:
            missing += 1
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("World Bank returned a non-numeric observation")
        if indicator == "NY.GDP.MKTP.CD" and value < 0:
            raise ValueError("GDP cannot be negative")
        if indicator == "NY.GDP.MKTP.KD.ZG" and not -100 <= value <= 1000:
            raise ValueError("GDP growth is outside the accepted sanity range")
        rows.append((country, indicator, year, float(value)))
    return rows, missing


def refresh(countries: list[str], start_year: int, end_year: int) -> dict:
    """Fetch first, validate, then commit a scoped replacement in one transaction."""
    selected = _scope(countries, start_year, end_year)
    urls: list[str] = []
    all_rows: list[tuple] = []
    missing = 0
    with httpx.Client(timeout=25.0, follow_redirects=False) as client:
        for indicator in sorted(ALLOWED_INDICATORS):
            url = f"{API_ROOT}/country/{';'.join(selected)}/indicator/{indicator}"
            params = {"format": "json", "date": f"{start_year}:{end_year}", "per_page": 1000}
            response = client.get(url, params=params)
            response.raise_for_status()
            page = response.json()
            if not isinstance(page, list) or not page or int(page[0].get("pages", 1)) != 1:
                raise ValueError("World Bank response was incomplete or unexpectedly paginated")
            parsed, skipped = _world_bank_rows(page, indicator, set(selected), start_year, end_year)
            if not parsed:
                raise ValueError(f"World Bank returned no usable observations for {indicator}")
            all_rows.extend(parsed)
            missing += skipped
            urls.append(str(response.url))
    stamp = datetime.now(timezone.utc).isoformat()
    source_id = f"WB-WDI-{uuid4().hex[:12]}"
    units = {"NY.GDP.MKTP.CD": "current US$", "NY.GDP.MKTP.KD.ZG": "annual %"}
    catalog = json.loads((ROOT / "data" / "fixtures" / "world_bank_snapshot.json").read_text())["countries"]
    with connect("structured", read_only=False) as db:
        db.execute("BEGIN TRANSACTION")
        try:
            db.execute("INSERT INTO sources VALUES (?, ?, ?, ?)", [source_id, " | ".join(urls), stamp, "api_refresh"])
            for item in catalog:
                if item["iso3"] in selected:
                    db.execute("INSERT OR REPLACE INTO countries VALUES (?, ?, ?, ?)",
                               [item["iso3"], item["name"], item["region"], item["income_group"]])
            for country in selected:
                for indicator in ALLOWED_INDICATORS:
                    db.execute(
                        "DELETE FROM observations WHERE country_iso3=? AND indicator_id=? AND year BETWEEN ? AND ?",
                        [country, indicator, start_year, end_year],
                    )
            for country, indicator, year, value in all_rows:
                db.execute("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)", [country, indicator, year, value, units[indicator], source_id])
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
    return {"status": "refreshed", "countries": selected, "start_year": start_year, "end_year": end_year,
            "observations_written": len(all_rows), "missing_values_skipped": missing,
            "source_id": source_id, "source_urls": urls, "retrieved_at": stamp}


def clean_preview(countries: list[str]) -> dict:
    """Check the stored values without changing source data or calling a model."""
    selected = _scope(countries)
    placeholders = ",".join("?" for _ in selected)
    with connect("structured") as db:
        rows = db.execute(
            f"SELECT country_iso3, indicator_id, year, value FROM observations WHERE country_iso3 IN ({placeholders}) ORDER BY country_iso3, indicator_id, year",
            selected,
        ).fetchall()
    findings = []
    seen = set()
    for country, indicator, year, value in rows:
        key = (country, indicator, year)
        if key in seen:
            findings.append({"country": country, "indicator": indicator, "year": year, "issue": "duplicate_observation"})
        seen.add(key)
        if value is None or not math.isfinite(value):
            findings.append({"country": country, "indicator": indicator, "year": year, "issue": "missing_or_nonfinite"})
        elif indicator == "NY.GDP.MKTP.CD" and value < 0:
            findings.append({"country": country, "indicator": indicator, "year": year, "issue": "negative_gdp"})
        elif indicator == "NY.GDP.MKTP.KD.ZG" and not -100 <= value <= 1000:
            findings.append({"country": country, "indicator": indicator, "year": year, "issue": "growth_out_of_range"})
    return {"status": "preview_only", "model_status": "disabled", "model": None,
            "observations_checked": len(rows), "findings": findings[:100], "finding_count": len(findings),
            "estimated_cost_usd": 0, "message": "Source values were not changed. Model-assisted cleaning is disabled until explicitly enabled with a cost budget."}
