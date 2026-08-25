"""Tests for the optics lab framework and experiments."""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

import pytest

from optibench.lab import OpticsExperiment, get_registry
from optibench.lab.experiments.aberration_spot import AberrationSpotExperiment
from optibench.lab.experiments.angle_of_view import AngleOfViewExperiment
from optibench.lab.experiments.blackbody import BlackbodyExperiment
from optibench.lab.experiments.chromatic_aberration import ChromaticAberrationExperiment
from optibench.lab.experiments.color_mixing import ColorMixingExperiment
from optibench.lab.experiments.depth_of_field import DepthOfFieldExperiment
from optibench.lab.experiments.detector_snr import DetectorSnrExperiment
from optibench.lab.experiments.diffraction import DiffractionExperiment
from optibench.lab.experiments.double_slit import DoubleSlitExperiment
from optibench.lab.experiments.gaussian_beam import GaussianBeamExperiment
from optibench.lab.experiments.grating import GratingExperiment
from optibench.lab.experiments.illumination_geometry import IlluminationGeometryExperiment
from optibench.lab.experiments.magnification_scale import MagnificationScaleExperiment
from optibench.lab.experiments.mtf_explorer import MtfExplorerExperiment
from optibench.lab.experiments.rayleigh_two_point import RayleighTwoPointExperiment
from optibench.lab.experiments.photometric_flux import PhotometricFluxExperiment
from optibench.lab.experiments.color_gamut import ColorGamutExperiment
from optibench.lab.experiments.qe_responsivity import QeResponsivityExperiment
from optibench.lab.experiments.solid_angle_cone import SolidAngleConeExperiment
from optibench.lab.experiments.lambertian_radiance import LambertianRadianceExperiment
from optibench.lab.experiments.nyquist_sampling import NyquistSamplingExperiment
from optibench.lab.experiments.penumbra import PenumbraExperiment
from optibench.lab.experiments.polarization_malus import PolarizationMalusExperiment
from optibench.lab.experiments.sensor_coverage import SensorCoverageExperiment
from optibench.lab.experiments.single_slit_diffraction import SingleSlitDiffractionExperiment
from optibench.lab.experiments.snell_refraction import SnellRefractionExperiment
from optibench.lab.experiments.thermal_ifov_netd import ThermalIfovNetdExperiment
from optibench.lab.experiments.thin_lens import ThinLensExperiment
from optibench.lab.experiments.tir_critical_angle import TirCriticalAngleExperiment


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


class TestMtfExplorerExperiment:
    def test_default_run(self):
        exp = MtfExplorerExperiment()
        result = exp.run({})
        assert result.data["diffraction_cutoff_lp_mm"] > 0
        assert result.data["mtf50_lp_mm"] is not None
        assert len(result.data["frequencies_lp_mm"]) == len(result.data["mtf_total"])
        _assert_svg(result.svg)

    def test_smaller_aperture_increases_cutoff(self):
        exp = MtfExplorerExperiment()
        low_f = float(exp.run({"f_number": 8.0}).data["diffraction_cutoff_lp_mm"])
        high_f = float(exp.run({"f_number": 2.8}).data["diffraction_cutoff_lp_mm"])
        assert high_f > low_f

    def test_defocus_reduces_mtf50(self):
        exp = MtfExplorerExperiment()
        focused = float(exp.run({"defocus_distance_mm": 1000.0}).data["mtf50_lp_mm"])
        defocused = float(exp.run({"defocus_distance_mm": 900.0}).data["mtf50_lp_mm"])
        assert defocused < focused


class TestBlackbodyExperiment:
    def test_default_run(self):
        exp = BlackbodyExperiment()
        result = exp.run({})
        assert result.data["peak_wavelength_nm"] > 0
        assert len(result.data["wavelengths_nm"]) == len(result.data["radiance"])
        assert len(result.data["perceived_rgb"]) == 3
        _assert_svg(result.svg)

    def test_higher_temperature_shifts_peak_to_shorter_wavelength(self):
        exp = BlackbodyExperiment()
        cool = exp.run({"temperature_k": 3000.0}).data["peak_wavelength_nm"]
        hot = exp.run({"temperature_k": 6500.0}).data["peak_wavelength_nm"]
        assert hot < cool

    def test_peak_matches_wiens_law(self):
        exp = BlackbodyExperiment()
        for t in (2700, 5500, 6500):
            peak = exp.run({"temperature_k": float(t)}).data["peak_wavelength_nm"]
            expected = 2.898e6 / t
            assert peak == pytest.approx(expected, rel=0.01)


