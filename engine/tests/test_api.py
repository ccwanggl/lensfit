"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from lensfit.api.server import app
from lensfit.db.models import Base, DetectorCatalog, LensCatalog, Manufacturer

TEST_API_KEY = "test-api-key"


@pytest.fixture
def sample_catalog_items(client):
    """Insert a lens and detector into the in-memory DB for visualization tests."""
    import lensfit.api.server as server_module

    with server_module._session_maker() as session:
        mfg = Manufacturer(name="TestOptics", name_en="TestOptics")
        session.add(mfg)
        session.flush()

        lens = LensCatalog(
            manufacturer_id=mfg.id,
            model="Test Lens 50mm",
            category="photography",
            focal_length_mm=50.0,
            max_aperture=1.8,
            image_circle_mm=44.0,
            mtf50_lpmm=60.0,
            price_usd=500.0,
        )
        det = DetectorCatalog(
            manufacturer_id=mfg.id,
            model="Test Sensor",
            category="photography",
            sensor_w_mm=36.0,
            sensor_h_mm=24.0,
            sensor_diag_mm=43.27,
            pixel_size_um=5.0,
            resolution_w=6000,
            resolution_h=4000,
            price_usd=1000.0,
        )
        session.add(lens)
        session.add(det)
        session.commit()
        return {"lens_id": lens.id, "detector_id": det.id}


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
    setup_id = setup["id"]

    # List setups
    resp = client.get(f"/api/v1/projects/{proj_id}/setups", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1

    # Delete setup
    resp = client.delete(f"/api/v1/projects/{proj_id}/setups/{setup_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    resp = client.get(f"/api/v1/projects/{proj_id}/setups", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 0

    # Delete project
    resp = client.delete(f"/api/v1/projects/{proj_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    resp = client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200
    assert all(p["id"] != proj_id for p in resp.json()["items"])


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


def test_export_csv(client, auth_headers):
    resp = client.post(
        "/api/v1/export",
        json={
            "format": "csv",
            "requirements": {"sensor_size": "2/3", "working_distance_mm": 200},
            "results": [],
            "top_k": 5,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "text/csv; charset=utf-8"
    content = resp.content.decode("utf-8-sig")
    assert "LensFit" in content
    assert "排名" in content


def test_visualize_mtf(client, auth_headers, sample_catalog_items):
    resp = client.post(
        "/api/v1/visualize/mtf",
        json={
            "lens_id": sample_catalog_items["lens_id"],
            "detector_id": sample_catalog_items["detector_id"],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "points" in data
    assert data["lens_mtf50_lpmm"] == 60.0
    assert data["detector_nyquist_lpmm"] is not None
    assert len(data["points"]) > 0
    assert all("frequency_lpmm" in p and "mtf" in p for p in data["points"])


def test_visualize_coc(client, auth_headers, sample_catalog_items):
    resp = client.post(
        "/api/v1/visualize/coc",
        json={
            "lens_id": sample_catalog_items["lens_id"],
            "detector_id": sample_catalog_items["detector_id"],
            "focus_distance_m": 2.0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "coc_mm" in data
    assert "apertures" in data
    assert len(data["apertures"]) > 0
    first = data["apertures"][0]
    assert "hyperfocal_m" in first
    assert "near_limit_m" in first
