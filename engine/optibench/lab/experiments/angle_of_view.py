"""Angle of view experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.core.sensor import SENSOR_FORMAT_TABLE
from optibench.core.thin_lens import ThinLensCalculator
from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, polygon, svg_root, text


class AngleOfViewExperiment(OpticsExperiment):
    experiment_id = "angle-of-view"
    title = "视角与传感器尺寸实验"
    description = "给定焦距和传感器尺寸，观察水平、垂直、对角线视角的变化。"
    difficulty = "foundation"
    prerequisites = ["thin-lens"]
    linked_concepts = [
        "focal-length",
    ]
    linked_formulas = [
        "angle-of-view",
    ]
    learning_objectives = [
        "理解视角同时取决于焦距和传感器尺寸。",
        "比较同一焦距在不同传感器上的视野差异。",
    ]
    parameters = [
        Parameter(
            name="focal_length",
            label="焦距",
            type="float",
            default=50.0,
            min=5.0,
            max=400.0,
            step=1.0,
            unit="mm",
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
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f = float(params.get("focal_length", 50.0))
        fmt = str(params.get("sensor_format", "Full Frame"))
        size = SENSOR_FORMAT_TABLE.get(fmt)
        if size is None:
            raise ValueError(f"Unknown sensor format: {fmt}")

        calc = ThinLensCalculator()
        afov_h = calc.afov_from_sensor_focal(size.w, f)
        afov_v = calc.afov_from_sensor_focal(size.h, f)
        afov_d = calc.afov_from_sensor_focal(size.diag, f)

        svg = self._draw_svg(f, fmt, size, afov_h)

        return ExperimentResult(
            data={
                "focal_length_mm": f,
                "sensor_format": fmt,
                "sensor_width_mm": round(size.w, 2),
                "sensor_height_mm": round(size.h, 2),
                "sensor_diag_mm": round(size.diag, 2),
                "afov_horizontal_deg": round(afov_h, 2),
                "afov_vertical_deg": round(afov_v, 2),
                "afov_diagonal_deg": round(afov_d, 2),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "传感器越大，同一焦距的视角越宽。",
                "手机的小传感器需要很短的焦距才能获得与全画幅相似的视角。",
            ],
        )

    def _draw_svg(
        self,
        f: float,
        fmt: str,
        size,
        afov_h: float,
    ) -> str:
        width, height = 600, 260
        lens_x = 80
        sensor_x = width - 80
        cy = height // 2

        # Draw a field-of-view cone from the lens to the sensor edges.
        # Use a fixed sensor height in px; scale focal length visually.
        sensor_px_h = 120
        scale = sensor_px_h / size.h
        half_h_px = (size.h / 2) * scale
        focal_px = max(80, min(220, f * 1.5))
        lens_to_sensor_px = focal_px + 80

        lens_x = 80
        sensor_x = lens_x + lens_to_sensor_px

        children = [
            # Optical axis
            line(lens_x, cy, sensor_x + 40, cy, stroke="#94a3b8", dash="4"),
            # Lens
            line(lens_x, cy - 60, lens_x, cy + 60, stroke="#374151", stroke_width=4),
            text(lens_x - 10, cy + 80, "透镜", fill="#64748b", font_size=11, anchor="end"),
            # Sensor rectangle
            polygon(
                [
                    (sensor_x, cy - half_h_px),
                    (sensor_x, cy + half_h_px),
                    (sensor_x + 10, cy + half_h_px),
                    (sensor_x + 10, cy - half_h_px),
                ],
                fill="rgba(99,102,241,0.2)",
                stroke="#4f46e5",
            ),
            text(
                sensor_x,
                cy - half_h_px - 10,
                fmt,
                fill="#4f46e5",
                font_size=11,
                anchor="middle",
            ),
            # FOV rays
            line(
                lens_x, cy, sensor_x, cy - half_h_px,
                stroke="#2563eb", opacity=0.6, stroke_width=1.5,
            ),
            line(
                lens_x, cy, sensor_x, cy + half_h_px,
                stroke="#2563eb", opacity=0.6, stroke_width=1.5,
            ),
            # Angle arc
            self._angle_arc(lens_x, cy, focal_px, afov_h),
            # Stats
            text(
                width / 2,
                height - 25,
                (
                    f"f = {f:.0f} mm  |  {fmt}  |  "
                    f"水平 {afov_h:.1f}°  垂直 {self._afov(size.h, f):.1f}°  "
                    f"对角 {self._afov(size.diag, f):.1f}°"
                ),
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)

    def _afov(self, sensor_size: float, f: float) -> float:
        return 2 * math.degrees(math.atan(sensor_size / (2 * f)))

    def _angle_arc(self, cx: float, cy: float, radius: float, angle_deg: float) -> str:
        """Return an SVG path for an angle arc centered at (cx,cy) opening upward."""
        half = angle_deg / 2
        start_angle = -half
        end_angle = half
        # Convert to radians and compute end point for large/small arc flag
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        x1 = cx + radius * math.cos(start_rad)
        y1 = cy + radius * math.sin(start_rad)
        x2 = cx + radius * math.cos(end_rad)
        y2 = cy + radius * math.sin(end_rad)
        large_arc = 1 if angle_deg > 180 else 0
        return (
            f'<path d="M {x1:.1f} {y1:.1f} A {radius:.1f} {radius:.1f} 0 {large_arc} 1 '
            f'{x2:.1f} {y2:.1f}" fill="none" stroke="#f59e0b" stroke-width="2"/>'
        )