class TestIlluminationGeometryExperiment:
    def test_default_run(self):
        exp = IlluminationGeometryExperiment()
        result = exp.run({})
        assert result.data["mode"] == "bright-field"
        assert result.data["visibility"] in {
            "dim", "bright", "glare", "shadow", "uniform", "silhouette", "edge",
        }
        _assert_svg(result.svg)

    def test_each_mode_has_valid_visibility(self):
        exp = IlluminationGeometryExperiment()
        for mode in ("bright-field", "dark-field", "coaxial", "diffuse-back", "low-angle"):
            result = exp.run({"mode": mode})
            assert result.data["mode"] == mode
            assert result.data["visibility"]

    def test_scratch_bright_in_dark_field(self):
        exp = IlluminationGeometryExperiment()
        result = exp.run({"mode": "dark-field", "feature_type": "scratch"})
        assert result.data["visibility"] == "bright"


class TestThermalIfovNetdExperiment:
    def test_default_run(self):
        exp = ThermalIfovNetdExperiment()
        result = exp.run({})
        assert result.data["ifov_mrad"] > 0
        assert result.data["projected_pixel_size_mm"] > 0
        assert result.data["pixels_across_target"] > 0
        _assert_svg(result.svg)

    def test_longer_focal_length_decreases_ifov(self):
        exp = ThermalIfovNetdExperiment()
        short_f = exp.run({"focal_length_mm": 10.0}).data["ifov_mrad"]
        long_f = exp.run({"focal_length_mm": 50.0}).data["ifov_mrad"]
        assert long_f < short_f

    def test_larger_distance_increases_projected_pixel(self):
        exp = ThermalIfovNetdExperiment()
        near = exp.run({"target_distance_m": 1.0}).data["projected_pixel_size_mm"]
        far = exp.run({"target_distance_m": 10.0}).data["projected_pixel_size_mm"]
        assert far > near

    def test_low_snr_is_not_detectable(self):
        exp = ThermalIfovNetdExperiment()
        result = exp.run({"target_delta_t_k": 0.05, "netd_mk": 50.0})
        assert result.data["detectable"] is False


class TestAberrationSpotExperiment:
    def test_default_run(self):
        exp = AberrationSpotExperiment()
        result = exp.run({})
        assert result.data["rms_radius"] >= 0
        assert result.data["geometric_radius"] >= 0
        assert len(result.data["spot_rays"]) > 0
        _assert_svg(result.svg)

    def test_spherical_aberration_increases_spot_size(self):
        exp = AberrationSpotExperiment()
        no_ab = exp.run({"spherical": 0.0}).data["rms_radius"]
        with_ab = exp.run({"spherical": 0.5}).data["rms_radius"]
        assert with_ab > no_ab

    def test_astigmatism_produces_non_zero_rms(self):
        exp = AberrationSpotExperiment()
        result = exp.run({"astigmatism": 0.5, "field_height": 0.7})
        assert result.data["rms_radius"] > 0


class TestDoubleSlitExperiment:
    def test_default_run(self):
        exp = DoubleSlitExperiment()
        result = exp.run({})
        assert result.data["fringe_spacing_mm"] == pytest.approx(5.5, rel=1e-3)
        assert result.data["visible_maxima_in_envelope"] > 1
        samples = result.data["intensity_samples"]
        assert len(samples) > 0
        assert samples[0]["y_mm"] < 0
        assert samples[-1]["y_mm"] > 0
        assert any(s["intensity"] > 0.9 for s in samples)
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
        samples = result.data["intensity_samples"]
        assert len(samples) > 0
        assert samples[0]["y_mm"] < 0
        assert samples[-1]["y_mm"] > 0
        assert max(s["intensity"] for s in samples) == pytest.approx(1.0, abs=1e-2)
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
        AberrationSpotExperiment,
        ThermalIfovNetdExperiment,
        IlluminationGeometryExperiment,
        BlackbodyExperiment,
        MtfExplorerExperiment,
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


class TestBlackbodyDualTemperature:
    def test_exitance_ratio_follows_t4(self):
        exp = BlackbodyExperiment()
        result = exp.run({"temperature_k": 6000.0, "temperature_2_k": 3000.0})
        assert result.data["exitance_ratio_t2_over_t1"] == pytest.approx(0.0625, rel=1e-3)
        _assert_svg(result.svg)

    def test_wien_peak_scales_inverse(self):
        exp = BlackbodyExperiment()
        result = exp.run({"temperature_k": 6000.0, "temperature_2_k": 3000.0})
        assert result.data["peak_wavelength_nm"] == pytest.approx(483.0, abs=1.0)
        assert result.data["peak_wavelength_2_nm"] == pytest.approx(965.9, abs=1.0)


