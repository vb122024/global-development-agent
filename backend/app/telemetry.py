from __future__ import annotations

import json
import time
from uuid import uuid4

from .db import connect


def start_run(task: str, mode: str) -> str:
    run_id = str(uuid4())
    with connect("telemetry", read_only=False) as db:
        db.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?)",
            [run_id, task, mode, "running", time.time(), None, None],
        )
    return run_id


def finish_run(run_id: str, status: str, error_code: str | None = None) -> None:
    with connect("telemetry", read_only=False) as db:
        db.execute("UPDATE runs SET status=?, ended_at=?, error_code=? WHERE run_id=?", [status, time.time(), error_code, run_id])


def log_model_call(run_id: str, agent: str, model: str, usage: dict | None, cost: float | None) -> None:
    usage = usage or {}
    with connect("telemetry", read_only=False) as db:
        db.execute(
            "INSERT INTO model_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [str(uuid4()), run_id, agent, model, usage.get("input_tokens"), usage.get("cached_tokens"), usage.get("output_tokens"), cost, time.time()],
        )


def log_tool_call(run_id: str, tool: str, arguments: dict, status: str) -> None:
    with connect("telemetry", read_only=False) as db:
        db.execute(
            "INSERT INTO tool_calls VALUES (?, ?, ?, ?, ?, ?)",
            [str(uuid4()), run_id, tool, json.dumps(arguments, sort_keys=True), status, time.time()],
        )
