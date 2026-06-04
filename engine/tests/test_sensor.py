"""Tests for sensor utilities."""

import pytest
from lensfit.core.sensor import (
    SENSOR_FORMAT_TABLE,
    sensor_diag_from_format,
    sensor_size_from_format,
    sensor_size_from_pixels,
)


class TestSensorSize:
    def test_format_table_coverage(self):
        assert "2/3" in SENSOR_FORMAT_TABLE
        assert "1/2" in SENSOR_FORMAT_TABLE
        assert "Full Frame" in SENSOR_FORMAT_TABLE

    def test_sensor_size_from_format(self):
        size = sensor_size_from_format("2/3")
        assert size is not None
        assert size.w == 8.8
        assert size.h == 6.6
        assert size.diag == pytest.approx(11.0, rel=0.01)

    def test_sensor_diag_from_format(self):
        assert sensor_diag_from_format("1/2") == pytest.approx(8.0, rel=0.01)

    def test_sensor_size_from_pixels(self):
        size = sensor_size_from_pixels(1920, 1080, 3.45)
        assert size.w == pytest.approx(6.624, rel=0.001)
        assert size.h == pytest.approx(3.726, rel=0.001)

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError):
            sensor_diag_from_format("Unknown")
