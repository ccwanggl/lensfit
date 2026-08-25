"""API tests for /api/v1/content endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from optibench.api import server as server_module
from optibench.api.server import app
from optibench.content.loader import reset_content_index


@pytest.fixture
def client():
    """Create a TestClient with DB/API key patching (mirrors test_api_lab.py)."""
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    db_engine = sqlalchemy.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_maker = sessionmaker(bind=db_engine)

    original_session_maker = getattr(server_module, "_session_maker", None)
    original_engine = getattr(server_module, "_engine", None)
    original_api_key = getattr(server_module, "_API_KEY", None)

    server_module._session_maker = session_maker
    server_module._engine = None
    server_module._API_KEY = "test-key"

    app.state.mode = "dev"  # bypass API key verification

    reset_content_index()
    with TestClient(app) as c:
        yield c
    reset_content_index()

    server_module._session_maker = original_session_maker
    server_module._engine = original_engine
    server_module._API_KEY = original_api_key


def test_list_concepts(client: TestClient):
    res = client.get("/api/v1/content/concepts")
    assert res.status_code == 200
    data = res.json()
    ids = {item["id"] for item in data["items"]}
    assert "cmos-fundamentals" in ids
    assert "cmos-spectral-response" in ids
    assert data["errors"] == []
    # List items carry metadata but no body.
    for item in data["items"]:
        assert "body" not in item
        assert item["module"]
        assert item["difficulty"] in ("foundation", "intermediate", "advanced")


def test_get_concept(client: TestClient):
    res = client.get("/api/v1/content/concepts/cmos-fundamentals")
    assert res.status_code == 200
    item = res.json()
    assert item["id"] == "cmos-fundamentals"
    assert item["title"] == "CMOS Image Sensor 基础"
    assert item["module"] == "20-geometric-optics"
    assert item["linked_experiments"] == ["sensor-coverage"]
    assert item["body"].startswith("## 前言")


def test_get_concept_not_found(client: TestClient):
    res = client.get("/api/v1/content/concepts/does-not-exist")
    assert res.status_code == 404
