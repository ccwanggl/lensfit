"""MTF curve data generator.

The catalog only stores a single ``mtf50_lpmm`` value per lens.  We synthesise
a smooth modulation-transfer curve from that value and overlay the detector
Nyquist frequency so users can see whether the lens out-resolves the sensor.
"""

from __future__ import annotations

import math
from typing import Any


def _mtf_value(frequency: float, mtf50: float) -> float:
    """Estimate MTF at *frequency* (lp/mm) given the lens MTF50.

    Uses a Gaussian-shaped MTF approximation:
        MTF(f) = exp(-f^2 / (2 sigma^2))
    where sigma is chosen so that MTF(mtf50) = 0.5.
    """
    if mtf50 <= 0:
        return 1.0 if frequency == 0 else 0.0
    # MTF50 => sigma = mtf50 / sqrt(2 ln 2)
    sigma = mtf50 / math.sqrt(2.0 * math.log(2.0))
    if sigma <= 0:
        return 1.0 if frequency == 0 else 0.0
    return math.exp(-(frequency**2) / (2.0 * sigma**2))


class MtfPlotData:
    """Generate MTF curve data for a lens/detector pair."""

    def __init__(self, mtf50_lpmm: float, pixel_size_um: float | None = None):
        self.mtf50_lpmm = mtf50_lpmm
        self.pixel_size_um = pixel_size_um

    def generate(self, num_points: int = 80) -> dict[str, Any]:
        """Return MTF curve points and detector Nyquist frequency.

        Returns:
            {
                "lens_mtf50_lpmm": float,
                "detector_nyquist_lpmm": float | None,
                "points": [{"frequency_lpmm": float, "mtf": float, "is_nyquist": bool}, ...]
            }
        """
        nyquist = None
        if self.pixel_size_um and self.pixel_size_um > 0:
            nyquist = 1000.0 / (2.0 * self.pixel_size_um)

        # Upper frequency bound: at least 1.2× nyquist or 2× MTF50
        upper = 2.0 * (self.mtf50_lpmm or 0)
        if nyquist:
            upper = max(upper, nyquist * 1.2)
        upper = max(upper, 10.0)

        step = upper / max(num_points - 1, 1)
        points = []
        mtf50 = self.mtf50_lpmm or 0.0
        for i in range(num_points):
            f = i * step
            mtf = _mtf_value(f, mtf50)
            is_nyquist = False
            if nyquist and abs(f - nyquist) < step / 2:
                is_nyquist = True
                # Pin the displayed nyquist point to the exact frequency
                f = nyquist
            points.append(
                {
                    "frequency_lpmm": round(f, 3),
                    "mtf": round(mtf, 4),
                    "is_nyquist": is_nyquist,
                }
            )

        return {
            "lens_mtf50_lpmm": self.mtf50_lpmm,
            "detector_nyquist_lpmm": nyquist,
            "points": points,
        }
