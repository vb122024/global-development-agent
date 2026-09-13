"""Prepare official World Bank PDFs and manage their OpenAI portal objects.

Run from the repository root with backend/.venv/bin/python. Uploading and
creating an empty store are separate from the opt-in embedding/index step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.vector_store import (  # noqa: E402
    create_empty_store,
    index_uploaded_file,
    list_store_file_ids,
    list_uploaded_files,
    remote_filename,
    upload_reviewed_file,
)

CATALOG = ROOT / "docs" / "corpus" / "catalog.json"
CORPUS_DIR = ROOT / "data" / "source_documents"
STATE_FILE = ROOT / "data" / "runtime" / "openai_corpus_state.json"
ALLOWED_HOSTS = {"documents1.worldbank.org", "openknowledge.worldbank.org"}
MAX_PDF_BYTES = 15 * 1024 * 1024


def catalog() -> list[dict]:
    rows = json.loads(CATALOG.read_text())
    for row in rows:
        parsed = urlparse(row["url"])
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"Unreviewed source host for {row['slug']}")
    return rows


def document_path(row: dict) -> Path:
    return CORPUS_DIR / f"{row['slug']}.pdf"


def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"files": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def prepare() -> None:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for row in catalog():
        path = document_path(row)
        if path.exists():
            if path.read_bytes()[:5] != b"%PDF-":
                raise ValueError(f"Existing file is not a PDF: {path}")
            print(f"Ready: {row['slug']} ({path.stat().st_size:,} bytes)")
            continue
        request = Request(row["url"], headers={"User-Agent": "GlobalDevelopmentPortfolio/0.1 (educational corpus)"})
        with urlopen(request, timeout=30) as response:
            if urlparse(response.url).hostname not in ALLOWED_HOSTS:
                raise ValueError("Report redirected to an unreviewed host")
            data = response.read(MAX_PDF_BYTES + 1)
        if len(data) > MAX_PDF_BYTES or not data.startswith(b"%PDF-"):
            raise ValueError(f"Unexpected report format or size: {row['slug']}")
        path.write_bytes(data)
        print(f"Downloaded: {row['slug']} ({len(data):,} bytes)")


def upload() -> None:
    state = load_state()
    remote = list_uploaded_files()
    for row in catalog():
        path = document_path(row)
        if not path.exists():
            raise FileNotFoundError(f"Run prepare first: {path}")
        expected_name = remote_filename(row["slug"], path)
        # Reuse a portal file even when a previous run was interrupted before
        # saving the local manifest.
        file_id = remote.get(expected_name)
        created = False
        if not file_id:
            file_id, created = upload_reviewed_file(path, row["slug"])
        state.setdefault("files", {})[row["slug"]] = {
            "file_id": file_id,
            "filename": expected_name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_url": row["url"],
            "title": row["title"],
            "license": row["license"],
        }
        state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        print(f"{'Uploaded' if created else 'Reused'}: {row['slug']} ({file_id})")


def create_store() -> None:
    state = load_state()
    store_id, created = create_empty_store()
    state["vector_store_id"] = store_id
    state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    print(f"{'Created' if created else 'Reused'} empty vector store: {store_id}")


def status() -> None:
    state = load_state()
    remote = list_uploaded_files()
    for row in catalog():
        local = state.get("files", {}).get(row["slug"], {})
        filename = local.get("filename")
        print(f"{row['slug']}: {'visible' if filename in remote else 'missing'} in OpenAI Files")
    store_id = state.get("vector_store_id")
    if store_id:
        indexed = list_store_file_ids(store_id)
        print(f"Vector store: {store_id}; attached files: {len(indexed)}")
    else:
        print("Vector store: not yet created")


def index(allow_model_indexing: bool) -> None:
    if not allow_model_indexing:
        raise ValueError("Indexing invokes embeddings; pass --allow-model-indexing explicitly")
    state = load_state()
    store_id = state.get("vector_store_id")
    if not store_id:
        raise ValueError("Create the vector store first")
    for row in catalog():
        file_id = state.get("files", {}).get(row["slug"], {}).get("file_id")
        if not file_id:
            raise ValueError(f"Upload {row['slug']} first")
        created = index_uploaded_file(store_id, file_id)
        print(f"{'Indexed' if created else 'Already indexed'}: {row['slug']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "upload", "create-store", "status", "index"])
    parser.add_argument("--allow-model-indexing", action="store_true")
    args = parser.parse_args()
    {"prepare": prepare, "upload": upload, "create-store": create_store, "status": status,
     "index": lambda: index(args.allow_model_indexing)}[args.action]()


if __name__ == "__main__":
    main()
