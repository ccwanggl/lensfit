"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from lensfit.api.server import app
from lensfit.db.models import Base, DetectorCatalog, LensCatalog, Manufacturer
from lensfit.domains.infrared import InfraredModule
from lensfit.domains.microscope import MicroscopyModule
from lensfit.domains.photography import PhotographyModule

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
    server_module._engine.register_domain(MicroscopyModule())
    server_module._engine.register_domain(InfraredModule())
    server_module._engine.register_domain(PhotographyModule())
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


def _seed_domain_catalog(session, domain: str):
    """Insert a minimal lens+detector pair for the given domain."""
    from lensfit.db.models import DetectorCatalog, LensCatalog, Manufacturer

    mfg = Manufacturer(name=f"TestMfg-{domain}")
    session.add(mfg)
    session.flush()

    if domain == "industrial":
        lens = LensCatalog(
            manufacturer_id=mfg.id,
            model="FA-25mm",
            category="fa",
            focal_length_mm=25,
            max_aperture=2.8,
            image_circle_mm=11,
            mount_type="C-mount",
            price_usd=299,
        )
        det = DetectorCatalog(
            manufacturer_id=mfg.id,
            model="IMX-2/3",
            category="industrial",
            sensor_format_inch="2/3",
            sensor_w_mm=8.45,
            sensor_h_mm=7.07,
            sensor_diag_mm=11.0,
            resolution_w=2448,
            resolution_h=2048,
            pixel_size_um=3.45,
            mount_type="C-mount",
            price_usd=199,
        )
    elif domain == "photography":
        lens = LensCatalog(
            manufacturer_id=mfg.id,
            model="Photo-50mm",
            category="photography",
            focal_length_mm=50,
            max_aperture=1.8,
            image_circle_mm=44,
            mount_type="E-mount",
            price_usd=499,
        )
        det = DetectorCatalog(
            manufacturer_id=mfg.id,
            model="FullFrame-24MP",
            category="photography",
            sensor_format_inch="FF",
            sensor_w_mm=36,
            sensor_h_mm=24,
            sensor_diag_mm=43.27,
            resolution_w=6000,
            resolution_h=4000,
            pixel_size_um=5.0,
            mount_type="E-mount",
            price_usd=999,
        )
    elif domain == "microscope":
        lens = LensCatalog(
            manufacturer_id=mfg.id,
            model="Micro-20x",
            category="microscope",
            focal_length_mm=20,
            max_aperture=0.65,
            image_circle_mm=20,
            na=0.65,
            price_usd=999,
        )
        det = DetectorCatalog(
            manufacturer_id=mfg.id,
            model="MicroCam-5M",
            category="microscope",
            sensor_format_inch="2/3",
            sensor_w_mm=8.45,
            sensor_h_mm=7.07,
            sensor_diag_mm=11.0,
            resolution_w=2448,
            resolution_h=2048,
            pixel_size_um=3.45,
            price_usd=499,
        )
    else:  # infrared
        lens = LensCatalog(
            manufacturer_id=mfg.id,
            model="IR-25mm",
            category="infrared",
            focal_length_mm=25,
            max_aperture=1.4,
            image_circle_mm=16,
            wavelength_min_nm=8000,
            wavelength_max_nm=14000,
            price_usd=1999,
        )
        det = DetectorCatalog(
            manufacturer_id=mfg.id,
            model="IR-640",
            category="infrared",
            sensor_format_inch="1/2",
            sensor_w_mm=6.4,
            sensor_h_mm=4.8,
            sensor_diag_mm=8.0,
            resolution_w=640,
            resolution_h=512,
            pixel_size_um=12,
            price_usd=999,
        )

    session.add(lens)
    session.add(det)
    session.commit()


def _poll_match_result(client, auth_headers, task_id: str):
    for _ in range(50):
        resp = client.get(f"/api/v1/match/async/{task_id}", headers=auth_headers)
        assert resp.status_code == 200
        status = resp.json()
        if status["status"] == "completed":
            break
        if status["status"] == "failed":
            pytest.fail(f"Match failed: {status.get('error')}")
    else:
        pytest.fail("Match did not complete in time")

    resp = client.get(f"/api/v1/match/async/{task_id}/result", headers=auth_headers)
    assert resp.status_code == 200
    return resp.json()


