"""API tests for /api/v1/lab/workbench/run."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from lensfit.api import server as server_module
from lensfit.api.server import app
from lensfit.lab import get_registry


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


def _scene(
    *,
    slit_width_um: float = 50.0,
    wavelength_nm: float = 550.0,
    screen_x_mm: float = 1100.0,
):
    return {
        "version": 1,
        "components": [
            {
                "id": "laser-1",
                "spec_id": "laser-monochrome",
                "category": "source",
                "transform": {"x_mm": 0, "y_mm": 0, "rotation_deg": 0},
                "params": {"wavelength_nm": wavelength_nm},
            },
            {
                "id": "slit-1",
                "spec_id": "single-slit",
                "category": "aperture",
                "transform": {"x_mm": 100, "y_mm": 0, "rotation_deg": 0},
                "params": {"slit_width_um": slit_width_um},
            },
            {
                "id": "screen-1",
                "spec_id": "screen",
                "category": "screen",
                "transform": {"x_mm": screen_x_mm, "y_mm": 0, "rotation_deg": 0},
                "params": {},
            },
        ],
        "observables": [
            {
                "type": "fraunhofer_intensity",
                "source_id": "laser-1",
                "aperture_id": "slit-1",
                "screen_id": "screen-1",
            }
        ],
    }


def test_workbench_run_default_scene(client: TestClient):
    res = client.post("/api/v1/lab/workbench/run", json={"scene": _scene()})
    assert res.status_code == 200
    result = res.json()
    assert result["svg"]
    assert isinstance(result["warnings"], list)

    baseline = get_registry().run("single-slit-diffraction", {})
    assert result["data"]["central_max_width_mm"] == pytest.approx(
        baseline.data["central_max_width_mm"]
    )


def test_workbench_slit_width_decreases_central_max(client: TestClient):
    narrow = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(slit_width_um=20.0)},
    ).json()
    wide = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(slit_width_um=100.0)},
    ).json()
    assert narrow["data"]["central_max_width_mm"] > wide["data"]["central_max_width_mm"]


def test_workbench_wavelength_increases_central_max(client: TestClient):
    blue = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(wavelength_nm=450.0)},
    ).json()
    red = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(wavelength_nm=650.0)},
    ).json()
    assert red["data"]["central_max_width_mm"] > blue["data"]["central_max_width_mm"]


def test_workbench_distance_doubles_first_min(client: TestClient):
    near = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(screen_x_mm=1100.0)},
    ).json()
    far = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(screen_x_mm=2100.0)},
    ).json()
    assert far["data"]["first_min_position_mm"] == pytest.approx(
        2 * near["data"]["first_min_position_mm"], rel=1e-3
    )


def test_workbench_invalid_scene_returns_422(client: TestClient):
    payload = _scene()
    payload["components"] = [
        c for c in payload["components"] if c["category"] != "screen"
    ]
    res = client.post("/api/v1/lab/workbench/run", json={"scene": payload})
    assert res.status_code == 422


def test_workbench_fraunhofer_warning(client: TestClient):
    # screen at 110 mm -> distance 0.01 m, far below Fraunhofer condition
    res = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _scene(screen_x_mm=110.0)},
    )
    assert res.status_code == 200
    result = res.json()
    assert any("夫琅禾费" in w for w in result["warnings"])


def _double_slit_scene(
    *,
    slit_width_um: float = 20.0,
    slit_separation_um: float = 100.0,
    wavelength_nm: float = 550.0,
    screen_x_mm: float = 1100.0,
):
    return {
        "version": 1,
        "components": [
            {
                "id": "laser-1",
                "spec_id": "laser-monochrome",
                "category": "source",
                "transform": {"x_mm": 0, "y_mm": 0, "rotation_deg": 0},
                "params": {"wavelength_nm": wavelength_nm},
            },
            {
                "id": "slit-1",
                "spec_id": "double-slit",
                "category": "aperture",
                "transform": {"x_mm": 100, "y_mm": 0, "rotation_deg": 0},
                "params": {
                    "slit_width_um": slit_width_um,
                    "slit_separation_um": slit_separation_um,
                },
            },
            {
                "id": "screen-1",
                "spec_id": "screen",
                "category": "screen",
                "transform": {"x_mm": screen_x_mm, "y_mm": 0, "rotation_deg": 0},
                "params": {},
            },
        ],
        "observables": [
            {
                "type": "fraunhofer_intensity",
                "source_id": "laser-1",
                "aperture_id": "slit-1",
                "screen_id": "screen-1",
            }
        ],
    }


def test_workbench_double_slit_runs(client: TestClient):
    res = client.post(
        "/api/v1/lab/workbench/run", json={"scene": _double_slit_scene()}
    )
    assert res.status_code == 200
    result = res.json()
    assert result["svg"]
    assert result["data"]["fringe_spacing_mm"] > 0


def test_workbench_double_slit_separation_decreases_fringe_spacing(client: TestClient):
    close = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _double_slit_scene(slit_separation_um=200.0)},
    ).json()
    far = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _double_slit_scene(slit_separation_um=50.0)},
    ).json()
    assert close["data"]["fringe_spacing_mm"] < far["data"]["fringe_spacing_mm"]


def test_workbench_double_slit_distance_increases_fringe_spacing(client: TestClient):
    near = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _double_slit_scene(screen_x_mm=1100.0)},
    ).json()
    far = client.post(
        "/api/v1/lab/workbench/run",
        json={"scene": _double_slit_scene(screen_x_mm=2100.0)},
    ).json()
    assert far["data"]["fringe_spacing_mm"] == pytest.approx(
        2 * near["data"]["fringe_spacing_mm"], rel=1e-3
    )


def test_workbench_double_slit_invalid_returns_422(client: TestClient):
    payload = _double_slit_scene()
    payload["components"] = [
        c for c in payload["components"] if c["category"] != "screen"
    ]
    res = client.post("/api/v1/lab/workbench/run", json={"scene": payload})
    assert res.status_code == 422
