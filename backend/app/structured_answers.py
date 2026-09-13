from __future__ import annotations

from .repository import series
from .schemas import ChatRequest


COUNTRY_NAMES = {
    "india": "IND", "china": "CHN", "vietnam": "VNM", "indonesia": "IDN",
    "united states": "USA", "united kingdom": "GBR", "germany": "DEU",
    "japan": "JPN", "france": "FRA", "canada": "CAN", "australia": "AUS",
    "brazil": "BRA", "mexico": "MEX", "south africa": "ZAF", "nigeria": "NGA",
    "bangladesh": "BGD", "philippines": "PHL",
}


def answer(request: ChatRequest) -> tuple[str, list[dict], list[str]]:
    """Return a checked DuckDB fact for short GDP questions without a model."""

    question = request.question.lower()
    countries = [code for name, code in COUNTRY_NAMES.items() if name in question] or request.countries or ["IND"]
    current_gdp = "gdp" in question and "growth" not in question
    indicator = "NY.GDP.MKTP.CD" if current_gdp else "NY.GDP.MKTP.KD.ZG"
    summaries = []
    for country in countries:
        values = series(country, indicator, request.start_year, request.end_year)
        available = [row for row in values if row["value"] is not None]
        if not available:
            continue
        latest = available[-1]
        if current_gdp:
            summaries.append(f"{country}: ${latest['value'] / 1_000_000_000_000:.2f} trillion current-dollar GDP in {latest['year']}")
        else:
            summaries.append(f"{country}: {latest['value']:.2f}% GDP growth in {latest['year']}")
    citations = [{"source_id": "WB-WDI", "title": "World Development Indicators", "url": "https://api.worldbank.org/v2/"}]
    limitations = [
        "Structured World Bank data response; refresh before relying on current values.",
        "No causal conclusion is inferred from this indicator value.",
    ]
    return "Checked data response — " + "; ".join(summaries) + ".", citations, limitations
