"""Diffraction grating experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import arrow, line, svg_root, text


class GratingExperiment(OpticsExperiment):
    experiment_id = "grating"
    title = "光栅方程与光谱级次实验"
    description = "改变光栅刻线密度、波长和入射角，观察哪些衍射级次可以被接收到。"
    difficulty = "intermediate"
    prerequisites = ["double-slit", "color-mixing"]
    linked_concepts = [
        "diffraction-grating",
        "spectral-resolution",
    ]
    linked_formulas = [
        "grating-equation",
        "grating-resolving-power",
    ]
    learning_objectives = [
        "掌握光栅方程 d(sin θ_i + sin θ_m) = m λ。",
        "理解刻线密度越高，同级衍射角越大。",
        "观察不同级次如何把同一波长导向不同方向。",
    ]
    parameters = [
        Parameter(
            name="groove_density_l_mm",
            label="刻线密度",
            type="float",
            default=600.0,
            min=10.0,
            max=2400.0,
            step=10.0,
            unit="lines/mm",
        ),
        Parameter(
            name="wavelength_nm",
            label="波长",
            type="float",
            default=550.0,
            min=380.0,
            max=700.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="incident_angle_deg",
            label="入射角",
            type="float",
            default=0.0,
            min=0.0,
            max=89.0,
            step=1.0,
            unit="°",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        g = float(params.get("groove_density_l_mm", 600.0))
        lambda_nm = float(params.get("wavelength_nm", 550.0))
        theta_i_deg = float(params.get("incident_angle_deg", 0.0))

        d_mm = 1.0 / g  # grating spacing in mm
        lambda_mm = lambda_nm * 1e-6
        theta_i = math.radians(theta_i_deg)

        # Find all integer orders m for which sin(theta_m) is in [-1, 1]
        orders = []
        max_m = int(math.ceil(2 * d_mm / lambda_mm))
        for m in range(-max_m, max_m + 1):
            sin_theta_m = (m * lambda_mm / d_mm) - math.sin(theta_i)
            if -1.0 <= sin_theta_m <= 1.0:
                theta_m = math.asin(sin_theta_m)
                orders.append({
                    "order": m,
                    "angle_deg": round(math.degrees(theta_m), 2),
                })

        # Angular dispersion for the central (transmission) order near m=1
        angular_dispersion = None
        if orders:
            # d(theta)/d(lambda) = m / (d cos theta_m)
            # Pick m=1 if present, else first non-zero order
            ref = next((o for o in orders if o["order"] == 1), None)
            if ref is None:
                ref = next((o for o in orders if o["order"] != 0), None)
            if ref:
                theta_m = math.radians(ref["angle_deg"])
                angular_dispersion = ref["order"] / (d_mm * math.cos(theta_m))  # rad/mm
                angular_dispersion_rad_nm = angular_dispersion * 1e-6  # rad/nm

        svg = self._draw_svg(g, lambda_nm, theta_i_deg, orders)

        return ExperimentResult(
            data={
                "groove_density_l_mm": g,
                "grating_spacing_um": round(d_mm * 1000.0, 4),
                "wavelength_nm": lambda_nm,
                "incident_angle_deg": theta_i_deg,
                "orders": orders,
                "angular_dispersion_rad_nm": (
                    round(angular_dispersion_rad_nm, 6) if angular_dispersion else None
                ),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "刻线密度越高，同级光谱展开得越宽，分辨率越高。",
                "零级（m=0）不随波长变化，不能用于分光。",
                "实际光栅效率受闪耀角和偏振态影响，这里未建模。",
            ],
        )

    def _draw_svg(
        self,
        g: float,
        lambda_nm: float,
        theta_i_deg: float,
        orders: list[dict[str, Any]],
    ) -> str:
        width, height = 640, 320
        gx = width // 2
        gy = height // 2

        r, g_color, b = self._wavelength_to_rgb(lambda_nm)
        color = f"rgb({r},{g_color},{b})"

        children = [
            # Grating
            line(gx, gy - 80, gx, gy + 80, stroke="#374151", stroke_width=4),
            text(
                gx, gy + 100, f"光栅 {g:.0f} lines/mm",
                fill="#64748b", font_size=11, anchor="middle",
            ),
            # Incident ray from top-left
            *self._ray(gx, gy, theta_i_deg + 180, 120, color, label="入射"),
        ]

        # Diffracted orders
        for order_info in orders:
            m = order_info["order"]
            angle = order_info["angle_deg"]
            # angle is measured from grating normal; positive to the right/up side
            # Incident came from left, diffracted goes to right.
            label = f"m={m} {angle:.1f}°"
            children.extend(
                self._ray(gx, gy, angle, 110, color, label=label, offset=15 + abs(m) * 8)
            )

        return svg_root(width, height, children)

    def _ray(
        self,
        cx: float,
        cy: float,
        angle_deg: float,
        length: float,
        color: str,
        label: str,
        offset: float = 0,
    ) -> list[str]:
        """Draw a ray. angle_deg = 0 points right along +x; 90 points up."""
        rad = math.radians(angle_deg)
        # Start point away from center
        x1 = cx - length * math.cos(rad)
        y1 = cy - length * math.sin(rad)
        x2 = cx
        y2 = cy
        # Label near the start
        lx = x1 + offset * math.cos(rad + math.pi / 2)
        ly = y1 + offset * math.sin(rad + math.pi / 2)
        return [
            arrow(x1, y1, x2, y2, color=color, stroke_width=2),
            text(lx, ly, label, fill=color, font_size=10, anchor="middle"),
        ]

    @staticmethod
    def _wavelength_to_rgb(wavelength_nm: float) -> tuple[int, int, int]:
        w = wavelength_nm
        if w < 440:
            r = int((440 - w) / (440 - 380) * 255)
            g = 0
            b = 255
        elif w < 490:
            r = 0
            g = int((w - 440) / (490 - 440) * 255)
            b = 255
        elif w < 510:
            r = 0
            g = 255
            b = int((510 - w) / (510 - 490) * 255)
        elif w < 580:
            r = int((w - 510) / (580 - 510) * 255)
            g = 255
            b = 0
        elif w < 645:
            r = 255
            g = int((645 - w) / (645 - 580) * 255)
            b = 0
        else:
            r = 255
            g = 0
            b = int((w - 645) / (700 - 645) * 255)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
