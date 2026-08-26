"""Binocular parallax and depth perception experiment."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, line, svg_root, text


class ParallaxExperiment(OpticsExperiment):
    experiment_id = "parallax"
    title = "双目视差与深度实验"
    description = (
        "改变基线长度与目标距离，观察同一目标在左右相机中的视差"
        "如何随距离反比变化——立体视觉测距的核心几何。"
    )
    difficulty = "foundation"
    prerequisites = ["thin-lens"]
    linked_concepts = [
        "视差",
    ]
    linked_formulas: list[str] = []
    learning_objectives = [
        "掌握视差定义：同一目标在左右像面上的水平位置差。",
        "掌握深度公式 Z = f·B / d（d 为视差像素数）。",
        "理解视差与距离成反比：越远视差越小，测距精度越差。",
    ]
    parameters = [
        Parameter(
            name="baseline_mm",
            label="基线长度 B",
            type="float",
            default=120.0,
            min=20.0,
            max=400.0,
            step=10.0,
            unit="mm",
        ),
        Parameter(
            name="focal_mm",
            label="焦距",
            type="float",
            default=8.0,
            min=2.0,
            max=50.0,
            step=0.5,
            unit="mm",
        ),
        Parameter(
            name="depth_m",
            label="目标距离 Z",
            type="float",
            default=2.0,
            min=0.5,
            max=20.0,
            step=0.1,
            unit="m",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        baseline_m = float(params.get("baseline_mm", 120.0)) * 1e-3
        f_m = float(params.get("focal_mm", 8.0)) * 1e-3
        depth_m = float(params.get("depth_m", 2.0))

        disparity_m = baseline_m * f_m / depth_m
        disparity_px = disparity_m / (3.3e-6)  # assume 3.3 µm pixel for px count

        svg = self._draw_svg(baseline_m, depth_m, disparity_m * 1e3)

        return ExperimentResult(
            data={
                "baseline_mm": round(baseline_m * 1e3, 1),
                "focal_mm": round(f_m * 1e3, 1),
                "depth_m": depth_m,
                "disparity_mm": round(disparity_m * 1e3, 3),
                "disparity_px_3p3um": round(disparity_px, 1),
                "law": "Z = f·B/d，视差与距离成反比",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "距离翻倍 → 视差减半：远处的深度测量天然不精确。",
                "增大基线可提升远距分辨率，但近处会因视差过大丢失共同视野。",
                "人眼双目基线约 65 mm，因此人眼的立体视觉有效距离只有几米。",
            ],
        )

    def _draw_svg(self, baseline_m: float, depth_m: float, disparity_mm: float) -> str:
        width, height = 640, 300
        cx, cy = width / 2, 70.0

        # Scene scale: map depth to vertical pixels.
        scene_h = 170.0
        z_px = (depth_m / 20.0) * scene_h + 30
        b_half_px = min(90.0, baseline_m * 1e3 / 4)
        target_r = 10.0
        disparity_px = disparity_mm * 1e-3 / 3.3e-6

        children = [
            # Cameras.
            circle(cx - b_half_px, cy, 9, fill="#3b82f6"),
            circle(cx + b_half_px, cy, 9, fill="#dc2626"),
            text(cx - b_half_px, cy - 16, "L", fill="#3b82f6", font_size=12, anchor="middle"),
            text(cx + b_half_px, cy - 16, "R", fill="#dc2626", font_size=12, anchor="middle"),
            # Rays to target.
            line(cx - b_half_px, cy, cx - 14, cy + z_px, stroke="#3b82f6"),
            line(cx + b_half_px, cy, cx - 14, cy + z_px, stroke="#dc2626"),
            line(cx - b_half_px, cy, cx + 14, cy + z_px, stroke="#3b82f6"),
            line(cx + b_half_px, cy, cx + 14, cy + z_px, stroke="#dc2626"),
            # Target.
            circle(cx, cy + z_px, target_r, fill="#f59e0b", stroke="#b45309"),
            text(cx + 18, cy + z_px + 4, f"目标 @ {depth_m:.1f} m", fill="#b45309", font_size=11),
            # Baseline bar.
            line(cx - b_half_px, cy - 26, cx + b_half_px, cy - 26, stroke="#475569"),
            text(cx, cy - 32, f"B = {baseline_m*1e3:.0f} mm", fill="#475569",
                 font_size=11, anchor="middle"),
            text(width / 2, height - 34,
                 f"视差 d = f·B/Z = {disparity_mm:.2f} mm ≈ {disparity_px:.0f} px (3.3 µm 像元)",
                 fill="#475569", font_size=11, anchor="middle"),
            text(width / 2, height - 14,
                 "蓝/红射线与目标连线的夹角即视差角——两像面位置差就是它的直接体现",
                 fill="#94a3b8", font_size=10, anchor="middle"),
        ]
        return svg_root(width, height, children)
