"""Thin lens formula calculator."""

from __future__ import annotations

import math
from typing import Optional

from lensfit.core.types import OpticalParams


class ThinLensCalculator:
    """薄透镜公式计算器 — 支持已知任意参数，推导其余参数."""

    @staticmethod
    def focal_from_wd_fov(wd: float, fov: float, sensor: float) -> float:
        """精确公式: f = (WD * sensor) / (FOV + sensor)"""
        return (wd * sensor) / (fov + sensor)

    @staticmethod
    def fov_from_wd_focal(wd: float, focal: float, sensor: float) -> float:
        """已知工作距离和焦距，求视场."""
        return (wd * sensor) / focal - sensor

    @staticmethod
    def wd_from_fov_focal(fov: float, focal: float, sensor: float) -> float:
        """已知视场和焦距，求工作距离."""
        return focal * (fov + sensor) / sensor

    @staticmethod
    def magnification_from_focal_wd(focal: float, wd: float) -> float:
        """精确放大倍率: β = f / (WD - f)"""
        if wd <= focal:
            raise ValueError("Working distance must be greater than focal length")
        return focal / (wd - focal)

    @staticmethod
    def afov_from_sensor_focal(sensor: float, focal: float) -> float:
        """视角: AFOV = 2 * arctan(sensor / (2*f))"""
        return 2 * math.degrees(math.atan(sensor / (2 * focal)))

    def solve(self, params: OpticalParams, max_iter: int = 10) -> OpticalParams:
        """智能求解器：根据已知参数自动推导未知参数."""
        result = OpticalParams()
        # 拷贝已知值
        for field_name in result.__dataclass_fields__:
            setattr(result, field_name, getattr(params, field_name))

        changed = True
        iteration = 0

        while changed and iteration < max_iter:
            changed = False
            iteration += 1

            # Rule: WD + sensor_w + FOV_w → focal
            if result.focal_length is None and all(
                v is not None
                for v in [result.working_distance, result.sensor_w, result.fov_w]
            ):
                result.focal_length = self.focal_from_wd_fov(
                    result.working_distance, result.fov_w, result.sensor_w
                )
                changed = True

            # Rule: focal + sensor_w → AFOV_h
            if result.afov_h is None and all(
                v is not None for v in [result.sensor_w, result.focal_length]
            ):
                result.afov_h = self.afov_from_sensor_focal(
                    result.sensor_w, result.focal_length
                )
                changed = True

            # Rule: focal + WD → magnification
            if result.magnification is None and all(
                v is not None for v in [result.focal_length, result.working_distance]
            ):
                result.magnification = self.magnification_from_focal_wd(
                    result.focal_length, result.working_distance
                )
                changed = True

            # Rule: focal + sensor_w + FOV_w ← WD
            if result.working_distance is None and all(
                v is not None for v in [result.focal_length, result.sensor_w, result.fov_w]
            ):
                result.working_distance = self.wd_from_fov_focal(
                    result.fov_w, result.focal_length, result.sensor_w
                )
                changed = True

            # Rule: focal + sensor_w + WD ← FOV_w
            if result.fov_w is None and all(
                v is not None for v in [result.focal_length, result.sensor_w, result.working_distance]
            ):
                result.fov_w = self.fov_from_wd_focal(
                    result.working_distance, result.focal_length, result.sensor_w
                )
                changed = True

        return result

    @staticmethod
    def depth_of_field(
        focal: float, f_number: float, coc_diameter: float, focus_distance: float
    ) -> tuple[float, float]:
        """景深计算.

        Returns:
            (near_limit, far_limit) in mm.
        """
        hyperfocal = (focal**2) / (f_number * coc_diameter) + focal
        near = (hyperfocal * focus_distance) / (hyperfocal + focus_distance)
        if focus_distance >= hyperfocal:
            far = float("inf")
        else:
            far = (hyperfocal * focus_distance) / (hyperfocal - focus_distance)
        return near, far
