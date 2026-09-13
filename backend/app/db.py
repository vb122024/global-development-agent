from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import duckdb

from .settings import settings


DB_FILES = {
    "structured": "structured.duckdb",
    "telemetry": "telemetry.duckdb",
}


def db_path(name: str) -> Path:
    if name not in DB_FILES:
        raise ValueError(f"Unknown database: {name}")
    return settings.data_dir / DB_FILES[name]


@contextmanager
def connect(name: str, read_only: bool = True):
    """Open one named store; callers never provide paths or arbitrary databases."""

    path = db_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(path), read_only=read_only and path.exists())
    try:
        yield connection
    finally:
        connection.close()
