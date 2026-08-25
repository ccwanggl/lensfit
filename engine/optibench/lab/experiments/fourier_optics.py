"""Fourier optics: numerical FFT of apertures demonstrates the FT pair."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, line, path, svg_root, text


class FourierOpticsExperiment(OpticsExperiment):
    experiment_id = "fourier-optics"
    title = "傅里叶光学变换实验"
    description = (
        "用数值 FFT 计算单缝/双缝/圆孔的远场衍射图样："
        "孔径函数与其夫琅禾费衍射图样正是一对傅里叶变换。"
    )
    difficulty = "advanced"
    prerequisites = ["single-slit-diffraction", "diffraction"]
    linked_concepts = [
        "fourier-transform-pair",
    ]
    linked_formulas = [
        "fourier-transform-optics",
        "angular-spectrum",
    ]
    learning_objectives = [
        "理解夫琅禾费衍射图样即孔径函数的傅里叶变换模平方。",
        "掌握矩形孔 ↔ sinc、圆孔 ↔ Airy（jinc）两对经典变换对。",
        "理解双缝图样 = 单缝包络 × 余弦干涉因子的频域乘积关系。",
    ]
    parameters = [
        Parameter(
            name="aperture_type",
            label="孔径类型",
            type="choice",
            default="slit",
            options=[
                {"value": "slit", "label": "单缝"},
                {"value": "double_slit", "label": "双缝"},
                {"value": "circle", "label": "圆孔"},
            ],
        ),
        Parameter(
            name="slit_width_px",
            label="缝宽（栅格数）",
            type="float",
            default=16.0,
            min=2.0,
            max=64.0,
            step=1.0,
        ),
        Parameter(
            name="slit_separation_px",
            label="双缝中心间距",
            type="float",
            default=64.0,
            min=8.0,
            max=192.0,
            step=4.0,
        ),
        Parameter(
            name="circle_radius_px",
            label="圆孔半径（栅格数）",
            type="float",
            default=24.0,
            min=4.0,
            max=96.0,
            step=1.0,
        ),
    ]

    _N = 512  # 1D sampling grid size for slit cases.

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        aperture = params.get("aperture_type", "slit")
        w = float(params.get("slit_width_px", 16.0))
        sep = float(params.get("slit_separation_px", 64.0))
        r = float(params.get("circle_radius_px", 24.0))

        if aperture == "circle":
            n2d = 256
            ax = np.arange(n2d) - n2d / 2
            xx, yy = np.meshgrid(ax, ax)
            aperture_field = (xx**2 + yy**2 <= r**2).astype(float)
            ft = np.fft.fftshift(np.fft.fft2(aperture_field))
            intensity = np.abs(ft) ** 2
            intensity /= intensity.max()
            center_row = intensity[n2d // 2]
            profile = center_row[n2d // 2 :]
            # First zero of numeric pattern vs theory x = 1.22·(N/2)/r in bins.
            below = profile < 0.02
            first_zero_idx = int(np.argmax(below)) if below.any() else len(profile) - 1
            svg = self._draw_profile(profile, "圆孔数值衍射剖面（半边）", "#8b5cf6")
            return ExperimentResult(
                data={
                    "aperture_type": aperture,
                    "grid_n2d": n2d,
                    "first_zero_bin_index": first_zero_idx,
                    "theory_first_zero_bin": round(1.22 * (n2d / 2) / r, 2),
                    "peak_normalized": 1.0,
                },
                svg=svg,
                warnings=[],
                learning_hints=[
                    "数值剖面的第一暗环位置与解析式 x₀ = 1.22·(N/2r) 一致——FFT 就是衍射。",
                    "增大圆孔半径 → 图样压缩：空间域越窄、频率域越宽的反比关系。",
                ],
            )

        # 1D slits.
        n = self._N
        grid = np.zeros(n)
        half_w = max(1.0, w / 2)
        center = n / 2
        grid[int(center - half_w): int(center + half_w)] = 1.0
        if aperture == "double_slit":
            off = sep / 2
            g2 = np.zeros(n)
            g2[int(center + off - half_w): int(center + off + half_w)] = 1.0
            g3 = np.zeros(n)
            g3[int(center - off - half_w): int(center - off + half_w)] = 1.0
            grid = g2 + g3

        ft = np.fft.fftshift(np.fft.fft(grid))
        intensity = np.abs(ft) ** 2
        intensity /= intensity.max()

        half = intensity[n // 2:]
        svg = self._draw_profile(half[: len(half) // 2], "数值远场强度剖面（半边）",
                                 "#f59e0b")

        num_zeros = int(np.sum((half[:-1] > 0.05) & (half[1:] <= 0.05)))
        return ExperimentResult(
            data={
                "aperture_type": aperture,
                "grid_n": n,
                "slit_width_px": w,
                "slit_separation_px": sep if aperture == "double_slit" else None,
                "crossing_minima_count": num_zeros,
                "theory_note": (
                    f"单缝：极小间隔 ∝ 1/{w:.0f}px；"
                    if aperture == "slit"
                    else f"双缝干涉因子周期 ∝ 1/{sep:.0f}px，包络由缝宽 {w:.0f}px 决定。"
                ),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "矩形函数的傅里叶变换是 sinc——单缝远场图样即 sinc²。",
                "双缝图样 = 单缝 sinc 包络 × 余弦条纹（频域卷积定理的可视化）。",
                "这里没有任何解析公式参与成像：图样完全由数值 FFT 生成。",
            ],
        )

    def _draw_profile(self, values, title: str, color: str) -> str:
        width, height = 640, 280
        ox, oy, span_x, span_y = 50.0, 26.0, 520.0, 180.0
        peak = float(values.max()) if hasattr(values, "max") else max(values)
        n = len(values)

        def px(i: int, v: float):
            return ox + i / (n - 1) * span_x, oy + span_y - v / peak * span_y

        pts = " ".join(f"{px(i, v)[0]:.1f},{px(i, v)[1]:.1f}" for i, v in enumerate(values))
        children = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
            path("M" + pts, fill="none", stroke=color, stroke_width=2),
            text(width / 2, oy + 14, title, fill="#334155", font_size=11, anchor="middle"),
            text(ox + span_x / 2, height - 30, "频率/角度坐标（相对单位）",
                 fill="#64748b", font_size=11, anchor="middle"),
            text(ox + span_x / 2, height - 12,
                 "强度 |FT{孔径}|²，峰值归一化", fill="#94a3b8", font_size=10, anchor="middle"),
        ]
        return svg_root(width, height, children)
