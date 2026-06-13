"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from lensfit.api.server import app
from lensfit.db.models import Base

TEST_API_KEY = "test-api-key"


@pytest.fixture
def client():
    """Create a test client with an in-memory database."""
    # Use StaticPool so all connections share the same in-memory DB
    db_url = "sqlite:///:memory:"
    engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    # Override lifespan to use in-memory db
    import lensfit.api.server as server_module

    server_module._session_maker = session_factory
    from lensfit.domains.industrial import IndustrialVisionModule
    from lensfit.matching.engine import MatchingEngine

    server_module._engine = MatchingEngine(session_factory)
    server_module._engine.register_domain(IndustrialVisionModule())
    server_module._API_KEY = TEST_API_KEY

    with TestClient(app) as c:
        yield c

    # Cleanup
    server_module._engine = None
    server_module._session_maker = None


@pytest.fixture
def auth_headers():
    """Return API key headers for authenticated requests."""
    return {"X-API-Key": TEST_API_KEY}


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_calculate(client, auth_headers):
    resp = client.post(
        "/api/v1/calculate",
        json={"working_distance": 200, "sensor_w": 8.8, "fov_w": 50},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "focal_length" in data
    assert data["focal_length"] == pytest.approx(29.93, rel=0.01)


def test_match_async_and_poll(client, auth_headers):
    resp = client.post(
        "/api/v1/match/async",
        json={
            "domain": "industrial",
            "requirements": {
                "sensor_size": "2/3",
                "pixel_size_um": 3.45,
                "target_width_mm": 50,
                "target_height_mm": 40,
                "working_distance_mm": 200,
                "lens_type": "FA",
                "interface": "C-mount",
            },
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    task = resp.json()
    assert "task_id" in task
    assert task["status"] in ("pending", "running")

    # Poll until completion or timeout
    for _ in range(50):
        resp = client.get(f"/api/v1/match/async/{task['task_id']}", headers=auth_headers)
        assert resp.status_code == 200
        status = resp.json()
        if status["status"] == "completed":
            break
        if status["status"] == "failed":
            pytest.fail(f"Match failed: {status.get('error')}")
    else:
        pytest.fail("Match did not complete in time")

    # Get results
    resp = client.get(f"/api/v1/match/async/{task['task_id']}/result", headers=auth_headers)
    assert resp.status_code == 200
    result = resp.json()
    assert "top_matches" in result


def test_list_lenses_empty(client, auth_headers):
    resp = client.get("/api/v1/catalog/lenses?limit=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_detectors_empty(client, auth_headers):
    resp = client.get("/api/v1/catalog/detectors?limit=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_project_crud(client, auth_headers):
    # Create
    resp = client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "domain": "industrial"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    proj = resp.json()
    assert proj["name"] == "Test Project"
    assert proj["domain"] == "industrial"
    proj_id = proj["id"]

    # List
    resp = client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) >= 1

    # Create setup
    resp = client.post(
        f"/api/v1/projects/{proj_id}/setups",
        json={"name": "Setup 1", "lens_id": None, "detector_id": None},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    setup = resp.json()
    assert setup["name"] == "Setup 1"

    # List setups
    resp = client.get(f"/api/v1/projects/{proj_id}/setups", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


def test_export_pdf(client, auth_headers):
    resp = client.post(
        "/api/v1/export",
        json={
            "format": "pdf",
            "requirements": {"sensor_size": "2/3", "working_distance_mm": 200},
            "results": [],
            "top_k": 5,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 500


def test_export_excel(client, auth_headers):
    resp = client.post(
        "/api/v1/export",
        json={
            "format": "excel",
            "requirements": {"sensor_size": "2/3", "working_distance_mm": 200},
            "results": [],
            "top_k": 5,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.content) > 500


def test_export_invalid_format(client, auth_headers):
    resp = client.post(
        "/api/v1/export",
        json={
            "format": "docx",
            "requirements": {},
            "results": [],
            "top_k": 5,
        },
        headers=auth_headers,
    )
    # FastAPI/Pydantic v2 returns 422 for enum validation errors
    assert resp.status_code == 422
