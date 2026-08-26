"""Umbra and penumbra geometry experiment (extended light source)."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, rect, svg_root, text


class PenumbraExperiment(OpticsExperiment):
    experiment_id = "penumbra"
    title = "半影与本影实验"
    description = (
        "改变光源尺寸、障碍物尺寸与距离，观察本影如何收缩乃至消失、"
        "半影如何展宽——光的直线传播最直接的几何证据。"
    )
    difficulty = "foundation"
    prerequisites = []
    linked_concepts = [
        "半影",
    ]
    linked_formulas: list[str] = []
    learning_objectives = [
        "理解本影是完全无光区域，其边界由光源与障碍物的同侧边缘连线决定。",
        "理解半影是部分受光区域，宽度随光源尺寸和屏幕距离增大。",
        "掌握本影闭合条件：光源半径大于障碍物半径时，本影在有限距离处闭合。",
    ]
    parameters = [
        Parameter(
            name="source_diameter_mm",
            label="光源直径",
            type="float",
            default=40.0,
            min=5.0,
            max=100.0,
            step=5.0,
            unit="mm",
        ),
        Parameter(
            name="object_diameter_mm",
            label="障碍物直径",
            type="float",
            default=20.0,
            min=5.0,
            max=60.0,
            step=5.0,
            unit="mm",
        ),
        Parameter(
            name="source_object_distance_mm",
            label="光源—障碍物距离",
            type="float",
            default=200.0,
            min=50.0,
            max=500.0,
            step=10.0,
            unit="mm",
        ),
        Parameter(
            name="screen_distance_mm",
            label="障碍物—屏距离",
            type="float",
            default=150.0,
            min=10.0,
            max=600.0,
            step=10.0,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        source_r = float(params.get("source_diameter_mm", 40.0)) / 2
        object_r = float(params.get("object_diameter_mm", 20.0)) / 2
        d = float(params.get("source_object_distance_mm", 200.0))
        screen_l = float(params.get("screen_distance_mm", 150.0))

        delta_ratio = (source_r - object_r) / d

        umbra_radius = max(0.0, object_r - delta_ratio * screen_l)
        penumbra_radius = object_r + (source_r + object_r) * screen_l / d

        umbra_tip_mm: float | None = None
        if source_r > object_r:
            umbra_tip_mm = object_r / delta_ratio

        svg = self._draw_svg(
            source_r, object_r, d, screen_l, umbra_radius, penumbra_radius, umbra_tip_mm
        )

        return ExperimentResult(
            data={
                "source_radius_mm": source_r,
                "object_radius_mm": object_r,
                "umbra_radius_at_screen_mm": round(umbra_radius, 2),
                "penumbra_outer_radius_mm": round(penumbra_radius, 2),
                "penumbra_band_width_mm": round(penumbra_radius - umbra_radius, 2),
                "umbra_tip_distance_mm": round(umbra_tip_mm, 1)
                if umbra_tip_mm is not None
                else None,
                "umbra_exists_on_screen": umbra_radius > 0,
                "screen_beyond_umbra_tip": umbra_tip_mm is not None
                and screen_l > umbra_tip_mm,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "本影边界来自「光源上边缘 → 障碍物上边缘」的同侧切线，两条同侧切线相交处本影闭合。",
                "半影外边界来自「光源一侧边缘 → 障碍物另一侧边缘」的交叉切线。",
                "日食的本影/半影正是同一几何：月亮是障碍物，太阳是大尺度光源。",
            ],
        )

    def _draw_svg(
        self,
        source_r: float,
        object_r: float,
        d: float,
        screen_l: float,
        umbra_r: float,
        penumbra_r: float,
        umbra_tip_mm: float | None,
    ) -> str:
        width, height = 640, 300
        axis_y_px = height / 2 - 14
        x_source = 56.0
        span = d + screen_l
        h_scale = (width - x_source - 96) / span if span > 0 else 1.0
        max_extent = max(penumbra_r, source_r, object_r, 1.0)
        v_scale = min(h_scale, (height / 2 - 44) / max_extent)

        x_obj = x_source + d * h_scale
        x_screen = x_source + span * h_scale

        def y_px(y_mm: float) -> float:
            return axis_y_px + y_mm * v_scale

        children: list[str] = [
            line(x_source - 16, axis_y_px, x_screen + 24, axis_y_px, stroke="#cbd5e1", dash="3"),
        ]

        boundary_rays = [
            (-source_r, -object_r, "#f97316"),
            (source_r, object_r, "#f97316"),
            (-source_r, object_r, "#94a3b8"),
            (source_r, -object_r, "#94a3b8"),
        ]
        for y_s, y_o, color in boundary_rays:
            slope = (y_o - y_s) / d
            children.append(
                line(
                    x_source,
                    y_px(y_s),
                    x_screen,
                    y_px(y_o + slope * screen_l),
                    stroke=color,
                    stroke_width=1,
                    opacity=0.85,
                )
            )

        children.append(
            rect(x_source - 7, y_px(-source_r), 7,
                 2 * source_r * v_scale, fill="#fbbf24")
        )
        children.append(text(x_source + 2, y_px(-source_r) - 6,
                             "光源", fill="#b45309", font_size=11))

        obj_w = 10.0
        children.append(
            rect(x_obj - obj_w / 2, y_px(-object_r), obj_w,
                 2 * object_r * v_scale, fill="#334155")
        )
        children.append(
            text(x_obj, y_px(object_r) + 15, "障碍物", fill="#334155",
                 font_size=11, anchor="middle")
        )

        band_half = max(penumbra_r * v_scale, 20.0)
        children.append(
            rect(x_screen, axis_y_px - band_half, 10, 2 * band_half,
                 fill="#f8fafc", stroke="#94a3b8")
        )
        if umbra_r > 0:
            umbra_h = 2 * umbra_r * v_scale
            children.append(rect(x_screen, axis_y_px - umbra_h / 2, 10, umbra_h, fill="#334155"))
            children.append(text(x_screen + 15, axis_y_px - 4,
                                 "本影", fill="#334155", font_size=11))
        pen_mid_mm = -(umbra_r + penumbra_r) / 2 if umbra_r > 0 else -(band_half / v_scale) / 2
        children.append(
            text(x_screen + 15, y_px(pen_mid_mm) + 4, "半影", fill="#64748b", font_size=11)
        )

        tip_text = (
            f"本影尖端：距障碍物 {umbra_tip_mm:.0f} mm"
            if umbra_tip_mm is not None
            else "光源 ≥ 障碍物：屏幕方向无有限本影"
        )
        children.append(
            text(
                width / 2,
                height - 14,
                f"屏幕处：本影半径 {umbra_r:.1f} mm｜半影外径 {penumbra_r:.1f} mm　{tip_text}",
                fill="#475569",
                font_size=11,
                anchor="middle",
            )
        )
        return svg_root(width, height, children)
