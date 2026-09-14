from __future__ import annotations

import json
from pathlib import Path

from .repository import series
from .vector_store import list_store_file_ids, search_managed_store

from .settings import ROOT, settings


# Tool-facing models sometimes use country names or indicator labels even when
# the prompt contains ISO IDs. Normalize those harmless aliases at the boundary
# so an otherwise valid research request does not terminate the run.
COUNTRY_ALIASES = {
    "INDIA": "IND", "CHINA": "CHN", "VIETNAM": "VNM", "INDONESIA": "IDN",
    "UNITED STATES": "USA", "USA": "USA", "UNITED KINGDOM": "GBR", "UK": "GBR",
    "GERMANY": "DEU", "JAPAN": "JPN", "FRANCE": "FRA", "CANADA": "CAN", "AUSTRALIA": "AUS",
    "BRAZIL": "BRA", "MEXICO": "MEX", "SOUTH AFRICA": "ZAF", "NIGERIA": "NGA",
    "BANGLADESH": "BGD", "PHILIPPINES": "PHL",
}
INDICATOR_ALIASES = {
    "GDP": "NY.GDP.MKTP.CD", "GDP (CURRENT US$)": "NY.GDP.MKTP.CD",
    "GDP GROWTH": "NY.GDP.MKTP.KD.ZG", "GDP GROWTH (ANNUAL %)": "NY.GDP.MKTP.KD.ZG",
    "NY.GDP.MKTP.CD": "NY.GDP.MKTP.CD", "NY.GDP.MKTP.KD.ZG": "NY.GDP.MKTP.KD.ZG",
}


def _country_code(value: str) -> str:
    clean = value.strip().upper()
    return COUNTRY_ALIASES.get(clean, clean)


def _indicator_code(value: str) -> str:
    clean = value.strip().upper()
    return INDICATOR_ALIASES.get(clean, clean)


def _instructions(name: str) -> str:
    return (ROOT / "agent_instructions" / f"{name}.txt").read_text(encoding="utf-8")


def _usage_from(*results) -> dict:
    """Combine token counts exposed by official Agents SDK run results."""

    totals = {"input_tokens": 0, "cached_tokens": 0, "output_tokens": 0}
    for run in results:
        usage = getattr(getattr(run, "context_wrapper", None), "usage", None)
        if usage is None:
            continue
        totals["input_tokens"] += int(getattr(usage, "input_tokens", 0) or 0)
        totals["output_tokens"] += int(getattr(usage, "output_tokens", 0) or 0)
        details = getattr(usage, "input_tokens_details", None)
        totals["cached_tokens"] += int(getattr(details, "cached_tokens", 0) or 0)
    return totals


def _estimated_cost(usage: dict) -> float | None:
    """Estimate cost only when the owner has entered verified current prices."""

    if settings.input_usd_per_million <= 0 or settings.output_usd_per_million <= 0:
        return None
    uncached_input = max(0, usage["input_tokens"] - usage["cached_tokens"])
    return round(
        uncached_input * settings.input_usd_per_million / 1_000_000
        + usage["output_tokens"] * settings.output_usd_per_million / 1_000_000,
        8,
    )


def structured_retrieval(country: str, indicator: str, start_year: int, end_year: int) -> list[dict]:
    """Read the frozen, allowlisted time-series snapshot for a function tool."""

    return series(_country_code(country), _indicator_code(indicator), start_year, end_year)


def local_vector_retrieval(query: str, limit: int = 3) -> list[dict]:
    """Search the reviewed local report catalog without calling an embedding API.

    The shipped MVP has report metadata but no locally indexed full-text corpus.
    This token-vector fallback is deliberately labelled as catalog retrieval so a
    response cannot imply that a report passage or a managed vector store was
    searched. A future live tool can replace this body with managed retrieval.
    """

    terms = {term.lower() for term in query.split() if term.isalnum()}
    if not terms or len(query) > 1000:
        raise ValueError("Invalid retrieval query")
    catalog_path = ROOT / "docs" / "corpus" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    ranked = []
    for item in catalog:
        searchable = " ".join(str(item.get(key, "")) for key in ("title", "citation", "publisher", "year")).lower()
        score = sum(term in searchable for term in terms)
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["slug"]))
    return [
        {
            "source_id": item["slug"],
            "title": item["title"],
            "url": item["url"],
            "retrieval_mode": "local_catalog_token_vector",
        }
        for _, item in ranked[:max(1, min(limit, 5))]
    ]


def managed_vector_retrieval(query: str) -> list[dict]:
    """Retrieve indexed report passages only after the owner has enabled RAG.

    This function is never reached in the shipped zero-budget configuration.
    It deliberately refuses an empty store so a model cannot claim it searched
    reports that have only been uploaded, not embedded and attached.
    """

    if not settings.vector_store_id:
        raise ValueError("The managed vector store is not configured")
    if not list_store_file_ids(settings.vector_store_id):
        raise ValueError("The managed vector store has no indexed files")
    results = search_managed_store(settings.vector_store_id, query)
    return [
        {
            "source_id": getattr(item, "file_id", "openai-managed-file"),
            "title": getattr(item, "filename", "Reviewed World Bank report"),
            "text": getattr(item, "text", ""),
            "retrieval_mode": "openai_managed_vector_store",
        }
        for item in results.data
    ]


