"""Single-slit Fraunhofer diffraction experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, line, path, polygon, svg_root, text


class SingleSlitDiffractionExperiment(OpticsExperiment):
    experiment_id = "single-slit-diffraction"
    title = "单缝衍射实验"
    description = "改变缝宽和波长，观察夫琅禾费单缝衍射的强度分布和第一极小位置。"
    difficulty = "intermediate"
    prerequisites = ["diffraction"]
    linked_concepts = [
        "10-concepts/diffraction-limit",
        "10-concepts/衍射极限",
    ]
    linked_formulas = [
        "20-formulas/single-slit-minima",
    ]
    learning_objectives = [
        "理解单缝衍射中央亮纹宽度与缝宽成反比。",
        "观察波长越长、缝越窄，衍射展宽越明显。",
    ]
    parameters = [
        Parameter(
            name="slit_width_um",
            label="缝宽",
            type="float",
            default=50.0,
            min=1.0,
            max=500.0,
            step=1.0,
            unit="μm",
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
            name="screen_distance_m",
            label="屏距",
            type="float",
            default=1.0,
            min=0.1,
            max=5.0,
            step=0.1,
            unit="m",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        a_um = float(params.get("slit_width_um", 50.0))
        lambda_nm = float(params.get("wavelength_nm", 550.0))
        l_m = float(params.get("screen_distance_m", 1.0))

        a_mm = a_um / 1000.0
        lambda_mm = lambda_nm * 1e-6

        # First minima: sin θ = λ / a
        sin_theta1 = lambda_mm / a_mm
        theta1_rad = math.asin(min(1.0, sin_theta1))
        theta1_deg = math.degrees(theta1_rad)
        y1_mm = l_m * 1000.0 * math.tan(theta1_rad)  # first min position on screen
        central_width_mm = 2 * y1_mm

        intensity_samples = self._intensity_samples(a_um, lambda_nm, l_m, y1_mm)
        svg = self._draw_svg(a_um, lambda_nm, l_m, y1_mm, intensity_samples)

        return ExperimentResult(
            data={
                "slit_width_um": a_um,
                "wavelength_nm": lambda_nm,
                "screen_distance_m": l_m,
                "first_min_angle_deg": round(theta1_deg, 4),
                "first_min_position_mm": round(y1_mm, 4),
                "central_max_width_mm": round(central_width_mm, 4),
                "intensity_samples": intensity_samples,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "第一极小位置满足 a sin θ = λ。",
                "减小缝宽会使中央亮纹变宽，但亮度降低。",
                "夫琅禾费近似要求屏距远大于缝宽（远场条件）。",
            ],
        )

    def _intensity_samples(
        self,
        a_um: float,
        lambda_nm: float,
        l_m: float,
        y1_mm: float,
        num_points: int = 200,
    ) -> list[dict[str, float]]:
        """Return sampled relative intensity vs screen position for 3D texture."""
        y_max_mm = max(3 * y1_mm, 0.5)
        a_mm = a_um / 1000.0
        lambda_mm = lambda_nm * 1e-6

        def intensity(y_mm: float) -> float:
            sin_theta = (y_mm / 1000.0) / l_m
            if abs(sin_theta) >= 1.0:
                return 0.0
            beta = math.pi * a_mm * sin_theta / lambda_mm
            if abs(beta) < 1e-9:
                return 1.0
            return (math.sin(beta) / beta) ** 2

        ys = [
            -y_max_mm + 2 * y_max_mm * i / (num_points - 1)
            for i in range(num_points)
        ]
        return [{"y_mm": y, "intensity": intensity(y)} for y in ys]

    def _draw_svg(
        self,
        a_um: float,
        lambda_nm: float,
        l_m: float,
        y1_mm: float,
        intensity_samples: list[dict[str, float]],
    ) -> str:
        width, height = 640, 320
        plot_x, plot_y = 60, 50
        plot_w, plot_h = 400, 180

        ys = [s["y_mm"] for s in intensity_samples]
        intensities = [s["intensity"] for s in intensity_samples]
        y_max_mm = max(abs(ys[0]), abs(ys[-1]))

        def x_to_px(y):
            return plot_x + (y + y_max_mm) / (2 * y_max_mm) * plot_w

        def y_to_px(i):
            return plot_y + plot_h - i * plot_h

        curve = "M " + " L ".join(
            f"{x_to_px(y):.1f} {y_to_px(i):.1f}" for y, i in zip(ys, intensities)
        )

        nq_x = x_to_px(y1_mm)

        children = [
            *axis_x(plot_x, plot_y + plot_h, plot_w, label="屏上位置 y (mm)"),
            *axis_y(plot_x, plot_y + plot_h, plot_h, label="相对强度"),
            # Fill under curve
            polygon(
                [(plot_x, plot_y + plot_h)]
                + [(x_to_px(y), y_to_px(i)) for y, i in zip(ys, intensities)]
                + [(plot_x + plot_w, plot_y + plot_h)],
                fill="rgba(37,99,235,0.15)",
                stroke="none",
            ),
            path(curve, fill="none", stroke="#2563eb", stroke_width=2),
            line(
                nq_x, plot_y, nq_x, plot_y + plot_h,
                stroke="#dc2626", dash="4",
            ),
            line(
                width - nq_x + 20, plot_y, width - nq_x + 20, plot_y + plot_h,
                stroke="#dc2626", dash="4",
            ),
            text(
                nq_x,
                plot_y - 10,
                f"第一极小 y=±{y1_mm:.2f} mm",
                fill="#dc2626",
                font_size=10,
                anchor="middle",
            ),
            # Slit diagram on the right
            *self._slit_diagram(width - 120, plot_y, 80, a_um, lambda_nm),
            # Summary
            text(
                width / 2,
                height - 20,
                f"缝宽 {a_um:.0f} μm  |  波长 {lambda_nm:.0f} nm  |  屏距 {l_m:.1f} m",
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)

    def _slit_diagram(
        self, x: float, y: float, h: float, a_um: float, lambda_nm: float
    ) -> list[str]:
        """Draw a simple slit aperture with incoming wave color."""
        r, g, b = self._wavelength_to_rgb(lambda_nm)
        color = f"rgb({r},{g},{b})"
        slit_h = min(60, max(10, a_um / 5))  # visual slit height
        top_edge = y + (h - slit_h) / 2
        bottom_edge = y + (h + slit_h) / 2
        return [
            polygon(
                [(x, y), (x + 30, y), (x + 30, y + h), (x, y + h)],
                fill="#e2e8f0",
                stroke="#64748b",
            ),
            line(x + 10, top_edge, x + 20, top_edge, stroke="#1e293b", stroke_width=2),
            line(x + 10, bottom_edge, x + 20, bottom_edge, stroke="#1e293b", stroke_width=2),
            text(
                x + 15, y + h + 15, f"a={a_um:.0f}μm",
                fill="#475569", font_size=10, anchor="middle",
            ),
            text(
                x + 15, y - 10, f"λ={lambda_nm:.0f}nm",
                fill=color, font_size=10, anchor="middle",
            ),
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
