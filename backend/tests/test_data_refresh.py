from fastapi.testclient import TestClient

from app.data_refresh import _world_bank_rows
from app.main import app
from app.settings import settings

client = TestClient(app)


def _headers(csrf: bool = True):
    headers = {"X-Admin-Token": settings.admin_token}
    if csrf:
        headers["X-CSRF-Token"] = settings.admin_token
    return headers


def test_world_bank_rows_keep_scope_and_missingness():
    page = [{"pages": 1}, [
        {"countryiso3code": "IND", "date": "2023", "value": 7.2},
        {"countryiso3code": "IND", "date": "2022", "value": None},
        {"countryiso3code": "USA", "date": "2023", "value": 5.0},
    ]]
    rows, missing = _world_bank_rows(page, "NY.GDP.MKTP.KD.ZG", {"IND"}, 2022, 2023)
    assert rows == [("IND", "NY.GDP.MKTP.KD.ZG", 2023, 7.2)]
    assert missing == 1


def test_refresh_requires_owner_and_csrf():
    assert client.post("/api/admin/refresh-data", json={}).status_code == 401
    assert client.post("/api/admin/refresh-data", json={}, headers=_headers(False)).status_code == 403


def test_refresh_rejects_out_of_scope_before_network():
    result = client.post("/api/admin/refresh-data", json={"countries": ["XXX"]}, headers=_headers())
    assert result.status_code == 400


def test_clean_preview_makes_no_model_call():
    result = client.post("/api/admin/clean-data", json={"countries": ["IND"]}, headers=_headers())
    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "preview_only"
    assert body["model_status"] == "disabled"
    assert body["estimated_cost_usd"] == 0
    assert body["observations_checked"] > 0


def test_model_cleaning_fails_closed_without_cost_budget():
    result = client.post("/api/admin/clean-data", json={"mode": "model"}, headers=_headers())
    assert result.status_code == 503
    assert "not enabled" in result.json()["detail"] or "cost budget" in result.json()["detail"]
