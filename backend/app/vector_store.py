from __future__ import annotations

import hashlib
from pathlib import Path

from .settings import settings


STORE_NAME = "global-development-world-bank-reports"


def _client():
    if not settings.openai_ready:
        raise RuntimeError("OPENAI_API_KEY is unavailable")
    from openai import OpenAI

    return OpenAI()


def remote_filename(slug: str, path: Path) -> str:
    """A stable name lets us detect an upload even if local state is lost."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return f"world-bank-{slug}-{digest}.pdf"


def list_uploaded_files(client=None) -> dict[str, str]:
    client = client or _client()
    return {item.filename: item.id for item in client.files.list(purpose="assistants")}


def upload_reviewed_file(path: Path, slug: str, client=None) -> tuple[str, bool]:
    """Reuse a matching remote file; never upload arbitrary or missing paths."""
    if not path.is_file() or path.suffix.lower() != ".pdf" or path.read_bytes()[:5] != b"%PDF-":
        raise ValueError("Expected a reviewed PDF file")
    client = client or _client()
    filename = remote_filename(slug, path)
    existing = list_uploaded_files(client).get(filename)
    if existing:
        return existing, False
    with path.open("rb") as handle:
        uploaded = client.files.create(file=(filename, handle), purpose="assistants")
    return uploaded.id, True


def create_empty_store(client=None) -> tuple[str, bool]:
    """Find or create a portal-visible store without indexing files."""
    client = client or _client()
    for item in client.vector_stores.list():
        if item.name == STORE_NAME:
            return item.id, False
    store = client.vector_stores.create(name=STORE_NAME)
    return store.id, True


def list_store_file_ids(vector_store_id: str, client=None) -> set[str]:
    client = client or _client()
    return {item.id for item in client.vector_stores.files.list(vector_store_id=vector_store_id)}


def index_uploaded_file(vector_store_id: str, file_id: str, client=None) -> bool:
    """Explicit paid indexing step; callers must opt in separately."""
    client = client or _client()
    if file_id in list_store_file_ids(vector_store_id, client):
        return False
    client.vector_stores.files.create_and_poll(vector_store_id=vector_store_id, file_id=file_id)
    return True


def search_managed_store(vector_store_id: str, query: str):
    """The managed retrieval API embeds the query using the store configuration."""

    if not vector_store_id.startswith("vs_") or not query.strip() or len(query) > 1000:
        raise ValueError("Invalid vector store or query")
    return _client().vector_stores.search(vector_store_id=vector_store_id, query=query, max_num_results=5)


def inspect_managed_store(vector_store_id: str, client=None) -> dict:
    """Return safe, portal-comparable managed-index metadata.

    OpenAI's managed vector stores do not return the raw embedding arrays. This
    endpoint reports only what the platform exposes: store usage and attached
    files. It performs no generation, embedding, upload, or indexing work.
    """

    if not vector_store_id.startswith("vs_"):
        raise ValueError("The managed vector store is not configured")
    client = client or _client()
    store = client.vector_stores.retrieve(vector_store_id)
    attached = list(client.vector_stores.files.list(vector_store_id=vector_store_id))
    uploaded = list(client.files.list(purpose="assistants"))
    attached_ids = {item.id for item in attached}
    return {
        "store_id": getattr(store, "id", vector_store_id),
        "name": getattr(store, "name", STORE_NAME),
        "usage_bytes": int(getattr(store, "usage_bytes", 0) or 0),
        "status": getattr(store, "status", "unknown"),
        "embedding_visibility": "Managed by OpenAI; raw embedding coordinates are not exposed.",
        "attached_files": [
            {
                "id": getattr(item, "id", ""),
                "status": getattr(item, "status", "unknown"),
                "usage_bytes": int(getattr(item, "usage_bytes", 0) or 0),
            }
            for item in attached
        ],
        "unattached_uploaded_files": [
            {"id": getattr(item, "id", ""), "filename": getattr(item, "filename", "Uploaded file"), "bytes": int(getattr(item, "bytes", 0) or 0)}
            for item in uploaded if getattr(item, "id", "") not in attached_ids
        ],
    }
