from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .live_agents import run_casual_chat, run_live, sandbox_status
from .repository import ALLOWED_COUNTRIES, ALLOWED_INDICATORS, list_countries, list_indicators, series
from .schemas import ChatRequest, ChatResponse, DataCleanRequest, DataRefreshRequest, SettingsPatch
from .conversation_memory import clear, context_for, ensure_session, remember
from .security import require_mutation_guard, require_owner, validate_prompt
from .settings import settings
from .state import runtime_state
from .telemetry import finish_run, log_model_call, log_tool_call, start_run

app = FastAPI(title="Global Development Intelligence Agent", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=True, allow_methods=["GET", "POST", "PATCH"], allow_headers=["*"])


@app.get("/")
def api_home():
    """Make the local API endpoint self-explanatory when opened in a browser."""

    return {
        "service": "Global Development Intelligence API",
        "dashboard": "http://127.0.0.1:4173/",
        "evaluation_lab": "http://127.0.0.1:4175/",
        "health": "/health",
    }


def _is_casual_chat(question: str) -> bool:
    """Keep non-development conversation to a single low-cost model turn."""

    text = question.strip()
    data_terms = (
        "gdp", "growth", "inflation", "population", "economy", "economic", "indicator",
        "world bank", "compare", "explain", "why", "evidence", "report", "research", "data", "development", "country", "countries",
        "india", "china", "vietnam", "indonesia", "united states", "united kingdom", "usa", "uk", "germany", "japan", "france", "canada", "australia", "brazil", "mexico", "south africa", "nigeria", "bangladesh", "philippines",
        "ind", "chn", "vnm", "idn", "gbr", "deu", "jpn", "fra", "can", "aus", "bra", "mex", "zaf", "nga", "bgd", "phl",
        "जीडीपी", "pib", "produit intérieur brut", "国内総生産", "国内生产总值", "국내총생산",
    )
    return bool(text) and not any(term in text.lower() for term in data_terms)


def _telemetry_call(operation, *args):
    """Telemetry is useful observability, never a prerequisite for user output."""

    try:
        return operation(*args)
    except Exception:
        return None


@app.get("/health")
def health():
    # A configured key alone does not make paid model calls available.
    live_ready = settings.openai_ready and settings.per_run_budget_usd > 0 and runtime_state.chat_enabled
    return {"status": "ok", "mode": "live-ready" if live_ready else "local"}


@app.get("/api/capabilities")
def capabilities(_: str = Depends(require_owner)):
    reasons = []
    if not runtime_state.chat_enabled: reasons.append("chat_disabled")
    if not settings.openai_ready: reasons.append("credential_unavailable")
    if settings.per_run_budget_usd <= 0: reasons.append("budget_not_configured")
    return {"direct_data": True, "live_chat": not reasons, "reasons": reasons, "sandbox": sandbox_status()}


@app.get("/api/countries")
def countries(_: str = Depends(require_owner)):
    return list_countries()


@app.get("/api/indicators")
def indicators(_: str = Depends(require_owner)):
    return list_indicators()


@app.get("/api/series")
def get_series(country: str = Query(), indicator: str = Query(), start_year: int = 2019, end_year: int = 2023, _: str = Depends(require_owner)):
    try:
        return series(country.upper(), indicator, start_year, end_year)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, _: str = Depends(require_mutation_guard)):
    validate_prompt(request.question)
    request.countries = [value.upper() for value in request.countries]
    if any(value not in ALLOWED_COUNTRIES for value in request.countries):
        raise HTTPException(400, "Country is outside the MVP allowlist")
    # Conversation memory shares the telemetry store, so an external DuckDB
    # inspector must not prevent an otherwise valid question from completing.
    session_id = request.session_id or uuid4().hex
    _telemetry_call(ensure_session, session_id)
    memory_context = _telemetry_call(context_for, session_id) or ""
    run_id = _telemetry_call(start_run, "chat", request.mode) or f"unrecorded-{uuid4()}"
    telemetry_available = not run_id.startswith("unrecorded-")
    try:
        if _is_casual_chat(request.question):
            if not runtime_state.chat_enabled:
                raise HTTPException(503, "Live chat is disabled by the owner")
            answer, model, usage, estimated_cost = await run_casual_chat(request.question)
            if telemetry_available:
                _telemetry_call(log_model_call, run_id, "casual_chat", model, usage, estimated_cost)
            citations, limitations, handoffs = [], ["Quick low-cost conversational response; no research tools or specialist handoffs were used."], []
        elif request.mode == "live":
            if not runtime_state.chat_enabled:
                raise HTTPException(503, "Live chat is disabled by the owner")
            answer, model, usage, estimated_cost = await run_live(request.question, memory_context)
            if telemetry_available:
                _telemetry_call(log_model_call, run_id, "multi_agent_run", model, usage, estimated_cost)
            citations, limitations = [], ["Verify all generated claims against cited source material."]
            handoffs = []
        if telemetry_available:
            _telemetry_call(finish_run, run_id, "completed")
            _telemetry_call(remember, session_id, request.question, answer)
        return ChatResponse(run_id=run_id, status="completed", answer=answer, citations=citations, model=model, estimated_cost_usd=estimated_cost, limitations=limitations, handoffs=handoffs, session_id=session_id)
    except HTTPException:
        if telemetry_available:
            _telemetry_call(finish_run, run_id, "refused", "capability_disabled")
        raise
    except Exception as exc:
        if telemetry_available:
            _telemetry_call(finish_run, run_id, "failed", type(exc).__name__)
        raise HTTPException(503, str(exc)) from exc


