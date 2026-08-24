"""Nyquist sampling and aliasing experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, circle, line, path, svg_root, text
from optibench.visualization.mtf import MtfPlotData


class NyquistSamplingExperiment(OpticsExperiment):
    experiment_id = "nyquist-sampling"
    title = "奈奎斯特采样与混叠实验"
    description = "比较镜头 MTF50 与传感器奈奎斯特频率，判断是否存在混叠风险或过度采样。"
    difficulty = "intermediate"
    prerequisites = ["diffraction", "magnification-scale"]
    linked_concepts = [
        "10-concepts/nyquist-frequency",
        "10-concepts/奈奎斯特频率",
        "10-concepts/aliasing",
        "10-concepts/混叠",
    ]
    linked_formulas = [
        "20-formulas/nyquist-frequency",
        "20-formulas/oversampling-ratio",
    ]
    learning_objectives = [
        "理解传感器奈奎斯特频率是它能无歧义记录的最高空间频率。",
        "认识镜头 MTF50 超过奈奎斯特频率时会出现混叠。",
        "了解过度采样与欠采样的权衡。",
    ]
    parameters = [
        Parameter(
            name="pixel_size_um",
            label="像元尺寸",
            type="float",
            default=3.45,
            min=0.5,
            max=20.0,
            step=0.1,
            unit="μm",
        ),
        Parameter(
            name="lens_mtf50_lpmm",
            label="镜头 MTF50",
            type="float",
            default=80.0,
            min=10.0,
            max=300.0,
            step=5.0,
            unit="lp/mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        pixel_um = float(params.get("pixel_size_um", 3.45))
        mtf50 = float(params.get("lens_mtf50_lpmm", 80.0))

        data = MtfPlotData(mtf50, pixel_um).generate()
        nyquist = data["detector_nyquist_lpmm"]
        ratio = mtf50 / nyquist if nyquist else 0.0

        if ratio > 1.0:
            status = "混叠风险"
            status_color = "#dc2626"
        elif ratio > 0.5:
            status = "匹配良好"
            status_color = "#10b981"
        else:
            status = "过度采样"
            status_color = "#2563eb"

        warnings: list[str] = []
        if ratio > 1.0:
            warnings.append(
                "镜头 MTF50 高于传感器奈奎斯特频率，高对比度细节可能产生混叠。"
            )

        svg = self._draw_svg(data, ratio, status, status_color)

        return ExperimentResult(
            data={
                "pixel_size_um": pixel_um,
                "lens_mtf50_lpmm": mtf50,
                "detector_nyquist_lpmm": round(nyquist, 2) if nyquist else None,
                "oversampling_ratio": round(ratio, 3),
                "status": status,
            },
            svg=svg,
            warnings=warnings,
            learning_hints=[
                "奈奎斯特频率 = 1 / (2 × 像元尺寸)。",
                "当镜头 MTF50 ≈ 奈奎斯特频率时，系统匹配最佳。",
                "工业视觉常取 0.5–1.0 个像素/特征作为可分辨条件。",
            ],
        )

    def _draw_svg(
        self,
        data: dict[str, Any],
        ratio: float,
        status: str,
        status_color: str,
    ) -> str:
        width, height = 640, 320
        plot_x, plot_y = 60, 40
        plot_w, plot_h = 360, 180

        nyquist = data["detector_nyquist_lpmm"]
        mtf50 = data["lens_mtf50_lpmm"]
        points = data["points"]

        max_freq = max(p["frequency_lpmm"] for p in points)

        def x_to_px(f):
            return plot_x + (f / max_freq) * plot_w

        def y_to_px(mtf):
            return plot_y + plot_h - mtf * plot_h

        # MTF curve path
        mtf_path = "M " + " L ".join(
            f"{x_to_px(p['frequency_lpmm']):.1f} {y_to_px(p['mtf']):.1f}"
            for p in points
        )

        # Nyquist line x position
        nq_x = x_to_px(nyquist)

        children = [
            *axis_x(plot_x, plot_y + plot_h, plot_w, label="空间频率 (lp/mm)"),
            *axis_y(plot_x, plot_y + plot_h, plot_h, label="MTF"),
            path(mtf_path, fill="none", stroke="#2563eb", stroke_width=2),
            line(nq_x, plot_y, nq_x, plot_y + plot_h, stroke="#dc2626", dash="4"),
            text(
                nq_x,
                plot_y - 10,
                f"奈奎斯特 {nyquist:.1f} lp/mm",
                fill="#dc2626",
                font_size=10,
                anchor="middle",
            ),
            text(
                x_to_px(mtf50),
                y_to_px(0.5) - 10,
                f"MTF50 = {mtf50:.1f}",
                fill="#2563eb",
                font_size=10,
                anchor="middle",
            ),
            # Status badge
            text(
                plot_x + plot_w + 20,
                plot_y + 40,
                status,
                fill=status_color,
                font_size=14,
                anchor="start",
            ),
            text(
                plot_x + plot_w + 20,
                plot_y + 65,
                f"ratio = {ratio:.2f}",
                fill="#475569",
                font_size=11,
                anchor="start",
            ),
            # Mini aliasing diagram on the right
            *self._aliasing_diagram(
                plot_x + plot_w + 20,
                plot_y + 90,
                140,
                80,
                ratio,
            ),
        ]

        return svg_root(width, height, children)

    def _aliasing_diagram(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        ratio: float,
    ) -> list[str]:
        """Draw a small signal-vs-samples diagram."""
        # Show a high-frequency sine being sampled; if ratio > 1 the sampled
        # points reconstruct a lower-frequency alias.
        elements = []
        # Signal frequency in radians across the width
        freq = 3.0 * max(ratio, 1.0)
        pts = []
        num_samples = 8
        for i in range(num_samples + 1):
            px = x + (i / num_samples) * w
            py_signal = y + h / 2 - (h / 3) * math.sin(freq * i / num_samples * 2 * math.pi)
            pts.append((px, py_signal))

        # Sample points
        for px, py in pts:
            elements.append(circle(px, py, 3, fill="#dc2626", stroke="none"))

        # Reconstructed alias if ratio > 1
        if ratio > 1.0:
            alias_freq = freq - 1.0  # simplified alias visualization
            alias_pts = []
            for i in range(num_samples + 1):
                px = x + (i / num_samples) * w
                py = y + h / 2 - (h / 3) * math.sin(alias_freq * i / num_samples * 2 * math.pi)
                alias_pts.append((px, py))
            d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in alias_pts)
            elements.append(path(d, fill="none", stroke="#f59e0b", stroke_width=2))
            text(
                x + w / 2,
                y + h + 15,
                "高频信号被采样成低频假影",
                fill="#b45309",
                font_size=9,
                anchor="middle",
            )
        else:
            text(
                x + w / 2,
                y + h + 15,
                "采样点可还原原信号",
                fill="#10b981",
                font_size=9,
                anchor="middle",
            )

        return elements
