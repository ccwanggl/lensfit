"""Thin-lens imaging experiment."""

from __future__ import annotations

from typing import Any

from lensfit.lab.base import ExperimentResult, OpticsExperiment, Parameter
from lensfit.lab.renderer import arrow, circle, line, svg_root, text


class ThinLensExperiment(OpticsExperiment):
    experiment_id = "thin-lens"
    title = "薄透镜成像实验"
    description = "改变焦距和物距，观察像距、放大倍率和光路图的变化。"
    difficulty = "foundation"
    linked_concepts = [
        "10-concepts/focal-length",
        "20-formulas/thin-lens-gauss",
        "10-concepts/焦距",
    ]
    learning_objectives = [
        "理解 1/f = 1/u + 1/v 的物像关系。",
        "观察物距接近焦距时像距趋向无穷远。",
        "认识放大率与物距、焦距的关系。",
    ]
    parameters = [
        Parameter(
            name="focal_length",
            label="焦距",
            type="float",
            default=50.0,
            min=10.0,
            max=200.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="object_distance",
            label="物距",
            type="float",
            default=100.0,
            min=20.0,
            max=500.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="object_height",
            label="物高",
            type="float",
            default=30.0,
            min=5.0,
            max=100.0,
            step=1.0,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f = float(params.get("focal_length", 50.0))
        u = float(params.get("object_distance", 100.0))
        h_o = float(params.get("object_height", 30.0))

        warnings: list[str] = []

        # Avoid singularity at u == f
        if abs(u - f) < 0.05:
            u = f + 0.05
            warnings.append("物距过于接近焦距，已做微小偏移以避免除零。")

        v = (f * u) / (u - f)
        m = -v / u
        h_i = h_o * m
        image_type = "实像" if v > 0 else "虚像"

        if v < 0:
            warnings.append("当前成虚像，屏幕无法承接，需从透镜另一侧观察。")

        svg = self._draw_svg(u, v, f, h_o, h_i)

        return ExperimentResult(
            data={
                "focal_length_mm": f,
                "object_distance_mm": u,
                "object_height_mm": h_o,
                "image_distance_mm": round(v, 2),
                "magnification": round(m, 3),
                "image_height_mm": round(h_i, 2),
                "image_type": image_type,
            },
            svg=svg,
            warnings=warnings,
            learning_hints=[
                "当物距 u > 2f 时，成倒立缩小实像。",
                "当 f < u < 2f 时，成倒立放大实像。",
                "当 u < f 时，成正立放大虚像。",
            ],
        )

    def _draw_svg(self, u: float, v: float, f: float, h_o: float, h_i: float) -> str:
        width, height = 640, 320
        cx, cy = width // 2, height // 2
        max_dist = max(abs(u), abs(v), 2 * f, 100.0)
        scale = (width / 2 - 80) / max_dist

        lens_x = cx
        obj_x = lens_x - u * scale
        img_x = lens_x + v * scale
        # Scale object/image heights so they always fit vertically
        height_scale = min(scale * 0.6, (cy - 70) / max(h_o, abs(h_i), 1.0))
        obj_top = cy - h_o * height_scale
        img_top = cy - h_i * height_scale

        focal_img_x = lens_x + f * scale
        focal_obj_x = lens_x - f * scale

        children = [
            # Optical axis
            line(20, cy, width - 20, cy, stroke="#94a3b8", dash="4"),
            # Lens
            line(lens_x, cy - 60, lens_x, cy + 60, stroke="#374151", stroke_width=4),
            text(lens_x + 8, cy + 80, "透镜", fill="#64748b", font_size=12),
            # Focal points
            circle(focal_obj_x, cy, 3, fill="#f59e0b", stroke="none"),
            text(focal_obj_x - 4, cy + 18, "F", fill="#b45309", font_size=10, anchor="middle"),
            circle(focal_img_x, cy, 3, fill="#f59e0b", stroke="none"),
            text(focal_img_x - 4, cy + 18, "F", fill="#b45309", font_size=10, anchor="middle"),
            # Object arrow
            arrow(obj_x, cy, obj_x, obj_top, color="#2563eb", stroke_width=2),
            text(obj_x - 10, cy - 10, "物", fill="#2563eb", font_size=11, anchor="end"),
            # Image arrow
            arrow(img_x, cy, img_x, img_top, color="#dc2626", stroke_width=2),
            text(img_x + 10, cy - 10, "像", fill="#dc2626", font_size=11),
            # Principal rays
            # Ray 1: parallel -> focal point on image side
            line(obj_x, obj_top, lens_x, obj_top, stroke="#2563eb", opacity=0.5, stroke_width=1.5),
            line(lens_x, obj_top, img_x, img_top, stroke="#2563eb", opacity=0.5, stroke_width=1.5),
            # Ray 2: through center (undeviated)
            line(obj_x, obj_top, img_x, img_top, stroke="#2563eb", opacity=0.5, stroke_width=1.5),
            # Ray 3: through object focal point -> parallel
            line(obj_x, obj_top, lens_x, cy, stroke="#2563eb", opacity=0.5, stroke_width=1.5),
            line(lens_x, cy, img_x, cy, stroke="#2563eb", opacity=0.5, stroke_width=1.5),
            # Labels
            text(
                width / 2,
                height - 20,
                f"u={u:.1f} mm  f={f:.1f} mm  v={v:.1f} mm  M={-v/u:.2f}",
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)