@app.delete("/api/conversation-memory")
def clear_conversation(session_id: str = Query(), _: str = Depends(require_mutation_guard)):
    clear(session_id)
    return {"cleared": True}


@app.patch("/api/admin/settings")
def patch_settings(patch: SettingsPatch, _: str = Depends(require_mutation_guard)):
    runtime_state.set_chat_enabled(patch.chat_enabled)
    return {"chat_enabled": runtime_state.chat_enabled, "applied": True}


@app.post("/api/admin/refresh-data")
def refresh_data(request: DataRefreshRequest, _: str = Depends(require_mutation_guard)):
    """Owner-only World Bank API ingestion. No OpenAI model is used."""
    from .data_refresh import refresh
    run_id = start_run("world_bank_refresh", "api")
    try:
        result = refresh(request.countries, request.start_year, request.end_year)
        log_tool_call(run_id, "world_bank_api", request.model_dump(), "completed")
        finish_run(run_id, "completed")
        return result
    except ValueError as exc:
        finish_run(run_id, "refused", "invalid_data_scope")
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        finish_run(run_id, "failed", type(exc).__name__)
        raise HTTPException(503, f"World Bank refresh failed: {type(exc).__name__}") from exc


@app.post("/api/admin/clean-data")
def clean_data(request: DataCleanRequest, _: str = Depends(require_mutation_guard)):
    """Deterministic, read-only quality check; model calls are deliberately disabled."""
    from .data_refresh import clean_preview
    if request.mode == "model":
        if settings.per_run_budget_usd <= 0:
            raise HTTPException(503, "Set a positive per-run cost budget before model-assisted cleaning")
        raise HTTPException(503, "Model-assisted cleaning is not enabled in this build")
    try:
        result = clean_preview(request.countries)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    run_id = start_run("data_clean_preview", "deterministic")
    log_tool_call(run_id, "quality_rules", request.model_dump(), "completed")
    finish_run(run_id, "completed")
    return result


@app.get("/api/admin/usage")
def usage(_: str = Depends(require_owner)):
    from .db import connect
    with connect("telemetry") as db:
        row = db.execute("SELECT count(*), sum(input_tokens), sum(output_tokens), sum(estimated_cost_usd) FROM model_calls").fetchone()
    return {"model_calls": row[0], "input_tokens": row[1], "output_tokens": row[2], "estimated_cost_usd": row[3], "cost_status": "unknown_when_null"}


@app.get("/api/admin/vector-store")
def vector_store_inspection(_: str = Depends(require_owner)):
    """Read-only metadata for the local document-index inspection panel."""
    from .vector_store import inspect_managed_store
    try:
        return inspect_managed_store(settings.vector_store_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, f"Vector store inspection failed: {type(exc).__name__}") from exc


@app.get("/api/admin/evals")
def eval_results(_: str = Depends(require_owner)):
    from .db import connect
    with connect("telemetry") as db:
        rows = db.execute("SELECT case_id, metric, score, passed, explanation FROM eval_results ORDER BY case_id").fetchall()
    return [{"case_id": r[0], "metric": r[1], "score": r[2], "passed": r[3], "explanation": r[4]} for r in rows]


@app.get("/api/admin/evaluation-dashboard")
def evaluation_dashboard(_: str = Depends(require_owner)):
    """Developer-only aggregate view of the project's local telemetry."""
    from .db import connect
    with connect("telemetry") as db:
        runs = db.execute("SELECT run_id, task, mode, status, started_at, ended_at, error_code FROM runs ORDER BY started_at DESC LIMIT 20").fetchall()
        evaluations = db.execute("SELECT case_id, metric, score, passed, explanation FROM eval_results ORDER BY rowid DESC LIMIT 30").fetchall()
        models = db.execute("SELECT model, count(*), sum(input_tokens), sum(output_tokens), sum(estimated_cost_usd) FROM model_calls GROUP BY model ORDER BY count(*) DESC").fetchall()
        tools = db.execute("SELECT tool, count(*), sum(CASE WHEN status='completed' THEN 1 ELSE 0 END) FROM tool_calls WHERE tool NOT LIKE '%graph%' GROUP BY tool ORDER BY count(*) DESC").fetchall()
    with connect("structured") as db:
        data_rows = db.execute("SELECT o.country_iso3, c.name, o.indicator_id, i.name, o.year, o.value, o.unit, o.source_id FROM observations o JOIN countries c ON c.iso3=o.country_iso3 JOIN indicators i ON i.indicator_id=o.indicator_id ORDER BY o.year DESC, c.name LIMIT 80").fetchall()
    from .vector_store import inspect_managed_store
    try:
        vector_store = inspect_managed_store(settings.vector_store_id) if settings.vector_store_id else None
    except Exception:
        vector_store = None
    return {
        "runs": [{"id": r[0], "task": r[1], "mode": r[2], "status": r[3], "started_at": r[4], "ended_at": r[5], "error": r[6]} for r in runs],
        "evaluations": [{"case_id": r[0], "metric": r[1], "score": r[2], "passed": r[3], "explanation": r[4]} for r in evaluations],
        "models": [{"model": r[0], "calls": r[1], "input_tokens": r[2] or 0, "output_tokens": r[3] or 0, "estimated_cost": r[4]} for r in models],
        "tools": [{"tool": r[0], "calls": r[1], "completed": r[2]} for r in tools],
        "vector_store": vector_store,
        "structured_data": [{"country": r[0], "country_name": r[1], "indicator": r[2], "indicator_name": r[3], "year": r[4], "value": r[5], "unit": r[6], "source": r[7]} for r in data_rows],
    }
