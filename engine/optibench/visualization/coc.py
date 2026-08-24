"""Circle of confusion and depth-of-field data generator.

Provides an estimated CoC for a sensor and classic DoF distances
(hyperfocal, near limit, far limit) across a range of apertures.

All distances are returned in metres for consistency.
"""

from __future__ import annotations

import math
from typing import Any

# Standard full-frame-equivalent CoC divisor (Zeiss / widely used).
_COC_DIVISOR = 1730.0
# Aperture stops to evaluate for the DoF chart.
_APERTURE_STOPS = [1.4, 2.0, 2.8, 4.0, 5.6, 8.0, 11.0, 16.0, 22.0]


def _sensor_diag_mm(sensor_w_mm: float, sensor_h_mm: float) -> float:
    return math.sqrt(sensor_w_mm**2 + sensor_h_mm**2)


def _compute_coc_mm(sensor_diag_mm: float, pixel_size_um: float | None) -> float:
    """Return a conservative CoC estimate in millimetres."""
    coc_from_diag = sensor_diag_mm / _COC_DIVISOR
    coc = coc_from_diag
    if pixel_size_um and pixel_size_um > 0:
        # Pixel-size limited CoC: ~2 pixels is a common print/digital threshold.
        coc_from_pixel = (pixel_size_um * 2.0) / 1000.0
        coc = min(coc_from_diag, coc_from_pixel)
    return coc


class CocPlotData:
    """Generate CoC / DoF data for a lens/detector pair."""

    def __init__(
        self,
        focal_length_mm: float,
        max_aperture: float,
        sensor_w_mm: float,
        sensor_h_mm: float,
        pixel_size_um: float | None = None,
        focus_distance_m: float = 2.0,
    ):
        self.focal_length_mm = focal_length_mm
        self.max_aperture = max_aperture
        self.sensor_w_mm = sensor_w_mm
        self.sensor_h_mm = sensor_h_mm
        self.pixel_size_um = pixel_size_um
        self.focus_distance_m = focus_distance_m

    def generate(self) -> dict[str, Any]:
        """Return CoC and DoF data across aperture stops.

        Returns:
            {
                "coc_mm": float,
                "sensor_diag_mm": float,
                "focus_distance_m": float,
                "focal_length_mm": float,
                "max_aperture": float,
                "apertures": [
                    {
                        "aperture": float,
                        "hyperfocal_m": float,
                        "near_limit_m": float,
                        "far_limit_m": float | None,
                        "dof_total_m": float | None,
                    },
                    ...
                ]
            }
        """
        if self.focal_length_mm <= 0 or self.max_aperture <= 0:
            raise ValueError("Focal length and max aperture must be positive")
        if self.sensor_w_mm <= 0 or self.sensor_h_mm <= 0:
            raise ValueError("Sensor dimensions must be positive")

        sensor_diag = _sensor_diag_mm(self.sensor_w_mm, self.sensor_h_mm)
        coc_mm = _compute_coc_mm(sensor_diag, self.pixel_size_um)
        if coc_mm <= 0:
            raise ValueError("Computed CoC must be positive")
        f_mm = self.focal_length_mm

        apertures = []
        for n in _APERTURE_STOPS:
            # Only include stops that this lens can achieve (f-number >= max_aperture).
            if n + 1e-6 < self.max_aperture:
                continue

            # Hyperfocal distance in metres.
            # H = f^2 / (N * c) + f  (exact formula)
            hyperfocal_m = ((f_mm * f_mm) / (n * coc_mm)) / 1000.0 + f_mm / 1000.0

            s = self.focus_distance_m
            # Near limit: H*s / (H + s)  (common approximation, H and s in metres)
            near_m = (hyperfocal_m * s) / (hyperfocal_m + s)

            # Far limit: infinity when focused at or beyond hyperfocal.
            if s >= hyperfocal_m - 1e-9:
                far_m = None
                dof_m = None
            else:
                far_m = (hyperfocal_m * s) / (hyperfocal_m - s)
                dof_m = far_m - near_m

            apertures.append(
                {
                    "aperture": n,
                    "hyperfocal_m": round(hyperfocal_m, 3),
                    "near_limit_m": round(near_m, 3),
                    "far_limit_m": round(far_m, 3) if far_m is not None else None,
                    "dof_total_m": round(dof_m, 3) if dof_m is not None else None,
                }
            )

        if not apertures:
            # Fallback: include max aperture even if it falls outside the standard stops.
            n = self.max_aperture
            hyperfocal_m = ((f_mm * f_mm) / (n * coc_mm)) / 1000.0 + f_mm / 1000.0
            s = self.focus_distance_m
            near_m = (hyperfocal_m * s) / (hyperfocal_m + s)
            far_m = None if s >= hyperfocal_m - 1e-9 else (hyperfocal_m * s) / (hyperfocal_m - s)
            dof_m = None if far_m is None else far_m - near_m
            apertures.append(
                {
                    "aperture": n,
                    "hyperfocal_m": round(hyperfocal_m, 3),
                    "near_limit_m": round(near_m, 3),
                    "far_limit_m": round(far_m, 3) if far_m is not None else None,
                    "dof_total_m": round(dof_m, 3) if dof_m is not None else None,
                }
            )

        return {
            "coc_mm": round(coc_mm, 4),
            "sensor_diag_mm": round(sensor_diag, 3),
            "focus_distance_m": self.focus_distance_m,
            "focal_length_mm": f_mm,
            "max_aperture": self.max_aperture,
            "apertures": apertures,
        }