class TestGaussianBeamExperiment:
    def test_default_run_rayleigh_range(self):
        exp = GaussianBeamExperiment()
        result = exp.run({})
        expected_zr_mm = math.pi * 50e-6**2 / 632.8e-9 * 1e3
        assert result.data["rayleigh_range_mm"] == pytest.approx(expected_zr_mm, rel=1e-3)
        _assert_svg(result.svg)

    def test_divergence_angle_formula(self):
        exp = GaussianBeamExperiment()
        result = exp.run({})
        expected_mrad = 632.8e-9 / (math.pi * 50e-6) * 1e3
        assert result.data["divergence_half_angle_mrad"] == pytest.approx(expected_mrad, rel=1e-3)

    def test_smaller_waist_diverges_faster(self):
        exp = GaussianBeamExperiment()
        wide = exp.run({"waist_radius_um": 100})
        narrow = exp.run({"waist_radius_um": 25})
        assert narrow.data["divergence_half_angle_mrad"] > wide.data["divergence_half_angle_mrad"]


class TestDetectorSnrExperiment:
    def test_default_run_snr_matches_formula(self):
        exp = DetectorSnrExperiment()
        result = exp.run({})
        lam_m = 550e-9
        area = (3.3e-6) ** 2
        t_s = 10e-3
        n_signal = 0.6 * 0.01 * lam_m / (6.62607015e-34 * 2.99792458e8) * area * t_s
        expected_snr = n_signal / math.sqrt(n_signal + 50 * t_s + 5**2)
        assert result.data["signal_electrons"] == pytest.approx(n_signal, rel=1e-3)
        assert result.data["snr"] == pytest.approx(expected_snr, rel=1e-3)
        _assert_svg(result.svg)

    def test_shot_limited_flag(self):
        exp = DetectorSnrExperiment()
        bright = exp.run({"irradiance_w_m2": 1.0})
        dim = exp.run({"irradiance_w_m2": 0.0001})
        assert bright.data["shot_limited"] is True
        assert dim.data["shot_limited"] is False


class TestTirCriticalAngleExperiment:
    def test_default_run_values(self):
        exp = TirCriticalAngleExperiment()
        result = exp.run({})
        assert result.data["critical_angle_deg"] == pytest.approx(80.51, abs=0.05)
        assert result.data["numerical_aperture"] == pytest.approx(0.2408, abs=0.001)
        _assert_svg(result.svg)

    def test_no_guiding_when_clad_denser(self):
        exp = TirCriticalAngleExperiment()
        result = exp.run({"n_core": 1.4, "n_clad": 1.45})
        assert result.data["guiding"] is False

    def test_air_interface_critical_angle(self):
        exp = TirCriticalAngleExperiment()
        result = exp.run({"n_core": 1.5, "n_clad": 1.0})
        assert result.data["critical_angle_deg"] == pytest.approx(41.81, abs=0.05)


class TestPenumbraExperiment:
    def test_default_run_geometry(self):
        exp = PenumbraExperiment()
        result = exp.run({})
        assert result.data["umbra_radius_at_screen_mm"] == pytest.approx(2.5, abs=0.01)
        assert result.data["penumbra_outer_radius_mm"] == pytest.approx(32.5, abs=0.01)
        assert result.data["umbra_tip_distance_mm"] == pytest.approx(200.0, abs=0.1)
        _assert_svg(result.svg)

    def test_pointlike_source_sharp_shadow(self):
        exp = PenumbraExperiment()
        result = exp.run({"source_diameter_mm": 5, "object_diameter_mm": 20,
                          "screen_distance_mm": 100})
        assert result.data["umbra_tip_distance_mm"] is None
        assert result.data["umbra_exists_on_screen"] is True
        assert result.data["penumbra_band_width_mm"] > 0


class TestLambertianRadianceExperiment:
    def test_cosine_law_at_60deg(self):
        exp = LambertianRadianceExperiment()
        result = exp.run({"viewing_angle_deg": 60})
        assert result.data["intensity_at_angle"] == pytest.approx(30.0, abs=0.1)
        _assert_svg(result.svg)

    def test_radiance_independent_of_angle(self):
        exp = LambertianRadianceExperiment()
        normal = exp.run({"viewing_angle_deg": 0})
        tilted = exp.run({"viewing_angle_deg": 60})
        assert normal.data["radiance_relative"] == pytest.approx(
            tilted.data["radiance_relative"], rel=1e-3
        )


