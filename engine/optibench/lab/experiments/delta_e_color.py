"""Delta-E color difference experiment (CIE76, sRGB inputs)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import rect, svg_root, text


def _srgb_to_lab(r8: float, g8: float, b8: float) -> tuple[float, float, float]:
    def lin(v: float) -> float:
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    rl, gl, bl = lin(r8), lin(g8), lin(b8)
    x = 0.4124 * rl + 0.3576 * gl + 0.1805 * bl
    y = 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
    z = 0.0193 * rl + 0.1192 * gl + 0.9505 * bl
    # Normalize by D65 white.
    xn, yn, zn = x / 0.95047, y / 1.00000, z / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(xn), f(yn), f(zn)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def _delta_e76(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))


class DeltaEColorExperiment(OpticsExperiment):
    experiment_id = "delta-e-color"
    title = "色差 ΔE 实验与判读"
    description = (
        "选取两个 RGB 颜色，计算 CIE76 色差 ΔE，并对照行业经验"
        "阈值判断人眼是否可分辨。"
    )
    difficulty = "foundation"
    prerequisites = ["color-mixing"]
    linked_concepts = [
        "color-gamut",
        "color-temperature",
    ]
    linked_formulas = [
        "delta-e",
    ]
    learning_objectives = [
        "掌握 ΔE 的含义：CIELAB 空间中两颜色的欧氏距离。",
        "掌握行业经验判读：ΔE<1 不可辨、1–3 仔细看可辨、>5 一眼可见。",
        "理解为什么在 RGB 空间直接算距离不准确（需要感知均匀空间）。",
    ]
    parameters = [
        Parameter(name="r1", label="颜色A R",
                  type="float", default=220.0, min=0.0, max=255.0, step=5.0),
        Parameter(name="g1", label="颜色A G",
                  type="float", default=180.0, min=0.0, max=255.0, step=5.0),
        Parameter(name="b1", label="颜色A B",
                  type="float", default=140.0, min=0.0, max=255.0, step=5.0),
        Parameter(name="r2", label="颜色B R",
                  type="float", default=210.0, min=0.0, max=255.0, step=5.0),
        Parameter(name="g2", label="颜色B G",
                  type="float", default=175.0, min=0.0, max=255.0, step=5.0),
        Parameter(name="b2", label="颜色B B",
                  type="float", default=160.0, min=0.0, max=255.0, step=5.0),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        params = self.validate_params(params)
        c1 = tuple(float(params.get(k)) for k in ("r1", "g1", "b1"))
        c2 = tuple(float(params.get(k)) for k in ("r2", "g2", "b2"))

        lab1 = _srgb_to_lab(*c1)
        lab2 = _srgb_to_lab(*c2)
        delta_e = _delta_e76(lab1, lab2)

        verdict = (
            "不可分辨" if delta_e < 1.0
            else "仔细对比可辨" if delta_e < 3.0
            else "明显可辨" if delta_e < 5.0
            else "一眼可见"
        )

        svg = self._draw_svg(c1, c2, delta_e, verdict)

        return ExperimentResult(
            data={
                "lab_a": [round(v, 2) for v in lab1],
                "lab_b": [round(v, 2) for v in lab2],
                "delta_e_cie76": round(delta_e, 2),
                "verdict": verdict,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "ΔE 在 CIELAB（感知均匀）空间中定义；直接在 RGB 空间算欧氏距离会高估蓝区差异。",
                "显示面板出厂 ΔE 通常要求 < 2；印刷对色 < 1.5；ΔE > 5 属于明显偏色。",
                "更现代的 CIEDE2000 在饱和色与蓝色区修正了 CIE76 的偏差。",
            ],
        )

    def _draw_svg(self, c1, c2, delta_e: float, verdict: str) -> str:
        width, height = 640, 240
        fill_a = f"rgb({c1[0]:.0f},{c1[1]:.0f},{c1[2]:.0f})"
        fill_b = f"rgb({c2[0]:.0f},{c2[1]:.0f},{c2[2]:.0f})"
        children: list[str] = [
            text(width / 2 - 110, 60, "颜色 A", fill="#475569", font_size=12, anchor="middle"),
            text(width / 2 + 110, 60, "颜色 B", fill="#475569", font_size=12, anchor="middle"),
            rect(width / 2 - 170, 72, 120, 80, fill=fill_a, stroke="#94a3b8"),
            rect(width / 2 + 50, 72, 120, 80, fill=fill_b, stroke="#94a3b8"),
            text(width / 2 - 110, 172, f"#{int(c1[0]):02x}{int(c1[1]):02x}{int(c1[2]):02x}",
                 fill="#64748b", font_size=10, anchor="middle"),
            text(width / 2 + 110, 172, f"#{int(c2[0]):02x}{int(c2[1]):02x}{int(c2[2]):02x}",
                 fill="#64748b", font_size=10, anchor="middle"),
            text(width / 2, 208, f"ΔE(CIE76) = {delta_e:.2f}", fill="#0f172a",
                 font_size=16, anchor="middle"),
            text(width / 2, 228, f"判读：{verdict}", fill="#dc2626" if delta_e >= 3 else "#16a34a",
                 font_size=12, anchor="middle"),
        ]
        return svg_root(width, height, children)
