"""Create an isolated, non-secret runtime before the application is imported."""

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("ADMIN_TOKEN", "test-owner-token")
os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")
# Tests never make paid provider calls, even when the owner has enabled local chat.
os.environ["OPENAI_API_KEY"] = ""
os.environ["CHAT_ENABLED"] = "false"
os.environ["PER_RUN_BUDGET_USD"] = "0"
ROOT = Path(__file__).resolve().parents[2]
TEST_DATA_DIR = ROOT / ".test-runtime"
os.environ.setdefault("GDI_DATA_DIR", str(TEST_DATA_DIR))
sys.path.insert(0, str(ROOT / "backend"))

from app.db import connect  # noqa: E402


def _build_test_data() -> None:
    """Rebuild fixtures outside the owner’s local DuckDB runtime."""
    payload = json.loads((ROOT / "data" / "fixtures" / "world_bank_snapshot.json").read_text())
    with connect("structured", read_only=False) as db:
        db.execute("CREATE TABLE IF NOT EXISTS countries(iso3 VARCHAR PRIMARY KEY, name VARCHAR, region VARCHAR, income_group VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS indicators(indicator_id VARCHAR PRIMARY KEY, name VARCHAR, unit VARCHAR, definition VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS sources(source_id VARCHAR PRIMARY KEY, url VARCHAR, retrieved_at VARCHAR, status VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS observations(country_iso3 VARCHAR, indicator_id VARCHAR, year INTEGER, value DOUBLE, unit VARCHAR, source_id VARCHAR, PRIMARY KEY(country_iso3, indicator_id, year, source_id))")
        db.execute("DELETE FROM countries; DELETE FROM indicators; DELETE FROM sources; DELETE FROM observations")
        for row in payload["countries"]:
            db.execute("INSERT INTO countries VALUES (?, ?, ?, ?)", list(row.values()))
        for row in payload["indicators"]:
            db.execute("INSERT INTO indicators VALUES (?, ?, ?, ?)", list(row.values()))
        db.execute("INSERT INTO sources VALUES (?, ?, ?, ?)", [payload["source_id"], payload["source_url"], payload["retrieved_at"], payload["fixture_status"]])
        units = {row["indicator_id"]: row["unit"] for row in payload["indicators"]}
        for country, indicator, year, value in payload["observations"]:
            db.execute("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)", [country, indicator, year, value, units[indicator], payload["source_id"]])
    with connect("telemetry", read_only=False) as db:
        db.execute("CREATE TABLE IF NOT EXISTS runs(run_id VARCHAR PRIMARY KEY, task VARCHAR, mode VARCHAR, status VARCHAR, started_at DOUBLE, ended_at DOUBLE, error_code VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS model_calls(call_id VARCHAR PRIMARY KEY, run_id VARCHAR, agent VARCHAR, model VARCHAR, input_tokens BIGINT, cached_tokens BIGINT, output_tokens BIGINT, estimated_cost_usd DOUBLE, created_at DOUBLE)")
        db.execute("CREATE TABLE IF NOT EXISTS tool_calls(call_id VARCHAR PRIMARY KEY, run_id VARCHAR, tool VARCHAR, arguments_json VARCHAR, status VARCHAR, created_at DOUBLE)")
        db.execute("CREATE TABLE IF NOT EXISTS eval_runs(eval_run_id VARCHAR PRIMARY KEY, config_version VARCHAR, started_at DOUBLE, status VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS eval_results(result_id VARCHAR PRIMARY KEY, eval_run_id VARCHAR, case_id VARCHAR, metric VARCHAR, score DOUBLE, passed BOOLEAN, explanation VARCHAR)")


_build_test_data()
