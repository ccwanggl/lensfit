"""Spectral color mixing experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, polygon, svg_root, text


class ColorMixingExperiment(OpticsExperiment):
    experiment_id = "color-mixing"
    title = "光谱混色实验"
    description = "混合两种单色光，观察合成光谱和感知颜色。"
    difficulty = "foundation"
    linked_concepts = [
        "spectral-power-distribution",
        "color-temperature",
        "chromaticity-diagram",
    ]
    learning_objectives = [
        "理解颜色是光谱分布在人眼中的综合感知。",
        "观察两种单色光混合后如何产生新的色相。",
    ]
    parameters = [
        Parameter(
            name="wavelength_a_nm",
            label="光源 A 波长",
            type="float",
            default=450.0,
            min=380.0,
            max=700.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="intensity_a",
            label="光源 A 强度",
            type="float",
            default=1.0,
            min=0.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="wavelength_b_nm",
            label="光源 B 波长",
            type="float",
            default=620.0,
            min=380.0,
            max=700.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="intensity_b",
            label="光源 B 强度",
            type="float",
            default=1.0,
            min=0.0,
            max=1.0,
            step=0.05,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        wa = float(params.get("wavelength_a_nm", 450.0))
        ia = float(params.get("intensity_a", 1.0))
        wb = float(params.get("wavelength_b_nm", 620.0))
        ib = float(params.get("intensity_b", 1.0))

        ra, ga, ba = self._wavelength_to_rgb(wa)
        rb, gb, bb = self._wavelength_to_rgb(wb)
        total = ia + ib
        mixed_r = min(255, int((ra * ia + rb * ib) / max(total, 0.001)))
        mixed_g = min(255, int((ga * ia + gb * ib) / max(total, 0.001)))
        mixed_b = min(255, int((ba * ia + bb * ib) / max(total, 0.001)))

        svg = self._draw_svg(wa, ia, wb, ib, (mixed_r, mixed_g, mixed_b))

        return ExperimentResult(
            data={
                "wavelength_a_nm": wa,
                "intensity_a": ia,
                "wavelength_b_nm": wb,
                "intensity_b": ib,
                "mixed_rgb": [mixed_r, mixed_g, mixed_b],
                "mixed_hex": f"#{mixed_r:02x}{mixed_g:02x}{mixed_b:02x}",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "人眼通过 LMS 三种视锥细胞把光谱积分成三色信号。",
                "不同光谱可以有相同的颜色感知（同色异谱）。",
            ],
        )

    def _draw_svg(
        self,
        wa: float,
        ia: float,
        wb: float,
        ib: float,
        mixed: tuple[int, int, int],
    ) -> str:
        width, height = 640, 320
        ra, ga, ba = self._wavelength_to_rgb(wa)
        rb, gb, bb = self._wavelength_to_rgb(wb)
        color_a = f"rgba({ra},{ga},{ba},{0.3 + 0.7 * ia})"
        color_b = f"rgba({rb},{gb},{bb},{0.3 + 0.7 * ib})"
        mixed_color = f"rgb({mixed[0]},{mixed[1]},{mixed[2]})"

        x_min, x_max = 380, 700

        def gaussian(x, center, amp, sigma=12):
            return amp * math.exp(-((x - center) ** 2) / (2 * sigma ** 2))

        xs = list(range(x_min, x_max + 1, 5))
        ys_a = [gaussian(x, wa, ia * 100) for x in xs]
        ys_b = [gaussian(x, wb, ib * 100) for x in xs]
        ys_sum = [ys_a[i] + ys_b[i] for i in range(len(xs))]

        plot_x, plot_y = 50, 50
        plot_w, plot_h = 420, 150

        def x_to_px(x):
            return plot_x + (x - x_min) / (x_max - x_min) * plot_w

        def y_to_px(y):
            return plot_y + plot_h - y

        def make_path(ys):
            pts = [f"{x_to_px(x):.1f} {y_to_px(y):.1f}" for x, y in zip(xs, ys)]
            return "M " + " L ".join(pts)

        path_a = make_path(ys_a)
        path_b = make_path(ys_b)
        path_sum = make_path(ys_sum)

        children = [
            # Axis
            *axis_x(plot_x, plot_y + plot_h, plot_w, label="波长 (nm)"),
            *axis_y(plot_x, plot_y + plot_h, plot_h, label="相对强度"),
            # SPD curves
            f'<path d="{path_a}" fill="none" stroke="{color_a}" stroke-width="2"/>',
            f'<path d="{path_b}" fill="none" stroke="{color_b}" stroke-width="2"/>',
            (
                f'<path d="{path_sum}" fill="none" stroke="#374151" '
                f'stroke-width="2" stroke-dasharray="3"/>'
            ),
            # Legend
            polygon(
                [
                    (plot_x + plot_w + 20, plot_y),
                    (plot_x + plot_w + 60, plot_y),
                    (plot_x + plot_w + 60, plot_y + 20),
                    (plot_x + plot_w + 20, plot_y + 20),
                ],
                fill=color_a,
                stroke="#374151",
            ),
            text(plot_x + plot_w + 70, plot_y + 15, "光源 A", fill="#475569", font_size=11),
            polygon(
                [
                    (plot_x + plot_w + 20, plot_y + 30),
                    (plot_x + plot_w + 60, plot_y + 30),
                    (plot_x + plot_w + 60, plot_y + 50),
                    (plot_x + plot_w + 20, plot_y + 50),
                ],
                fill=color_b,
                stroke="#374151",
            ),
            text(plot_x + plot_w + 70, plot_y + 45, "光源 B", fill="#475569", font_size=11),
            # Mixed color swatch
            polygon(
                [
                    (plot_x + plot_w + 20, plot_y + 80),
                    (plot_x + plot_w + 140, plot_y + 80),
                    (plot_x + plot_w + 140, plot_y + 160),
                    (plot_x + plot_w + 20, plot_y + 160),
                ],
                fill=mixed_color,
                stroke="#374151",
            ),
            text(
                plot_x + plot_w + 80,
                plot_y + 180,
                "混合色感知",
                fill="#475569",
                font_size=11,
                anchor="middle",
            ),
            text(
                plot_x + plot_w + 80,
                plot_y + 200,
                f"#{mixed[0]:02x}{mixed[1]:02x}{mixed[2]:02x}",
                fill="#475569",
                font_size=10,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)

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
