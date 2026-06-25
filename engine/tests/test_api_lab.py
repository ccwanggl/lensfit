"""API tests for /api/v1/lab endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from lensfit.api import server as server_module
from lensfit.api.server import app


@pytest.fixture
def client():
    """Create a TestClient with DB/API key patching."""
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

    with TestClient(app) as c:
        yield c

    server_module._session_maker = original_session_maker
    server_module._engine = original_engine
    server_module._API_KEY = original_api_key


def test_list_experiments(client: TestClient):
    res = client.get("/api/v1/lab/experiments")
    assert res.status_code == 200
    data = res.json()
    ids = {item["id"] for item in data["items"]}
    assert "thin-lens" in ids
    assert "diffraction" in ids
    assert "color-mixing" in ids
    assert "sensor-coverage" in ids


def test_get_experiment(client: TestClient):
    res = client.get("/api/v1/lab/experiments/thin-lens")
    assert res.status_code == 200
    item = res.json()["items"][0]
    assert item["id"] == "thin-lens"
    assert item["parameters"]


def test_get_unknown_experiment(client: TestClient):
    res = client.get("/api/v1/lab/experiments/unknown")
    assert res.status_code == 404


def test_run_experiment(client: TestClient):
    res = client.post(
        "/api/v1/lab/experiments/thin-lens/run",
        json={"params": {"focal_length": 50, "object_distance": 100, "object_height": 30}},
    )
    assert res.status_code == 200
    result = res.json()
    assert result["data"]["image_distance_mm"] == pytest.approx(100.0, rel=1e-3)
    assert result["svg"]
    assert isinstance(result["warnings"], list)


def test_run_experiment_validation_error(client: TestClient):
    res = client.post(
        "/api/v1/lab/experiments/thin-lens/run",
        json={"params": {"focal_length": "not-a-number"}},
    )
    assert res.status_code == 422


def test_run_unknown_experiment(client: TestClient):
    res = client.post("/api/v1/lab/experiments/unknown/run", json={"params": {}})
    assert res.status_code == 404
