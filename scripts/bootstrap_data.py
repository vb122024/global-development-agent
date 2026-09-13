from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.db import connect  # noqa: E402


def build_structured(data: dict) -> None:
    with connect("structured", read_only=False) as db:
        db.execute("CREATE TABLE IF NOT EXISTS countries(iso3 VARCHAR PRIMARY KEY, name VARCHAR, region VARCHAR, income_group VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS indicators(indicator_id VARCHAR PRIMARY KEY, name VARCHAR, unit VARCHAR, definition VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS sources(source_id VARCHAR PRIMARY KEY, url VARCHAR, retrieved_at VARCHAR, status VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS observations(country_iso3 VARCHAR, indicator_id VARCHAR, year INTEGER, value DOUBLE, unit VARCHAR, source_id VARCHAR, PRIMARY KEY(country_iso3, indicator_id, year, source_id))")
        db.execute("DELETE FROM countries"); db.execute("DELETE FROM indicators"); db.execute("DELETE FROM observations"); db.execute("DELETE FROM sources")
        for row in data["countries"]: db.execute("INSERT INTO countries VALUES (?, ?, ?, ?)", list(row.values()))
        for row in data["indicators"]: db.execute("INSERT INTO indicators VALUES (?, ?, ?, ?)", list(row.values()))
        db.execute("INSERT INTO sources VALUES (?, ?, ?, ?)", [data["source_id"], data["source_url"], data["retrieved_at"], data["fixture_status"]])
        units = {row["indicator_id"]: row["unit"] for row in data["indicators"]}
        for country, indicator, year, value in data["observations"]:
            db.execute("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)", [country, indicator, year, value, units[indicator], data["source_id"]])


def build_telemetry() -> None:
    with connect("telemetry", read_only=False) as db:
        db.execute("CREATE TABLE IF NOT EXISTS runs(run_id VARCHAR PRIMARY KEY, task VARCHAR, mode VARCHAR, status VARCHAR, started_at DOUBLE, ended_at DOUBLE, error_code VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS model_calls(call_id VARCHAR PRIMARY KEY, run_id VARCHAR, agent VARCHAR, model VARCHAR, input_tokens BIGINT, cached_tokens BIGINT, output_tokens BIGINT, estimated_cost_usd DOUBLE, created_at DOUBLE)")
        db.execute("CREATE TABLE IF NOT EXISTS tool_calls(call_id VARCHAR PRIMARY KEY, run_id VARCHAR, tool VARCHAR, arguments_json VARCHAR, status VARCHAR, created_at DOUBLE)")
        db.execute("CREATE TABLE IF NOT EXISTS eval_runs(eval_run_id VARCHAR PRIMARY KEY, config_version VARCHAR, started_at DOUBLE, status VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS eval_results(result_id VARCHAR PRIMARY KEY, eval_run_id VARCHAR, case_id VARCHAR, metric VARCHAR, score DOUBLE, passed BOOLEAN, explanation VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS embedding_jobs(job_id VARCHAR PRIMARY KEY, mode VARCHAR, vector_store_id VARCHAR, model VARCHAR, dimensions INTEGER, input_tokens BIGINT, status VARCHAR, availability_note VARCHAR)")
        db.execute("CREATE TABLE IF NOT EXISTS security_events(event_id VARCHAR PRIMARY KEY, action VARCHAR, outcome VARCHAR, correlation_id VARCHAR, created_at DOUBLE)")


if __name__ == "__main__":
    payload = json.loads((ROOT / "data" / "fixtures" / "world_bank_snapshot.json").read_text())
    build_structured(payload); build_telemetry()
    print("Created structured.duckdb and telemetry.duckdb")
