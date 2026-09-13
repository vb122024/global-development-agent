from __future__ import annotations

import time
from uuid import uuid4

from .db import connect


def ensure_session(session_id: str | None) -> str:
    """Create or reuse an opaque local conversation identifier."""
    value = session_id or uuid4().hex
    with connect("telemetry", read_only=False) as db:
        db.execute("CREATE TABLE IF NOT EXISTS conversation_memory (session_id VARCHAR, turn_number INTEGER, question VARCHAR, answer_excerpt VARCHAR, created_at DOUBLE, PRIMARY KEY(session_id, turn_number))")
        db.execute("DELETE FROM conversation_memory WHERE created_at < ?", [time.time() - 60 * 60 * 24 * 30])
    return value


def context_for(session_id: str, limit: int = 3) -> str:
    """Return only a short local context window, never an unbounded transcript."""
    with connect("telemetry", read_only=False) as db:
        rows = db.execute("SELECT question, answer_excerpt FROM conversation_memory WHERE session_id=? ORDER BY turn_number DESC LIMIT ?", [session_id, limit]).fetchall()
    if not rows:
        return ""
    rows.reverse()
    return "\n".join(f"Earlier question: {question}\nEarlier answer: {answer}" for question, answer in rows)


def remember(session_id: str, question: str, answer: str) -> None:
    with connect("telemetry", read_only=False) as db:
        next_turn = db.execute("SELECT coalesce(max(turn_number), 0) + 1 FROM conversation_memory WHERE session_id=?", [session_id]).fetchone()[0]
        db.execute("INSERT INTO conversation_memory VALUES (?, ?, ?, ?, ?)", [session_id, next_turn, question[:500], answer[:1200], time.time()])


def clear(session_id: str) -> None:
    with connect("telemetry", read_only=False) as db:
        db.execute("DELETE FROM conversation_memory WHERE session_id=?", [session_id])