@pytest.mark.parametrize(
    "domain,requirements",
    [
        (
            "industrial",
            {
                "sensor_size": "2/3",
                "pixel_size_um": 3.45,
                "target_width_mm": 50,
                "target_height_mm": 40,
                "working_distance_mm": 200,
                "lens_type": "FA",
                "interface": "C-mount",
            },
        ),
        (
            "photography",
            {
                "purpose": "portrait",
                "sensor_format": "FF",
                "lens_type": "prime",
                "mount": "E-mount",
                "budget_usd": 3000,
                "max_aperture": 2.8,
            },
        ),
        (
            "microscope",
            {
                "microscope_type": "compound",
                "objective_na": 0.65,
                "magnification": 20,
                "wavelength_nm": 550,
                "sensor_format": "2/3",
                "pixel_size_um": 3.45,
                "application": "biology",
                "budget_usd": 5000,
            },
        ),
        (
            "infrared",
            {
                "band": "lwir",
                "focal_length_mm": 25,
                "f_number": 1.4,
                "sensor_format": "1/2",
                "pixel_size_um": 12,
                "working_distance_m": 10,
                "budget_usd": 5000,
            },
        ),
    ],
)
def test_match_regression_all_domains(client, auth_headers, domain, requirements):
    import lensfit.api.server as server_module

    with server_module._session_maker() as session:
        _seed_domain_catalog(session, domain)

    resp = client.post(
        "/api/v1/match/async",
        json={"domain": domain, "requirements": requirements},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    task = resp.json()
    result = _poll_match_result(client, auth_headers, task["task_id"])
    assert len(result.get("top_matches", [])) > 0, f"{domain} should return at least one match"


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


def test_manufacturer_create_and_list(client, auth_headers):
    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "AcmeOptics"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    mfg = resp.json()
    assert mfg["name"] == "AcmeOptics"

    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "AcmeOptics"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    resp = client.get("/api/v1/catalog/manufacturers", headers=auth_headers)
    assert resp.status_code == 200
    assert any(item["name"] == "AcmeOptics" for item in resp.json()["items"])


def test_lens_crud(client, auth_headers):
    # Create manufacturer
    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "LensMfg"},
        headers=auth_headers,
    )
    mfg_id = resp.json()["id"]

    # Create lens
    resp = client.post(
        "/api/v1/catalog/lenses",
        json={
            "manufacturer_id": mfg_id,
            "model": "LM-25mm",
            "category": "industrial",
            "focal_length_mm": 25,
            "max_aperture": 2.8,
            "image_circle_mm": 11,
            "mount_type": "C",
            "price_usd": 299,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    lens = resp.json()
    assert lens["model"] == "LM-25mm"
    assert lens["data_source"] == "user"

    # Get
    resp = client.get(f"/api/v1/catalog/lenses/{lens['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["model"] == "LM-25mm"

    # Update
    resp = client.put(
        f"/api/v1/catalog/lenses/{lens['id']}",
        json={"price_usd": 399},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["price_usd"] == 399

    # Delete
    resp = client.delete(f"/api/v1/catalog/lenses/{lens['id']}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/catalog/lenses/{lens['id']}", headers=auth_headers)
    assert resp.status_code == 404


def test_list_lenses_search_and_pagination(client, auth_headers):
    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "SearchMfg"},
        headers=auth_headers,
    )
    mfg_id = resp.json()["id"]

    for i in range(3):
        client.post(
            "/api/v1/catalog/lenses",
            json={
                "manufacturer_id": mfg_id,
                "model": f"SearchLens-{i}",
                "category": "industrial",
                "focal_length_mm": 25 + i,
                "max_aperture": 2.8,
                "image_circle_mm": 11,
                "mount_type": "C",
                "price_usd": 100 + i,
            },
            headers=auth_headers,
        )

    resp = client.get("/api/v1/catalog/lenses?q=SearchLens-1&limit=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

    resp = client.get("/api/v1/catalog/lenses?limit=2&skip=0", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2

    resp = client.get("/api/v1/catalog/lenses?limit=2&skip=2", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1


def test_detector_crud(client, auth_headers):
    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "DetMfg"},
        headers=auth_headers,
    )
    mfg_id = resp.json()["id"]

    resp = client.post(
        "/api/v1/catalog/detectors",
        json={
            "manufacturer_id": mfg_id,
            "model": "DM-5M",
            "category": "industrial",
            "sensor_format_inch": "1/1.8",
            "resolution_w": 2592,
            "resolution_h": 1944,
            "pixel_size_um": 2.2,
            "mount_type": "C",
            "price_usd": 199,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    det = resp.json()
    assert det["model"] == "DM-5M"

    resp = client.put(
        f"/api/v1/catalog/detectors/{det['id']}",
        json={"pixel_size_um": 2.5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["pixel_size_um"] == 2.5

    resp = client.delete(f"/api/v1/catalog/detectors/{det['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_create_duplicate_lens_returns_409(client, auth_headers):
    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "DupLensMfg"},
        headers=auth_headers,
    )
    mfg_id = resp.json()["id"]

    payload = {
        "manufacturer_id": mfg_id,
        "model": "DupLens-25mm",
        "category": "industrial",
        "focal_length_mm": 25,
        "max_aperture": 2.8,
        "image_circle_mm": 11,
        "mount_type": "C",
        "price_usd": 299,
    }
    resp = client.post("/api/v1/catalog/lenses", json=payload, headers=auth_headers)
    assert resp.status_code == 201

    resp = client.post("/api/v1/catalog/lenses", json=payload, headers=auth_headers)
    assert resp.status_code == 409


def test_create_duplicate_detector_returns_409(client, auth_headers):
    resp = client.post(
        "/api/v1/catalog/manufacturers",
        json={"name": "DupDetMfg"},
        headers=auth_headers,
    )
    mfg_id = resp.json()["id"]

    payload = {
        "manufacturer_id": mfg_id,
        "model": "DupDet-5M",
        "category": "industrial",
        "sensor_format_inch": "1/1.8",
        "resolution_w": 2592,
        "resolution_h": 1944,
        "pixel_size_um": 2.2,
        "mount_type": "C",
        "price_usd": 199,
    }
    resp = client.post("/api/v1/catalog/detectors", json=payload, headers=auth_headers)
    assert resp.status_code == 201

    resp = client.post("/api/v1/catalog/detectors", json=payload, headers=auth_headers)
    assert resp.status_code == 409


def test_import_lenses_csv(client, auth_headers):
    import io

    csv_content = (
        "manufacturer_name,model,category,focal_length_mm,max_aperture,"
        "image_circle_mm,mount_type,nominal_wd_mm,price_usd\n"
        "ImportMfg,IM-35mm,industrial,35,2.8,17,C,150,399\n"
        "ImportMfg,IM-50mm,industrial,50,2.8,22,C,200,499\n"
    )
    resp = client.post(
        "/api/v1/catalog/import",
        files={"file": ("lenses_import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["kind"] == "lenses"
    assert data["inserted"] == 2
    assert data["skipped"] == 0

    # Duplicate import should skip
    resp = client.post(
        "/api/v1/catalog/import",
        files={"file": ("lenses_import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["inserted"] == 0
    assert data["skipped"] == 2


def test_import_lenses_csv_rejects_invalid_manufacturer_id(client, auth_headers):
    import io

    csv_content = (
        "manufacturer_id,model,category,focal_length_mm,max_aperture,"
        "image_circle_mm,mount_type,nominal_wd_mm,price_usd\n"
        "999999,IM-35mm,industrial,35,2.8,17,C,150,399\n"
    )
    resp = client.post(
        "/api/v1/catalog/import",
        files={"file": ("lenses_import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["inserted"] == 0
    assert any("manufacturer_id 999999 does not exist" in err for err in data["errors"])


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
