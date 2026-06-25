"""Tests for the optics lab framework and experiments."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from lensfit.lab import OpticsExperiment, get_registry
from lensfit.lab.experiments.angle_of_view import AngleOfViewExperiment
from lensfit.lab.experiments.color_mixing import ColorMixingExperiment
from lensfit.lab.experiments.magnification_scale import MagnificationScaleExperiment
from lensfit.lab.experiments.diffraction import DiffractionExperiment
from lensfit.lab.experiments.sensor_coverage import SensorCoverageExperiment
from lensfit.lab.experiments.thin_lens import ThinLensExperiment


@pytest.fixture
def registry():
    return get_registry()


def _assert_svg(svg: str) -> None:
    """Verify that *svg* is a well-formed SVG containing a root <svg>."""
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"


class TestRegistry:
    def test_registry_discovers_mvp_experiments(self, registry):
        ids = {e.id for e in registry.list_experiments()}
        assert "thin-lens" in ids
        assert "diffraction" in ids
        assert "color-mixing" in ids
        assert "sensor-coverage" in ids

    def test_get_unknown_experiment_returns_none(self, registry):
        assert registry.get("nonexistent") is None

    def test_run_unknown_experiment_raises(self, registry):
        with pytest.raises(KeyError):
            registry.run("nonexistent", {})


class TestThinLensExperiment:
    def test_default_run(self):
        exp = ThinLensExperiment()
        result = exp.run({})
        assert result.data["image_distance_mm"] == pytest.approx(100.0, rel=1e-3)
        assert result.data["magnification"] == pytest.approx(-1.0, rel=1e-3)
        _assert_svg(result.svg)

    def test_virtual_image_warning(self):
        exp = ThinLensExperiment()
        result = exp.run({"focal_length": 50, "object_distance": 30, "object_height": 30})
        assert result.data["image_distance_mm"] < 0
        assert any("虚像" in w for w in result.warnings)

    def test_validation_clamps_out_of_bounds(self):
        exp = ThinLensExperiment()
        validated = exp.validate_params({"focal_length": 5, "object_distance": 1000})
        assert validated["focal_length"] == exp.parameters[0].min
        assert validated["object_distance"] == exp.parameters[1].max


class TestDiffractionExperiment:
    def test_default_run(self):
        exp = DiffractionExperiment()
        result = exp.run({})
        assert "airy_diameter_um" in result.data
        assert result.data["f_number"] == pytest.approx(5.0, rel=1e-3)
        _assert_svg(result.svg)

    def test_smaller_aperture_increases_airy_disk(self):
        exp = DiffractionExperiment()
        small = exp.run({"aperture_mm": 5}).data["airy_diameter_um"]
        large = exp.run({"aperture_mm": 20}).data["airy_diameter_um"]
        assert small > large


class TestColorMixingExperiment:
    def test_default_run(self):
        exp = ColorMixingExperiment()
        result = exp.run({})
        assert "mixed_hex" in result.data
        _assert_svg(result.svg)


class TestAngleOfViewExperiment:
    def test_default_run(self):
        exp = AngleOfViewExperiment()
        result = exp.run({})
        assert result.data["sensor_format"] == "Full Frame"
        assert result.data["afov_diagonal_deg"] == pytest.approx(46.79, rel=1e-2)
        _assert_svg(result.svg)

    def test_wider_focal_length_reduces_afov(self):
        exp = AngleOfViewExperiment()
        wide = exp.run({"focal_length": 25}).data["afov_horizontal_deg"]
        tele = exp.run({"focal_length": 100}).data["afov_horizontal_deg"]
        assert wide > tele

    def test_unknown_sensor_format_raises(self):
        exp = AngleOfViewExperiment()
        with pytest.raises(ValueError):
            exp.run({"sensor_format": "Unknown"})


class TestMagnificationScaleExperiment:
    def test_default_run(self):
        exp = MagnificationScaleExperiment()
        result = exp.run({})
        assert result.data["magnification"] == pytest.approx(0.1429, rel=1e-3)
        assert result.data["pixel_precision_um"] == pytest.approx(24.15, rel=1e-3)
        _assert_svg(result.svg)

    def test_longer_working_distance_reduces_magnification(self):
        exp = MagnificationScaleExperiment()
        near = exp.run({"working_distance": 100}).data["magnification"]
        far = exp.run({"working_distance": 500}).data["magnification"]
        assert abs(near) > abs(far)

    def test_too_short_working_distance_warns(self):
        exp = MagnificationScaleExperiment()
        result = exp.run({"focal_length": 50, "working_distance": 30})
        assert result.warnings
        assert result.data["working_distance_mm"] > 50


class TestSensorCoverageExperiment:
    def test_fully_covered(self):
        exp = SensorCoverageExperiment()
        result = exp.run({"sensor_w_mm": 6.4, "sensor_h_mm": 4.8, "image_circle_mm": 16})
        assert result.data["coverage_ratio"] == 1.0
        assert not result.warnings
        _assert_svg(result.svg)

    def test_partial_coverage_warns(self):
        exp = SensorCoverageExperiment()
        result = exp.run({"sensor_w_mm": 20, "sensor_h_mm": 15, "image_circle_mm": 10})
        assert result.data["coverage_ratio"] < 1.0
        assert result.warnings


def test_all_experiments_are_subclasses():
    for exp_cls in (
        MagnificationScaleExperiment,
        AngleOfViewExperiment,
        ThinLensExperiment,
        DiffractionExperiment,
        ColorMixingExperiment,
        SensorCoverageExperiment,
    ):
        assert issubclass(exp_cls, OpticsExperiment)
        assert exp_cls.experiment_id