def _live_function_tools(function_tool, include_managed_retrieval: bool = False):
    """Wrap the same bounded local operations when a paid run is enabled."""

    @function_tool
    def get_structured_series(country: str, indicator: str, start_year: int, end_year: int) -> list[dict]:
        """Retrieve an allowlisted World Bank time series from the frozen snapshot."""
        return structured_retrieval(country, indicator, start_year, end_year)

    @function_tool
    def search_local_report_catalog(query: str) -> list[dict]:
        """Search reviewed local report metadata; it does not retrieve report passages."""
        return local_vector_retrieval(query)

    tools = [get_structured_series, search_local_report_catalog]
    if include_managed_retrieval:
        @function_tool
        def search_indexed_reports(query: str) -> list[dict]:
            """Retrieve passages from owner-approved indexed World Bank PDFs."""
            return managed_vector_retrieval(query)

        tools.append(search_indexed_reports)
    return tools


async def run_live(question: str, memory_context: str = "") -> tuple[str, str, dict, float | None]:
    """Run the Agents SDK only when credentials and budget are explicitly ready."""

    if not settings.openai_ready:
        raise RuntimeError("OPENAI_API_KEY is unavailable")
    if settings.per_run_budget_usd <= 0:
        raise RuntimeError("A positive per-run budget is required")
    try:
        from agents import Agent, Runner, function_tool
    except ImportError as exc:
        raise RuntimeError("OpenAI Agents SDK is not installed") from exc

    model = settings.reasoning_model if len(question.split()) > 18 else settings.default_model
    structured_specialist = Agent(
        name="Structured-data specialist",
        instructions=_instructions("structured_retrieval"),
        model=settings.default_model,
        tools=_live_function_tools(function_tool)[:1],
    )
    document_specialist = Agent(
        name="Document-retrieval specialist",
        instructions=_instructions("document_retrieval"),
        model=settings.default_model,
        tools=_live_function_tools(function_tool, include_managed_retrieval=True)[1:],
    )

    # SDK-native handoffs give each specialist a narrow tool boundary. The
    # final synthesis run receives only the routed, tool-grounded output.
    routing = Agent(
        name="Orchestrator",
        instructions=_instructions("orchestrator"),
        model=settings.default_model,
        handoffs=[structured_specialist, document_specialist],
    )
    prompt = f"{memory_context}\n\nCurrent question: {question}" if memory_context else question
    route = await Runner.run(routing, prompt, max_turns=4)
    synthesis = Agent(name="Synthesis", instructions=_instructions("synthesis"), model=settings.default_model)
    result = await Runner.run(synthesis, f"Question: {question}\nValidated route and evidence: {route.final_output}", max_turns=2)
    usage = _usage_from(route, result)
    return str(result.final_output), model, usage, _estimated_cost(usage)


async def run_casual_chat(question: str) -> tuple[str, str, dict, float | None]:
    """Use one low-cost model turn for non-development conversation.

    Casual chat deliberately has no tools, handoffs, report retrieval, or
    conversation context. This keeps it brief and prevents incidental chatter
    from spending tokens on the research workflow.
    """

    if not settings.openai_ready:
        raise RuntimeError("OPENAI_API_KEY is unavailable")
    if settings.per_run_budget_usd <= 0:
        raise RuntimeError("A positive per-run budget is required")
    try:
        from agents import Agent, Runner
    except ImportError as exc:
        raise RuntimeError("OpenAI Agents SDK is not installed") from exc

    agent = Agent(
        name="Conversational guide",
        instructions=(
            "Reply naturally and helpfully to casual conversation in the user's language. "
            "Use no tools. Keep the answer to one short sentence, at most 18 words. "
            "If asked about this application, briefly direct the user to World Bank country comparisons and report evidence."
        ),
        model=settings.default_model,
    )
    result = await Runner.run(agent, question, max_turns=1)
    usage = _usage_from(result)
    return str(result.final_output), settings.default_model, usage, _estimated_cost(usage)


def evaluation_agent_definition():
    """Create the judge only for an explicitly requested paid evaluation run."""

    if not settings.openai_ready:
        raise RuntimeError("OPENAI_API_KEY is unavailable")
    from agents import Agent
    return Agent(name="Evaluation judge", instructions=_instructions("evaluation"), model=settings.default_model)


def sandbox_status() -> dict:
    """No local host-shell fallback: report actions remain disabled until verified."""

    return {
        "configured": settings.sandbox_ready,
        "mode": settings.sandbox_mode,
        "fail_closed": True,
    }
