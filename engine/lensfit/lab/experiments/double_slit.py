"""Double-slit interference experiment."""

from __future__ import annotations

import math
from typing import Any

from lensfit.lab.base import ExperimentResult, OpticsExperiment, Parameter
from lensfit.lab.renderer import axis_x, axis_y, line, path, polygon, svg_root, text


class DoubleSlitExperiment(OpticsExperiment):
    experiment_id = "double-slit"
    title = "双缝干涉实验"
    description = "改变缝宽、缝间距和波长，观察双缝干涉条纹及其被单缝包络调制的现象。"
    difficulty = "intermediate"
    prerequisites = ["single-slit-diffraction", "polarization-malus"]
    linked_concepts = [
        "10-concepts/interference",
        "10-concepts/diffraction-limit",
        "10-concepts/衍射极限",
    ]
    linked_formulas = [
        "20-formulas/double-slit-fringe-spacing",
    ]
    learning_objectives = [
        "理解条纹间距 Δy = λL / d。",
        "观察缝间距越小，条纹越稀疏；缝间距越大，条纹越密集。",
        "认识单缝包络如何限制可见干涉条纹的数目。",
    ]
    parameters = [
        Parameter(
            name="slit_width_um",
            label="单缝宽度",
            type="float",
            default=20.0,
            min=1.0,
            max=200.0,
            step=1.0,
            unit="μm",
        ),
        Parameter(
            name="slit_separation_um",
            label="缝间距",
            type="float",
            default=100.0,
            min=10.0,
            max=1000.0,
            step=10.0,
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
        a_um = float(params.get("slit_width_um", 20.0))
        d_um = float(params.get("slit_separation_um", 100.0))
        lambda_nm = float(params.get("wavelength_nm", 550.0))
        l_m = float(params.get("screen_distance_m", 1.0))

        d_mm = d_um / 1000.0
        lambda_mm = lambda_nm * 1e-6

        # Fringe spacing on screen (small angle): Δy = λ L / d
        fringe_spacing_mm = (lambda_mm * l_m * 1000.0) / d_mm

        # Number of visible interference maxima within central diffraction envelope
        # Central envelope angular half-width ≈ λ/a; maxima angular spacing ≈ λ/d
        # N ≈ 2 floor(d/a) - 1 if d/a not integer, else 2 d/a - 1
        ratio = d_um / a_um
        if ratio <= 1:
            visible_maxima = 1
        else:
            visible_maxima = 2 * int(math.floor(ratio)) + 1

        svg = self._draw_svg(a_um, d_um, lambda_nm, l_m, fringe_spacing_mm)

        return ExperimentResult(
            data={
                "slit_width_um": a_um,
                "slit_separation_um": d_um,
                "wavelength_nm": lambda_nm,
                "screen_distance_m": l_m,
                "fringe_spacing_mm": round(fringe_spacing_mm, 4),
                "visible_maxima_in_envelope": visible_maxima,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "干涉条纹间距与缝间距成反比。",
                "单缝衍射包络的零点会抑制某些干涉极大，造成「缺失级次」。",
                "实验中条纹可见度受光源相干性和缝宽影响很大。",
            ],
        )

    def _draw_svg(
        self,
        a_um: float,
        d_um: float,
        lambda_nm: float,
        l_m: float,
        fringe_spacing_mm: float,
    ) -> str:
        width, height = 640, 320
        plot_x, plot_y = 60, 50
        plot_w, plot_h = 420, 180

        a_mm = a_um / 1000.0
        d_mm = d_um / 1000.0
        lambda_mm = lambda_nm * 1e-6

        # Plot range: a few central fringes, but at least the central envelope
        y_max_mm = max(5 * fringe_spacing_mm, 3 * (lambda_mm * l_m * 1000.0) / a_mm, 0.5)

        def envelope(y_mm: float) -> float:
            sin_theta = (y_mm / 1000.0) / l_m
            if abs(sin_theta) >= 1.0:
                return 0.0
            a_mm = a_um / 1000.0
            alpha = math.pi * a_mm * sin_theta / lambda_mm
            if abs(alpha) < 1e-9:
                return 1.0
            return (math.sin(alpha) / alpha) ** 2

        def interference(y_mm: float) -> float:
            sin_theta = (y_mm / 1000.0) / l_m
            beta = math.pi * d_mm * sin_theta / lambda_mm
            return math.cos(beta) ** 2

        def intensity(y_mm: float) -> float:
            return envelope(y_mm) * interference(y_mm)

        num_points = 400
        ys = [-y_max_mm + 2 * y_max_mm * i / (num_points - 1) for i in range(num_points)]
        intensities = [intensity(y) for y in ys]
        envelope_values = [envelope(y) for y in ys]

        def x_to_px(y):
            return plot_x + (y + y_max_mm) / (2 * y_max_mm) * plot_w

        def y_to_px(i):
            return plot_y + plot_h - i * plot_h

        curve = "M " + " L ".join(
            f"{x_to_px(y):.1f} {y_to_px(i):.1f}" for y, i in zip(ys, intensities)
        )
        envelope_curve = "M " + " L ".join(
            f"{x_to_px(y):.1f} {y_to_px(e):.1f}" for y, e in zip(ys, envelope_values)
        )

        children = [
            *axis_x(plot_x, plot_y + plot_h, plot_w, label="屏上位置 y (mm)"),
            *axis_y(plot_x, plot_y + plot_h, plot_h, label="相对强度"),
            path(envelope_curve, fill="none", stroke="#94a3b8", stroke_width=1.5),
            polygon(
                [(plot_x, plot_y + plot_h)]
                + [(x_to_px(y), y_to_px(i)) for y, i in zip(ys, intensities)]
                + [(plot_x + plot_w, plot_y + plot_h)],
                fill="rgba(37,99,235,0.15)",
                stroke="none",
            ),
            path(curve, fill="none", stroke="#2563eb", stroke_width=2),
            text(
                plot_x + plot_w + 10,
                plot_y + 20,
                f"Δy={fringe_spacing_mm:.2f} mm",
                fill="#2563eb",
                font_size=11,
            ),
            *self._slit_diagram(width - 110, plot_y, 80, a_um, d_um, lambda_nm),
            text(
                width / 2,
                height - 20,
                f"a={a_um:.0f} μm  d={d_um:.0f} μm  λ={lambda_nm:.0f} nm  L={l_m:.1f} m",
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)

    def _slit_diagram(
        self, x: float, y: float, h: float, a_um: float, d_um: float, lambda_nm: float
    ) -> list[str]:
        """Draw a simple double-slit aperture."""
        r, g, b = self._wavelength_to_rgb(lambda_nm)
        color = f"rgb({r},{g},{b})"
        # Visual scale: make slit width and separation fit in the box
        scale = min(0.3, 60 / d_um)
        a_px = max(2, a_um * scale)
        d_px = max(a_px + 4, d_um * scale)
        cx = x + 15
        cy = y + h / 2
        top_y = cy - d_px / 2
        bottom_y = cy + d_px / 2

        def bar(y0):
            return line(cx - 5, y0, cx + 5, y0, stroke="#1e293b", stroke_width=2)

        return [
            polygon(
                [(x, y), (x + 30, y), (x + 30, y + h), (x, y + h)],
                fill="#e2e8f0",
                stroke="#64748b",
            ),
            bar(y),
            bar(top_y - a_px / 2),
            bar(top_y + a_px / 2),
            bar(bottom_y - a_px / 2),
            bar(bottom_y + a_px / 2),
            bar(y + h),
            text(
                cx, y + h + 15, f"d={d_um:.0f}μm",
                fill="#475569", font_size=10, anchor="middle",
            ),
            text(
                cx, y - 10, f"λ={lambda_nm:.0f}nm",
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
