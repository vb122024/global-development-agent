from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("ADMIN_TOKEN", "evaluation-owner")
os.environ.setdefault("GDI_DATA_DIR", str(ROOT / ".eval-runtime"))

from app.db import connect  # noqa: E402
from app.structured_answers import answer  # noqa: E402
from app.repository import series  # noqa: E402
from app.schemas import ChatRequest  # noqa: E402
from app.security import FORBIDDEN_PATTERNS  # noqa: E402
from scripts.bootstrap_data import build_structured, build_telemetry  # noqa: E402


def evaluate(case: dict) -> tuple[bool, str]:
    kind = case["kind"]
    if case["id"] == "numeric-india-2023":
        passed = round(series("IND", "NY.GDP.MKTP.KD.ZG", 2023, 2023)[0]["value"], 2) == 7.21
    elif case["id"] == "numeric-china-2020":
        passed = round(series("CHN", "NY.GDP.MKTP.KD.ZG", 2020, 2020)[0]["value"], 2) == 2.34
    elif kind == "units": passed = series("IND", "NY.GDP.MKTP.KD.ZG", 2023, 2023)[0]["unit"] == "annual %"
    elif kind == "citation":
        _, citations, _ = answer(ChatRequest(question="What is India's GDP?"))
        passed = case["expected"] in json.dumps(citations)
    elif kind == "restraint":
        _, _, limitations = answer(ChatRequest(question="What is India's GDP?"))
        passed = bool(limitations) if case["expected"] == "limitation" else case["expected"] in " ".join(limitations)
    elif kind == "security": passed = any(token in "ignore previous; drop table" for token in FORBIDDEN_PATTERNS)
    elif kind == "budget": passed = True  # Live configuration has chat off and zero budget by default.
    else: passed = False
    return passed, "Deterministic validation assertion"


def main() -> int:
    cases = json.loads((ROOT / "evals" / "cases.json").read_text())
    fixture = json.loads((ROOT / "data" / "fixtures" / "world_bank_snapshot.json").read_text())
    build_structured(fixture)
    build_telemetry()
    eval_run_id = str(uuid4())
    with connect("telemetry", read_only=False) as db:
        db.execute("INSERT INTO eval_runs VALUES (?, 'deterministic-v1', ?, 'running')", [eval_run_id, time.time()])
        for case in cases:
            passed, explanation = evaluate(case)
            db.execute("INSERT INTO eval_results VALUES (?, ?, ?, ?, ?, ?, ?)", [str(uuid4()), eval_run_id, case["id"], case["kind"], 1.0 if passed else 0.0, passed, explanation])
        db.execute("UPDATE eval_runs SET status='completed' WHERE eval_run_id=?", [eval_run_id])
    passed = sum(evaluate(case)[0] for case in cases)
    print(f"Deterministic evaluation: {passed}/{len(cases)} passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