class TestSolidAngleConeExperiment:
    def test_exact_value_at_30_deg(self):
        exp = SolidAngleConeExperiment()
        result = exp.run({"half_angle_deg": 30.0})
        expected = 2 * math.pi * (1 - math.cos(math.radians(30.0)))
        assert result.data["omega_exact_sr"] == pytest.approx(expected, rel=1e-4)
        _assert_svg(result.svg)

    def test_hemisphere_limit(self):
        exp = SolidAngleConeExperiment()
        result = exp.run({"half_angle_deg": 89.0})
        assert result.data["omega_exact_sr"] < 2 * math.pi
        assert result.data["approx_error_pct"] > 10


class TestQeResponsivityExperiment:
    def test_responsivity_formula(self):
        exp = QeResponsivityExperiment()
        result = exp.run({"quantum_efficiency": 0.8, "wavelength_nm": 800})
        expected = 0.8 * 1.602176634e-19 * 800e-9 / (6.62607015e-34 * 2.99792458e8)
        assert result.data["responsivity_a_per_w"] == pytest.approx(expected, rel=1e-3)
        _assert_svg(result.svg)

    def test_higher_qe_higher_responsivity(self):
        exp = QeResponsivityExperiment()
        low = exp.run({"quantum_efficiency": 0.3})
        high = exp.run({"quantum_efficiency": 0.9})
        assert high.data["responsivity_a_per_w"] > low.data["responsivity_a_per_w"] * 2


class TestColorGamutExperiment:
    def test_red_primary_maps_to_srgb_corner(self):
        exp = ColorGamutExperiment()
        result = exp.run({"rgb_r": 255, "rgb_g": 0, "rgb_b": 0})
        assert result.data["cie_x"] == pytest.approx(0.64, abs=0.005)
        assert result.data["cie_y"] == pytest.approx(0.33, abs=0.005)
        _assert_svg(result.svg)

    def test_white_is_d65_inside_gamut(self):
        exp = ColorGamutExperiment()
        result = exp.run({"rgb_r": 255, "rgb_g": 255, "rgb_b": 255})
        assert result.data["cie_x"] == pytest.approx(0.3127, abs=0.002)
        assert result.data["inside_srgb_gamut"] is True

    def test_deep_spectral_green_outside_srgb(self):
        exp = ColorGamutExperiment()
        result = exp.run({"rgb_r": 120, "rgb_g": 255, "rgb_b": 0})
        assert result.data["inside_srgb_gamut"] is True  # RGB 输入必然在 sRGB 内


class TestPhotometricFluxExperiment:
    def test_efficacy_bounded_by_km(self):
        exp = PhotometricFluxExperiment()
        for temp in (3000.0, 5500.0, 10000.0):
            result = exp.run({"temperature_k": temp})
            assert 0 < result.data["luminous_efficacy_lm_per_w"] <= 683.0
            _assert_svg(result.svg)

    def test_hotter_blackbody_more_efficient(self):
        exp = PhotometricFluxExperiment()
        warm = exp.run({"temperature_k": 3000.0})
        hot = exp.run({"temperature_k": 6500.0})
        assert hot.data["luminous_efficacy_lm_per_w"] > warm.data["luminous_efficacy_lm_per_w"]


class TestRayleighTwoPointExperiment:
    def test_rayleigh_criterion_dip(self):
        exp = RayleighTwoPointExperiment()
        result = exp.run({"separation_ratio": 1.0})
        assert result.data["resolved_by_rayleigh"] is True
        assert 15.0 < result.data["center_dip_pct"] < 40.0
        _assert_svg(result.svg)

    def test_unresolved_when_close(self):
        exp = RayleighTwoPointExperiment()
        merged = exp.run({"separation_ratio": 0.4})
        assert merged.data["resolved_by_rayleigh"] is False
        assert merged.data["resolved_by_sparrow"] is False

    def test_airy_radius_scales_with_f_number(self):
        exp = RayleighTwoPointExperiment()
        r8 = exp.run({"f_number": 8}).data["airy_radius_um"]
        r16 = exp.run({"f_number": 16}).data["airy_radius_um"]
        assert r16 == pytest.approx(2 * r8)
