from __future__ import annotations

from .db import connect

ALLOWED_INDICATORS = {"NY.GDP.MKTP.CD", "NY.GDP.MKTP.KD.ZG"}
ALLOWED_COUNTRIES = {"IND", "CHN", "VNM", "IDN", "BRA", "MEX", "ZAF", "NGA", "BGD", "PHL", "USA", "GBR", "DEU", "JPN", "FRA", "CAN", "AUS"}


def list_countries() -> list[dict]:
    with connect("structured") as db:
        rows = db.execute("SELECT iso3, name, region, income_group FROM countries ORDER BY name").fetchall()
    return [dict(zip(("iso3", "name", "region", "income_group"), row)) for row in rows]


def list_indicators() -> list[dict]:
    with connect("structured") as db:
        rows = db.execute("SELECT indicator_id, name, unit, definition FROM indicators ORDER BY name").fetchall()
    return [dict(zip(("indicator_id", "name", "unit", "definition"), row)) for row in rows]


def series(country: str, indicator: str, start_year: int, end_year: int) -> list[dict]:
    if country not in ALLOWED_COUNTRIES or indicator not in ALLOWED_INDICATORS:
        raise ValueError("Country or indicator is outside the MVP allowlist")
    if start_year > end_year or end_year - start_year > 30:
        raise ValueError("Invalid or excessive year range")
    with connect("structured") as db:
        rows = db.execute(
            """SELECT country_iso3, indicator_id, year, value, unit, source_id
               FROM observations WHERE country_iso3=? AND indicator_id=?
               AND year BETWEEN ? AND ? ORDER BY year""",
            [country, indicator, start_year, end_year],
        ).fetchall()
    keys = ("country", "indicator", "year", "value", "unit", "source_id")
    return [dict(zip(keys, row)) for row in rows]

