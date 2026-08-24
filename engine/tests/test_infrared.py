"""Tests for infrared domain module."""

import pytest

from optibench.domains.base import DeviceCombo, Requirements
from optibench.domains.infrared import InfraredModule


class MockLens:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockDetector:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestInfraredModule:
    @pytest.fixture
    def module(self):
        return InfraredModule()

    @pytest.fixture
    def lwir_lens(self):
        return MockLens(
            id=1,
            model="Lightpath 25mm f/1.0 LWIR",
            focal_length_mm=25.0,
            focal_length_max=None,
            max_aperture=1.0,
            image_circle_mm=21.0,
            mount_type="M34x0.5",
            price_usd=1299.0,
            wavelength_min_nm=8000,
            wavelength_max_nm=14000,
        )

    @pytest.fixture
    def lwir_detector(self):
        return MockDetector(
            id=1,
            model="FLIR Boson 640",
            sensor_format_inch="1/2",
            sensor_w_mm=7.68,
            sensor_h_mm=6.14,
            sensor_diag_mm=9.83,
            resolution_w=640,
            resolution_h=512,
            pixel_size_um=12.0,
            mount_type="M34x0.5",
            price_usd=2999.0,
            netd_mk=50.0,
            spectral_range_min_um=8.0,
            spectral_range_max_um=14.0,
        )

    def test_domain_id(self, module):
        assert module.domain_id == "infrared"

    def test_parameters(self, module):
        params = module.get_parameters()
        names = [p.name for p in params]
        assert "band" in names
        assert "wavelength_um" in names
        assert "fov_deg" in names
        assert "working_distance_m" in names

    def test_wavelength_coverage_pass(self, module, lwir_lens, lwir_detector):
        reqs = Requirements(domain="infrared", params={"wavelength_um": 10.0})
        combo = DeviceCombo(lens=lwir_lens, detector=lwir_detector, requirements=reqs)
        constraint = module.get_hard_constraints()[0]
        assert constraint.check(combo) is True

    def test_wavelength_coverage_fail(self, module, lwir_lens, lwir_detector):
        reqs = Requirements(domain="infrared", params={"wavelength_um": 3.0})
        combo = DeviceCombo(lens=lwir_lens, detector=lwir_detector, requirements=reqs)
        constraint = module.get_hard_constraints()[0]
        assert constraint.check(combo) is False

    def test_sensor_coverage_pass(self, module, lwir_lens, lwir_detector):
        reqs = Requirements(domain="infrared", params={})
        combo = DeviceCombo(lens=lwir_lens, detector=lwir_detector, requirements=reqs)
        constraint = module.get_hard_constraints()[1]
        assert constraint.check(combo) is True

    def test_calculate_derived(self, module, lwir_lens, lwir_detector):
        reqs = Requirements(
            domain="infrared",
            params={
                "wavelength_um": 10.0,
                "fov_deg": 24.0,
                "working_distance_m": 10.0,
                "pixel_size_um": 12.0,
            },
        )
        combo = DeviceCombo(lens=lwir_lens, detector=lwir_detector, requirements=reqs)
        derived = module.calculate_derived(combo)

        assert "ifov_mrad" in derived
        assert "spatial_resolution_m" in derived
        assert "fov_w_deg" in derived
        assert "fov_h_deg" in derived
        assert "band_overlap_ratio" in derived
        assert derived["ifov_mrad"] == pytest.approx(0.48, rel=0.1)
        assert derived["spatial_resolution_m"] == pytest.approx(0.0048, rel=0.1)
