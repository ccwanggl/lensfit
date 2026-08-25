"""Illumination uniformity experiment (LED array over target plane)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import rect, svg_root, text


class IlluminationUniformityExperiment(OpticsExperiment):
    experiment_id = "illumination-uniformity"
    title = "照明均匀度实验"
    description = (
        "调整 LED 阵列的排布间距与安装高度，观察目标面辐照热图的"
        "均匀度（min/avg）如何变化——照明系统设计的核心指标。"
    )
    difficulty = "intermediate"
    prerequisites = []
    linked_concepts = [
        "均匀性",
        "illuminance",
    ]
    linked_formulas = [
        "illumination-uniformity",
    ]
    learning_objectives = [
        "掌握均匀度定义 U₀ = E_min / E_avg。",
        "理解距离平方反比与 cos⁴ 因子共同造成边缘压暗。",
        "理解「抬高光源 / 加大阵列」能换均匀度，但牺牲峰值照度。",
    ]
    parameters = [
        Parameter(
            name="led_count_per_side",
            label="每边 LED 数",
            type="float",
            default=4.0,
            min=2.0,
            max=8.0,
            step=1.0,
        ),
        Parameter(
            name="array_pitch_mm",
            label="LED 间距",
            type="float",
            default=40.0,
            min=15.0,
            max=120.0,
            step=5.0,
            unit="mm",
        ),
        Parameter(
            name="working_distance_mm",
            label="工作距离",
            type="float",
            default=120.0,
            min=40.0,
            max=400.0,
            step=10.0,
            unit="mm",
        ),
        Parameter(
            name="target_half_mm",
            label="目标半宽",
            type="float",
            default=80.0,
            min=30.0,
            max=150.0,
            step=10.0,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        n_side = int(float(params.get("led_count_per_side", 4)))
        pitch_mm = float(params.get("array_pitch_mm", 40))
        height_mm = float(params.get("working_distance_mm", 120))
        half_mm = float(params.get("target_half_mm", 80))

        led_positions = []
        start = -(n_side - 1) / 2 * pitch_mm
        for i in range(n_side):
            for j in range(n_side):
                led_positions.append((start + i * pitch_mm, start + j * pitch_mm))

        grid_n = 21
        cell_px = 300 / grid_n
        e_map: list[list[float]] = []
        for gy in range(grid_n):
            row = []
            y_mm = -half_mm + gy * (2 * half_mm) / (grid_n - 1)
            for gx in range(grid_n):
                x_mm = -half_mm + gx * (2 * half_mm) / (grid_n - 1)
                e = 0.0
                for lx, ly in led_positions:
                    dx, dy = x_mm - lx, y_mm - ly
                    r2 = dx * dx + dy * dy + height_mm * height_mm
                    cos4 = (height_mm * height_mm / r2) ** 2
                    e += cos4 / r2
                row.append(e)
            e_map.append(row)

        flat = [v for row in e_map for v in row]
        e_min, e_max = min(flat), max(flat)
        e_avg = sum(flat) / len(flat)
        uniformity = e_min / e_avg if e_avg > 0 else 0.0

        svg = self._draw_svg(e_map, grid_n, cell_px, uniformity)

        return ExperimentResult(
            data={
                "led_count": len(led_positions),
                "array_pitch_mm": pitch_mm,
                "working_distance_mm": height_mm,
                "uniformity_min_over_avg": round(uniformity, 3),
                "relative_max_edge_drop_pct": round((1 - e_min / e_max) * 100, 1),
                "grade": "优" if uniformity > 0.9 else "良" if uniformity > 0.75 else "需优化",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "边缘暗化来自两个因素叠加：距离平方反比 + 大入射角的 cos⁴ 衰减。",
                "工程手段：抬高光源、扩大阵列、加漫射板，或直接用同轴/穹顶照明。",
                "检测系统中 U₀ < 0.75 时，阈值分割的全局阈值将不可靠。",
            ],
        )

    def _draw_svg(self, e_map, grid_n: int, cell_px: float, uniformity: float) -> str:
        width, height = 640, 320
        ox, oy = 40.0, 20.0
        flat = [v for row in e_map for v in row]
        lo, hi = min(flat), max(flat)

        def color(v: float) -> str:
            frac = (v - lo) / (hi - lo) if hi > lo else 1.0
            c = int(40 + 180 * frac)
            return f"rgb({c},{int(60+140*frac)},255)"

        children: list[str] = []
        for gy in range(grid_n):
            for gx in range(grid_n):
                children.append(
                    rect(ox + gx * cell_px, oy + gy * cell_px,
                         cell_px + 0.5, cell_px + 0.5, fill=color(e_map[gy][gx]))
                )

        verdict_color = "#16a34a" if uniformity > 0.9 else "#b45309" if uniformity > 0.75 else "#dc2626"
        children += [
            text(ox + 300 + 24, oy + 30,
                 f"U₀ = Emin/Eavg = {uniformity:.2f}", fill="#0f172a", font_size=13),
            text(ox + 300 + 24, oy + 54,
                 f"评级：{'优' if uniformity>0.9 else '良' if uniformity>0.75 else '需优化'}",
                 fill=verdict_color, font_size=13),
            text(ox + 300 + 24, oy + 86,
                 "提高手段：", fill="#334155", font_size=11),
            text(ox + 300 + 24, oy + 104, "· 抬高工作距离", fill="#64748b", font_size=11),
            text(ox + 300 + 24, oy + 122, "· 增大阵列尺寸/密度", fill="#64748b", font_size=11),
            text(ox + 300 + 24, oy + 140, "· 加漫射板（损失效率）", fill="#64748b", font_size=11),
        ]
        return svg_root(width, height, children)
