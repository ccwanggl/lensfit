"""Depth of field experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.core.sensor import SENSOR_FORMAT_TABLE
from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, polygon, svg_root, text


class DepthOfFieldExperiment(OpticsExperiment):
    experiment_id = "depth-of-field"
    title = "景深实验"
    description = "给定焦距、光圈、对焦距离和传感器参数，计算景深的前后界限和超焦距。"
    difficulty = "foundation"
    prerequisites = ["thin-lens", "magnification-scale"]
    linked_concepts = [
        "10-concepts/depth-of-field",
        "10-concepts/f-number",
    ]
    linked_formulas = [
        "20-formulas/depth-of-field",
        "20-formulas/hyperfocal-distance",
    ]
    learning_objectives = [
        "理解光圈、焦距和对焦距离如何共同影响景深。",
        "认识超焦距的意义及其与景深远/近界的关系。",
    ]
    parameters = [
        Parameter(
            name="focal_length",
            label="焦距",
            type="float",
            default=50.0,
            min=5.0,
            max=200.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="f_number",
            label="光圈值",
            type="float",
            default=2.8,
            min=1.0,
            max=22.0,
            step=0.1,
        ),
        Parameter(
            name="focus_distance_m",
            label="对焦距离",
            type="float",
            default=2.0,
            min=0.1,
            max=50.0,
            step=0.1,
            unit="m",
        ),
        Parameter(
            name="sensor_format",
            label="传感器尺寸",
            type="choice",
            default="Full Frame",
            options=[
                {"value": fmt, "label": fmt}
                for fmt in SENSOR_FORMAT_TABLE.keys()
            ],
        ),
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
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f = float(params.get("focal_length", 50.0))
        n = float(params.get("f_number", 2.8))
        s_m = float(params.get("focus_distance_m", 2.0))
        fmt = str(params.get("sensor_format", "Full Frame"))
        pixel_um = float(params.get("pixel_size_um", 3.45))

        size = SENSOR_FORMAT_TABLE.get(fmt)
        if size is None:
            raise ValueError(f"Unknown sensor format: {fmt}")

        sensor_diag = math.hypot(size.w, size.h)
        # CoC: standard print CoC vs pixel-limited CoC, conservative (smaller)
        coc_diag = sensor_diag / 1730.0
        coc_pixel = (pixel_um * 2.0) / 1000.0
        coc = min(coc_diag, coc_pixel)

        # Hyperfocal distance in metres
        hyperfocal_m = ((f * f) / (n * coc)) / 1000.0 + f / 1000.0
        s = s_m

        # Near limit (always finite for finite focus distance)
        near_m = (hyperfocal_m * s) / (hyperfocal_m + s)

        # Far limit: infinity when focused at or beyond hyperfocal
        if s >= hyperfocal_m - 1e-9:
            far_m = None
            dof_m = None
        else:
            far_m = (hyperfocal_m * s) / (hyperfocal_m - s)
            dof_m = far_m - near_m

        warnings: list[str] = []
        if coc == coc_pixel:
            warnings.append(
                "当前使用像元受限的弥散圆，景深估计比传统打印标准更严格。"
            )

        svg = self._draw_svg(s_m, near_m, far_m, hyperfocal_m)

        return ExperimentResult(
            data={
                "focal_length_mm": f,
                "f_number": n,
                "focus_distance_m": round(s, 3),
                "sensor_format": fmt,
                "coc_mm": round(coc, 4),
                "hyperfocal_m": round(hyperfocal_m, 3),
                "near_limit_m": round(near_m, 3),
                "far_limit_m": round(far_m, 3) if far_m is not None else None,
                "dof_total_m": round(dof_m, 3) if dof_m is not None else None,
            },
            svg=svg,
            warnings=warnings,
            learning_hints=[
                "光圈越小（F# 越大），景深越大。",
                "对焦距离越远，景深越大；对焦到超焦距时，远景可延伸到无穷远。",
                "长焦距会显著压缩景深。",
            ],
        )

    def _draw_svg(
        self,
        focus_m: float,
        near_m: float,
        far_m: float | None,
        hyperfocal_m: float,
    ) -> str:
        width, height = 640, 260
        lens_x = 60
        cy = height // 2

        # Choose a scale that fits near, focus, and either far or hyperfocal
        max_m = max(focus_m, near_m, far_m or focus_m * 2, hyperfocal_m, 1.0)
        scale = (width - 120) / max_m

        focus_x = lens_x + focus_m * scale
        near_x = lens_x + near_m * scale
        hyper_x = lens_x + hyperfocal_m * scale
        far_x = lens_x + (far_m * scale) if far_m is not None else None

        # DOF shaded region
        dof_poly = [
            (near_x, cy - 40),
            (far_x if far_x is not None else width - 40, cy - 40),
            (far_x if far_x is not None else width - 40, cy + 40),
            (near_x, cy + 40),
        ]

        children = [
            # Optical axis
            line(lens_x - 20, cy, width - 20, cy, stroke="#94a3b8", dash="4"),
            # Lens
            line(lens_x, cy - 50, lens_x, cy + 50, stroke="#374151", stroke_width=4),
            text(lens_x, cy + 70, "透镜", fill="#64748b", font_size=11, anchor="middle"),
            # DOF region
            polygon(dof_poly, fill="rgba(16,185,129,0.15)", stroke="none"),
            # Near limit
            line(near_x, cy - 45, near_x, cy + 45, stroke="#10b981", stroke_width=2),
            text(
                near_x, cy - 55, f"近界 {near_m:.2f} m",
                fill="#10b981", font_size=10, anchor="middle",
            ),
            # Focus plane
            line(focus_x, cy - 55, focus_x, cy + 55, stroke="#2563eb", stroke_width=2, dash="4"),
            text(
                focus_x, cy - 65, f"对焦 {focus_m:.2f} m",
                fill="#2563eb", font_size=10, anchor="middle",
            ),
            # Far limit or infinity
            *(
                [
                    line(far_x, cy - 45, far_x, cy + 45, stroke="#10b981", stroke_width=2),
                    text(
                        far_x, cy - 55, f"远界 {far_m:.2f} m",
                        fill="#10b981", font_size=10, anchor="middle",
                    ),
                ]
                if far_x is not None
                else [
                    text(width - 45, cy - 45, "远界 ∞", fill="#10b981", font_size=11, anchor="end"),
                ]
            ),
            # Hyperfocal marker
            line(hyper_x, cy - 30, hyper_x, cy + 30, stroke="#f59e0b", stroke_width=1),
            text(
                hyper_x, cy + 45, f"超焦距 {hyperfocal_m:.2f} m",
                fill="#b45309", font_size=10, anchor="middle",
            ),
            # Legend
            text(
                width / 2,
                height - 25,
                "绿色区域为可接受清晰范围，蓝色虚线为对焦平面，橙色线为超焦距位置",
                fill="#475569",
                font_size=11,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)
