"""Sensor size standardization utilities."""

from __future__ import annotations

from optibench.core.types import SensorSize

# 传感器尺寸标准化表（对角线名义值 → 实际物理尺寸 mm）
SENSOR_FORMAT_TABLE: dict[str, SensorSize] = {
    "1/4": SensorSize(3.20, 2.40),
    "1/3": SensorSize(4.80, 3.60),
    "1/2.3": SensorSize(6.16, 4.62),
    "1/2": SensorSize(6.40, 4.80),
    "1/1.8": SensorSize(7.18, 5.32),
    "2/3": SensorSize(8.80, 6.60),
    "1": SensorSize(12.80, 9.60),
    "4/3": SensorSize(17.30, 13.00),
    "APS-C": SensorSize(22.30, 14.90),
    "Full Frame": SensorSize(36.00, 24.00),
}


def sensor_size_from_format(format_inch: str) -> SensorSize | None:
    """从名义尺寸获取实际传感器尺寸."""
    return SENSOR_FORMAT_TABLE.get(format_inch)


def sensor_size_from_pixels(width_px: int, height_px: int, pixel_size_um: float) -> SensorSize:
    """从像素数和像元尺寸计算传感器物理尺寸."""
    w_mm = width_px * pixel_size_um / 1000.0
    h_mm = height_px * pixel_size_um / 1000.0
    return SensorSize(w_mm, h_mm)


def sensor_diag_from_format(format_inch: str) -> float:
    """获取传感器对角线（mm）."""
    size = sensor_size_from_format(format_inch)
    if size:
        return size.diag
    raise ValueError(f"Unknown sensor format: {format_inch}")
