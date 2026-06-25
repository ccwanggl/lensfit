"""Tests for the optics lab framework and experiments."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from lensfit.lab import OpticsExperiment, get_registry
from lensfit.lab.experiments.angle_of_view import AngleOfViewExperiment
from lensfit.lab.experiments.color_mixing import ColorMixingExperiment
from lensfit.lab.experiments.depth_of_field import DepthOfFieldExperiment
from lensfit.lab.experiments.magnification_scale import MagnificationScaleExperiment
from lensfit.lab.experiments.chromatic_aberration import ChromaticAberrationExperiment
from lensfit.lab.experiments.nyquist_sampling import NyquistSamplingExperiment
from lensfit.lab.experiments.double_slit import DoubleSlitExperiment
from lensfit.lab.experiments.grating import GratingExperiment
from lensfit.lab.experiments.polarization_malus import PolarizationMalusExperiment
from lensfit.lab.experiments.single_slit_diffraction import SingleSlitDiffractionExperiment
from lensfit.lab.experiments.snell_refraction import SnellRefractionExperiment
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


class TestNyquistSamplingExperiment:
    def test_default_run(self):
        exp = NyquistSamplingExperiment()
        result = exp.run({})
        assert result.data["detector_nyquist_lpmm"] == pytest.approx(144.93, rel=1e-3)
        assert "status" in result.data
        _assert_svg(result.svg)

    def test_aliasing_when_lens_outresolves_sensor(self):
        exp = NyquistSamplingExperiment()
        result = exp.run({"pixel_size_um": 5.0, "lens_mtf50_lpmm": 150})
        assert result.data["oversampling_ratio"] > 1.0
        assert result.data["status"] == "混叠风险"
        assert result.warnings

    def test_oversampling_when_sensor_outresolves_lens(self):
        exp = NyquistSamplingExperiment()
        result = exp.run({"pixel_size_um": 2.0, "lens_mtf50_lpmm": 40})
        assert result.data["oversampling_ratio"] < 0.5
        assert result.data["status"] == "过度采样"


class TestChromaticAberrationExperiment:
    def test_default_run(self):
        exp = ChromaticAberrationExperiment()
        result = exp.run({})
        assert result.data["total_chromatic_shift_mm"] == pytest.approx(0.8333, rel=1e-3)
        assert result.data["blue_focus_mm"] < result.data["green_focus_mm"]
        assert result.data["red_focus_mm"] > result.data["green_focus_mm"]
        _assert_svg(result.svg)

    def test_lower_abbe_increases_chromatic_shift(self):
        exp = ChromaticAberrationExperiment()
        low_v = exp.run({"abbe_number": 30}).data["total_chromatic_shift_mm"]
        high_v = exp.run({"abbe_number": 80}).data["total_chromatic_shift_mm"]
        assert low_v > high_v


class TestGratingExperiment:
    def test_default_run(self):
        exp = GratingExperiment()
        result = exp.run({})
        assert any(o["order"] == 0 for o in result.data["orders"])
        assert any(o["order"] == 1 for o in result.data["orders"])
        _assert_svg(result.svg)

    def test_zero_order_unchanged_by_wavelength(self):
        exp = GratingExperiment()
        a = exp.run({"wavelength_nm": 450}).data["orders"]
        b = exp.run({"wavelength_nm": 650}).data["orders"]
        a_zero = next(o for o in a if o["order"] == 0)
        b_zero = next(o for o in b if o["order"] == 0)
        assert a_zero["angle_deg"] == b_zero["angle_deg"]

    def test_higher_density_increases_angles(self):
        exp = GratingExperiment()
        low_g = exp.run({"groove_density_l_mm": 300}).data["orders"]
        high_g = exp.run({"groove_density_l_mm": 1200}).data["orders"]
        low_first = next(o for o in low_g if o["order"] == 1)
        high_first = next(o for o in high_g if o["order"] == 1)
        assert abs(high_first["angle_deg"]) > abs(low_first["angle_deg"])


class TestDoubleSlitExperiment:
    def test_default_run(self):
        exp = DoubleSlitExperiment()
        result = exp.run({})
        assert result.data["fringe_spacing_mm"] == pytest.approx(5.5, rel=1e-3)
        assert result.data["visible_maxima_in_envelope"] > 1
        _assert_svg(result.svg)

    def test_larger_separation_tighter_fringes(self):
        exp = DoubleSlitExperiment()
        wide = exp.run({"slit_separation_um": 50}).data["fringe_spacing_mm"]
        tight = exp.run({"slit_separation_um": 200}).data["fringe_spacing_mm"]
        assert wide > tight

    def test_longer_wavelength_wider_fringes(self):
        exp = DoubleSlitExperiment()
        blue = exp.run({"wavelength_nm": 450}).data["fringe_spacing_mm"]
        red = exp.run({"wavelength_nm": 650}).data["fringe_spacing_mm"]
        assert red > blue


class TestSingleSlitDiffractionExperiment:
    def test_default_run(self):
        exp = SingleSlitDiffractionExperiment()
        result = exp.run({})
        assert result.data["first_min_angle_deg"] > 0
        assert result.data["central_max_width_mm"] > 0
        _assert_svg(result.svg)

    def test_narrower_slit_widens_pattern(self):
        exp = SingleSlitDiffractionExperiment()
        narrow = exp.run({"slit_width_um": 20}).data["central_max_width_mm"]
        wide = exp.run({"slit_width_um": 100}).data["central_max_width_mm"]
        assert narrow > wide

    def test_longer_wavelength_widens_pattern(self):
        exp = SingleSlitDiffractionExperiment()
        blue = exp.run({"wavelength_nm": 450}).data["central_max_width_mm"]
        red = exp.run({"wavelength_nm": 650}).data["central_max_width_mm"]
        assert red > blue


class TestPolarizationMalusExperiment:
    def test_default_run(self):
        exp = PolarizationMalusExperiment()
        result = exp.run({})
        assert result.data["after_polarizer1"] == pytest.approx(0.5, rel=1e-6)
        assert result.data["after_polarizer2"] == pytest.approx(0.25, rel=1e-6)
        _assert_svg(result.svg)

    def test_crossed_polarizers_extinction(self):
        exp = PolarizationMalusExperiment()
        result = exp.run({"polarizer1_angle_deg": 0, "polarizer2_angle_deg": 90})
        assert result.data["after_polarizer2"] == pytest.approx(0.0, abs=1e-9)

    def test_parallel_polarizers_maximum(self):
        exp = PolarizationMalusExperiment()
        result = exp.run({"polarizer1_angle_deg": 30, "polarizer2_angle_deg": 30})
        assert result.data["after_polarizer2"] == pytest.approx(0.5, rel=1e-6)


class TestSnellRefractionExperiment:
    def test_default_air_to_glass(self):
        exp = SnellRefractionExperiment()
        result = exp.run({})
        assert result.data["refracted_angle_deg"] == pytest.approx(19.47, rel=1e-3)
        assert result.data["reflectance"] == pytest.approx(0.0415, rel=1e-3)
        _assert_svg(result.svg)

    def test_total_internal_reflection(self):
        exp = SnellRefractionExperiment()
        result = exp.run({"incident_angle_deg": 60, "n1": 1.5, "n2": 1.0})
        assert result.data["total_internal_reflection"] is True
        assert result.data["refracted_angle_deg"] is None
        assert result.data["reflectance"] == pytest.approx(1.0, rel=1e-6)
        assert result.warnings

    def test_normal_incidence_reflectance(self):
        exp = SnellRefractionExperiment()
        result = exp.run({"incident_angle_deg": 0, "n1": 1.0, "n2": 1.5})
        expected = ((1.0 - 1.5) / (1.0 + 1.5)) ** 2
        assert result.data["reflectance"] == pytest.approx(expected, rel=1e-6)


class TestDepthOfFieldExperiment:
    def test_default_run(self):
        exp = DepthOfFieldExperiment()
        result = exp.run({})
        assert result.data["f_number"] == 2.8
        assert result.data["near_limit_m"] < result.data["focus_distance_m"]
        assert result.data["far_limit_m"] > result.data["focus_distance_m"]
        _assert_svg(result.svg)

    def test_hyperfocal_infinite_dof(self):
        exp = DepthOfFieldExperiment()
        # Focus at hyperfocal -> far limit should be None (infinity)
        result = exp.run({"focus_distance_m": 130, "f_number": 2.8})
        assert result.data["far_limit_m"] is None
        assert result.data["dof_total_m"] is None

    def test_smaller_aperture_increases_dof(self):
        exp = DepthOfFieldExperiment()
        wide = exp.run({"f_number": 2.0}).data["dof_total_m"]
        stopped = exp.run({"f_number": 11.0}).data["dof_total_m"]
        assert stopped > wide


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
        GratingExperiment,
        DoubleSlitExperiment,
        SingleSlitDiffractionExperiment,
        PolarizationMalusExperiment,
        ChromaticAberrationExperiment,
        SnellRefractionExperiment,
        NyquistSamplingExperiment,
        DepthOfFieldExperiment,
        MagnificationScaleExperiment,
        AngleOfViewExperiment,
        ThinLensExperiment,
        DiffractionExperiment,
        ColorMixingExperiment,
        SensorCoverageExperiment,
    ):
        assert issubclass(exp_cls, OpticsExperiment)
        assert exp_cls.experiment_id
