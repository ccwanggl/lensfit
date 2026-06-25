"""Tests for SceneGraph v1 contract."""

from __future__ import annotations

import pytest

from lensfit.lab.workbench import CATALOG, SceneGraph


def _minimal_scene(
    *,
    laser_x: float = 0.0,
    slit_x: float = 100.0,
    screen_x: float = 1100.0,
    slit_width_um: float = 50.0,
    wavelength_nm: float = 550.0,
    rotation_deg: float = 0.0,
):
    return {
        "version": 1,
        "components": [
            {
                "id": "laser-1",
                "spec_id": "laser-monochrome",
                "category": "source",
                "transform": {"x_mm": laser_x, "y_mm": 0, "rotation_deg": rotation_deg},
                "params": {"wavelength_nm": wavelength_nm},
            },
            {
                "id": "slit-1",
                "spec_id": "single-slit",
                "category": "aperture",
                "transform": {"x_mm": slit_x, "y_mm": 0, "rotation_deg": 0},
                "params": {"slit_width_um": slit_width_um},
            },
            {
                "id": "screen-1",
                "spec_id": "screen",
                "category": "screen",
                "transform": {"x_mm": screen_x, "y_mm": 0, "rotation_deg": 0},
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


def test_valid_scene_parses():
    scene = SceneGraph.model_validate(_minimal_scene())
    assert scene.version == 1
    assert scene.units.length == "mm"
    assert len(scene.components) == 3
    assert len(scene.observables) == 1
    assert scene.screen_distance_m() == pytest.approx(1.0)


def test_default_params_merged():
    scene = SceneGraph.model_validate(_minimal_scene())
    assert scene.params_for("laser-1")["wavelength_nm"] == 550.0
    assert scene.params_for("slit-1")["slit_width_um"] == 50.0
    assert scene.params_for("screen-1") == {}


def test_overridden_params_take_precedence():
    scene = SceneGraph.model_validate(
        _minimal_scene(slit_width_um=100.0, wavelength_nm=650.0)
    )
    assert scene.params_for("slit-1")["slit_width_um"] == 100.0
    assert scene.params_for("laser-1")["wavelength_nm"] == 650.0


def test_missing_component_fails():
    payload = _minimal_scene()
    payload["components"] = [c for c in payload["components"] if c["category"] != "screen"]
    with pytest.raises(ValueError, match="exactly one screen component"):
        SceneGraph.model_validate(payload)


def test_duplicate_id_fails():
    payload = _minimal_scene()
    payload["components"][1]["id"] = "laser-1"
    with pytest.raises(ValueError, match="component ids must be unique"):
        SceneGraph.model_validate(payload)


def test_rotation_nonzero_fails():
    payload = _minimal_scene(rotation_deg=5.0)
    with pytest.raises(ValueError, match="rotation_deg must be 0"):
        SceneGraph.model_validate(payload)


def test_unknown_spec_id_fails():
    payload = _minimal_scene()
    payload["components"][0]["spec_id"] = "SingleRay"
    with pytest.raises(ValueError):
        SceneGraph.model_validate(payload)


def test_screen_before_aperture_fails():
    payload = _minimal_scene(screen_x=50.0)
    scene = SceneGraph.model_validate(payload)
    with pytest.raises(ValueError, match="screen must be placed after aperture"):
        scene.screen_distance_m()


def test_unknown_observable_reference_fails():
    payload = _minimal_scene()
    payload["observables"][0]["screen_id"] = "missing-screen"
    with pytest.raises(ValueError, match="unknown component id"):
        SceneGraph.model_validate(payload)


def test_screen_distance_derived_from_x_positions():
    scene = SceneGraph.model_validate(_minimal_scene(slit_x=200.0, screen_x=700.0))
    assert scene.screen_distance_m() == pytest.approx(0.5)


def test_catalog_has_v1_specs():
    assert set(CATALOG.keys()) == {"laser-monochrome", "single-slit", "screen"}
    assert CATALOG["laser-monochrome"].category == "source"
    assert CATALOG["single-slit"].category == "aperture"
    assert CATALOG["screen"].category == "screen"
