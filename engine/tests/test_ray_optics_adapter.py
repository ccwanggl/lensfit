"""Tests for the SceneGraph -> ray-optics adapter.

These tests live next to the existing ray-optics contract tests. They verify
that the adapter produces valid scenes, keeps SceneGraph v1 neutral, and
gracefully integrates with the workbench solver.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest

from lensfit.lab.workbench import SceneGraph
from lensfit.lab.workbench.ray_optics_adapter import (
    run_ray_optics,
    to_ray_optics_scene,
)
from lensfit.lab.workbench.ray_optics_sidecar import (
    RayOpticsNotAvailableError,
    RayOpticsSidecar,
)
from lensfit.lab.workbench.solver import WorkbenchSolver

NODE_AVAILABLE = shutil.which("node") is not None
CANVAS_AVAILABLE = NODE_AVAILABLE and (
    Path(__file__).resolve().parents[1]
    / "third_party"
    / "ray-optics"
    / "node_modules"
    / "canvas"
    / "package.json"
).exists()


def _single_slit_scene(
    *,
    slit_width_um: float = 50.0,
    wavelength_nm: float = 550.0,
    screen_x_mm: float = 1100.0,
) -> SceneGraph:
    return SceneGraph.model_validate(
        {
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
                    "transform": {
                        "x_mm": screen_x_mm,
                        "y_mm": 0,
                        "rotation_deg": 0,
                    },
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
    )


def _double_slit_scene(
    *,
    slit_width_um: float = 20.0,
    slit_separation_um: float = 100.0,
    wavelength_nm: float = 550.0,
    screen_x_mm: float = 1100.0,
) -> SceneGraph:
    return SceneGraph.model_validate(
        {
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
                    "transform": {
                        "x_mm": screen_x_mm,
                        "y_mm": 0,
                        "rotation_deg": 0,
                    },
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
    )


def _assert_no_external_references(scene: dict[str, Any]) -> None:
    """Recursively fail if any string looks like a path or URL."""
    stack = [scene]
    dangerous = ("file://", "http://", "https://", "\\", "/")
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str):
            for token in dangerous:
                assert token not in item, f"possible path/URL in scene: {item!r}"


def test_adapter_generates_valid_single_slit_scene():
    scene = _single_slit_scene()
    ro_scene = to_ray_optics_scene(scene)

    assert ro_scene["version"] == 5
    assert "rayModeDensity" in ro_scene
    _assert_no_external_references(ro_scene)

    types = {obj["type"] for obj in ro_scene["objs"]}
    assert types == {"PointSource", "Blocker", "Detector"}


def test_adapter_generates_valid_double_slit_scene():
    scene = _double_slit_scene()
    ro_scene = to_ray_optics_scene(scene)

    assert ro_scene["version"] == 5
    _assert_no_external_references(ro_scene)

    types = {obj["type"] for obj in ro_scene["objs"]}
    assert types == {"PointSource", "Blocker", "Detector"}


def test_adapter_omits_cropbox_by_default_even_when_canvas_available():
    scene = _single_slit_scene()
    ro_scene = to_ray_optics_scene(scene)
    has_cropbox = any(obj.get("type") == "CropBox" for obj in ro_scene["objs"])
    assert not has_cropbox, "CropBox should be opt-in"


def test_adapter_includes_cropbox_when_explicitly_requested():
    scene = _single_slit_scene()
    ro_scene = to_ray_optics_scene(scene, include_image=True)
    has_cropbox = any(obj.get("type") == "CropBox" for obj in ro_scene["objs"])
    if CANVAS_AVAILABLE:
        assert has_cropbox, "CropBox should be added when include_image=True and node-canvas is installed"
    else:
        assert not has_cropbox, "CropBox should be omitted when node-canvas is absent"


def test_scenegraph_fixture_remains_neutral():
    """SceneGraph v1 must not contain any ray-optics type names."""
    scene = _single_slit_scene()
    json_text = scene.model_dump_json()
    ray_optics_types = {
        "PointSource",
        "Blocker",
        "Detector",
        "SingleRay",
        "CropBox",
    }
    for token in ray_optics_types:
        assert token not in json_text, f"SceneGraph fixture contains {token}"


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js not available")
def test_single_slit_runs_and_normalizes_without_image_by_default():
    scene = _single_slit_scene()
    data = run_ray_optics(scene)

    assert data["available"] is True
    samples = data["samples"]
    assert len(samples) > 0
    assert all(0.0 <= s["intensity"] <= 1.0 for s in samples)
    assert data["power"] > 0
    assert data["image"] is None


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js not available")
def test_double_slit_runs_and_normalizes_without_image_by_default():
    scene = _double_slit_scene()
    data = run_ray_optics(scene)

    assert data["available"] is True
    samples = data["samples"]
    assert len(samples) > 0
    assert all(0.0 <= s["intensity"] <= 1.0 for s in samples)
    assert data["power"] > 0
    assert data["image"] is None


@pytest.mark.skipif(
    not NODE_AVAILABLE or not CANVAS_AVAILABLE,
    reason="Node.js / node-canvas not available",
)
def test_single_slit_image_is_generated_when_requested():
    scene = _single_slit_scene()
    data = run_ray_optics(scene, include_image=True)

    assert data["available"] is True
    assert data["image"] is not None
    assert data["image"].startswith("data:image/png;base64,")


@pytest.mark.skipif(
    not NODE_AVAILABLE or not CANVAS_AVAILABLE,
    reason="Node.js / node-canvas not available",
)
def test_double_slit_image_is_generated_when_requested():
    scene = _double_slit_scene()
    data = run_ray_optics(scene, include_image=True)

    assert data["available"] is True
    assert data["image"] is not None
    assert data["image"].startswith("data:image/png;base64,")


def test_solver_does_not_run_ray_optics_by_default():
    solver = WorkbenchSolver()
    result = solver.solve(_single_slit_scene())

    assert "ray_optics" not in result.data
    assert not any("ray-optics" in w for w in result.warnings)


@pytest.mark.skipif(
    not NODE_AVAILABLE or not CANVAS_AVAILABLE,
    reason="Node.js / node-canvas not available",
)
def test_solver_includes_ray_image_when_requested():
    solver = WorkbenchSolver()
    result = solver.solve(_single_slit_scene(), include_ray_image=True)

    assert "ray_optics" in result.data
    assert result.data["ray_optics"]["available"] is True
    assert result.data["ray_optics"]["image"] is not None
    assert result.data["ray_optics"]["image"].startswith("data:image/png;base64,")


def test_solver_gracefully_handles_missing_ray_optics(monkeypatch):
    def _raise_not_available(*args, **kwargs):
        raise RayOpticsNotAvailableError("node missing for test")

    monkeypatch.setattr(
        "lensfit.lab.workbench.solver.run_ray_optics", _raise_not_available
    )

    solver = WorkbenchSolver()
    result = solver.solve(_single_slit_scene(), include_ray_image=True)

    assert result.data["ray_optics"]["available"] is False
    assert "node missing for test" in result.data["ray_optics"]["error"]
    assert any("ray-optics" in w for w in result.warnings)
