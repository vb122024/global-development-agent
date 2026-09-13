from pathlib import Path
from types import SimpleNamespace

from app.vector_store import create_empty_store, inspect_managed_store, remote_filename, upload_reviewed_file


class FakeFiles:
    def __init__(self):
        self.uploaded = []

    def list(self, purpose):
        assert purpose == "assistants"
        return self.uploaded

    def create(self, file, purpose):
        assert purpose == "assistants"
        name, handle = file
        assert handle.read(5) == b"%PDF-"
        item = SimpleNamespace(filename=name, id="file-test")
        self.uploaded.append(item)
        return item


class FakeStores:
    def __init__(self):
        self.stores = []

    def list(self):
        return self.stores

    def create(self, name):
        item = SimpleNamespace(name=name, id="vs_test")
        self.stores.append(item)
        return item


def test_upload_and_store_creation_are_repeatable_without_indexing(tmp_path: Path):
    path = tmp_path / "report.pdf"
    path.write_bytes(b"%PDF-1.7 reviewed report")
    client = SimpleNamespace(files=FakeFiles(), vector_stores=FakeStores())

    first = upload_reviewed_file(path, "overview", client)
    second = upload_reviewed_file(path, "overview", client)
    assert first == ("file-test", True)
    assert second == ("file-test", False)
    assert len(client.files.uploaded) == 1
    assert client.files.uploaded[0].filename == remote_filename("overview", path)

    assert create_empty_store(client) == ("vs_test", True)
    assert create_empty_store(client) == ("vs_test", False)
    assert len(client.vector_stores.stores) == 1


def test_store_inspection_reports_files_without_exposing_vectors():
    attached = [SimpleNamespace(id="file-indexed", status="completed", usage_bytes=4096)]
    remote_file = SimpleNamespace(id="file-uploaded", filename="report.pdf", bytes=2048)
    stores = SimpleNamespace(
        retrieve=lambda _store_id: SimpleNamespace(id="vs_test", name="Test store", usage_bytes=4096, status="completed"),
        files=SimpleNamespace(list=lambda vector_store_id: attached),
    )
    result = inspect_managed_store("vs_test", SimpleNamespace(vector_stores=stores, files=SimpleNamespace(list=lambda purpose: [remote_file])))
    assert result["attached_files"][0]["id"] == "file-indexed"
    assert result["unattached_uploaded_files"][0]["filename"] == "report.pdf"
    assert "raw embedding" in result["embedding_visibility"].lower()
