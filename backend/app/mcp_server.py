"""Read-only MCP facade for the same validated repository functions."""

from mcp.server.fastmcp import FastMCP

from .repository import list_countries, list_indicators, series

mcp = FastMCP("world-bank-snapshot")


@mcp.tool()
def get_countries() -> list[dict]:
    """List countries included in the frozen MVP snapshot."""
    return list_countries()


@mcp.tool()
def get_indicators() -> list[dict]:
    """List indicators and definitions in the frozen MVP snapshot."""
    return list_indicators()


@mcp.tool()
def get_series(country: str, indicator: str, start_year: int, end_year: int) -> list[dict]:
    """Return a bounded, allowlisted World Bank series."""
    return series(country.upper(), indicator, start_year, end_year)


if __name__ == "__main__":
    mcp.run()
