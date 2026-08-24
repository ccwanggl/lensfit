"""Tests for thin lens calculator."""

import pytest

from optibench.core.thin_lens import ThinLensCalculator
from optibench.core.types import OpticalParams


class TestThinLensCalculator:
    def test_focal_from_wd_fov(self):
        calc = ThinLensCalculator()
        focal = calc.focal_from_wd_fov(wd=200, fov=50, sensor=8.8)
        # f = (wd * sensor) / (fov + sensor) = 1760 / 58.8
        assert focal == pytest.approx(29.93, rel=0.01)

    def test_fov_from_wd_focal(self):
        calc = ThinLensCalculator()
        fov = calc.fov_from_wd_focal(wd=200, focal=25, sensor=8.8)
        # fov = (wd * sensor) / focal - sensor = 1760/25 - 8.8
        assert fov == pytest.approx(61.6, rel=0.01)

    def test_magnification_from_focal_wd(self):
        calc = ThinLensCalculator()
        mag = calc.magnification_from_focal_wd(focal=25, wd=200)
        assert mag == pytest.approx(0.143, rel=0.01)

    def test_afov_from_sensor_focal(self):
        calc = ThinLensCalculator()
        afov = calc.afov_from_sensor_focal(sensor=8.8, focal=25)
        assert afov == pytest.approx(19.8, rel=0.01)

    def test_solve_wd_sensor_fov_to_focal(self):
        calc = ThinLensCalculator()
        params = OpticalParams(
            working_distance=200,
            sensor_w=8.8,
            fov_w=50,
        )
        result = calc.solve(params)
        assert result.focal_length is not None
        assert result.focal_length == pytest.approx(29.93, rel=0.01)

    def test_solve_focal_sensor_to_afov(self):
        calc = ThinLensCalculator()
        params = OpticalParams(
            focal_length=25,
            sensor_w=8.8,
        )
        result = calc.solve(params)
        assert result.afov_h is not None
        assert result.afov_h == pytest.approx(19.8, rel=0.01)
