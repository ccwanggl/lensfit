"""Solid angle of a cone: exact formula vs small-angle approximation."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, svg_root, text


class SolidAngleConeExperiment(OpticsExperiment):
    experiment_id = "solid-angle-cone"
    title = "立体角与锥形孔径实验"
    description = (
        "调整锥形孔径半角，对比立体角的精确式 Ω = 2π(1−cosα) "
        "与小角度近似 Ω ≈ πα²，理解近似何时失效。"
    )
    difficulty = "foundation"
    prerequisites = ["concept-solid-angle"]
    linked_concepts = [
        "solid-angle",
    ]
    linked_formulas = [
        "solid-angle-cone",
    ]
    learning_objectives = [
        "掌握锥形立体角精确公式 Ω = 2π(1 − cosα)。",
        "理解小角度近似 Ω ≈ πα² 及其相对误差随 α 的增长。",
        "建立立体角直觉：半球 = 2π sr，全空间 = 4π sr。",
    ]
    parameters = [
        Parameter(
            name="half_angle_deg",
            label="锥半角 α",
            type="float",
            default=30.0,
            min=0.5,
            max=89.0,
            step=0.5,
            unit="°",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        alpha_deg = float(params.get("half_angle_deg", 30.0))
        alpha_rad = math.radians(alpha_deg)

        omega_exact = 2.0 * math.pi * (1.0 - math.cos(alpha_rad))
        omega_approx = math.pi * alpha_rad**2
        approx_error_pct = (
            (omega_approx - omega_exact) / omega_exact * 100.0 if omega_exact > 0 else 0.0
        )

        svg = self._draw_svg(alpha_deg, omega_exact, omega_approx, approx_error_pct)

        return ExperimentResult(
            data={
                "half_angle_deg": alpha_deg,
                "omega_exact_sr": round(omega_exact, 5),
                "omega_approx_sr": round(omega_approx, 5),
                "approx_error_pct": round(approx_error_pct, 3),
                "sphere_fraction_pct": round(omega_exact / (4 * math.pi) * 100.0, 3),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "全空间立体角为 4π sr，半球为 2π sr——精确式在 α=90° 时恰好给出 2π。",
                "小角度近似 Ω≈πα² 在 α<20° 时误差 <1%，照明/光纤计算常直接使用。",
                "聚光比、耦合效率等非成像量都建立在立体角守恒（étendue）之上。",
            ],
        )

    def _draw_svg(
        self,
        alpha_deg: float,
        omega_exact: float,
        omega_approx: float,
        error_pct: float,
    ) -> str:
        width, height = 640, 300
        cx, apex_y = 190.0, 60.0
        base_y = 240.0
        depth = base_y - apex_y
        half_w = min(150.0, depth * math.tan(math.radians(alpha_deg)))

        children: list[str] = [
            # Cone silhouette.
            line(cx, apex_y, cx - half_w, base_y, stroke="#d97706", stroke_width=2),
            line(cx, apex_y, cx + half_w, base_y, stroke="#d97706", stroke_width=2),
            # Base ellipse (projected circle).
            f'<ellipse cx="{cx:.1f}" cy="{base_y:.1f}" rx="{half_w:.1f}" ry="{half_w*0.22:.1f}" '
            'fill="rgba(245,158,11,0.18)" stroke="#d97706"/>',
            # Axis.
            line(cx, apex_y, cx, base_y + 18, stroke="#94a3b8", dash="4"),
            text(cx + 6, apex_y + 24, "α", fill="#b45309", font_size=12),
        ]

        rows = [
            ("精确式 2π(1−cosα)", f"{omega_exact:.4f} sr"),
            ("小角度近似 πα²", f"{omega_approx:.4f} sr"),
            ("近似相对误差", f"{error_pct:+.2f}%"),
            ("占全球面比例", f"{omega_exact / (4*math.pi)*100:.2f}%"),
        ]
        y = 70.0
        for name, value in rows:
            children.append(text(370, y, name, fill="#475569", font_size=11))
            children.append(text(600, y, value, fill="#0f172a", font_size=12, anchor="end"))
            y += 34

        verdict = (
            "近似可靠" if abs(error_pct) < 1.0 else
            "近似开始偏离" if abs(error_pct) < 10.0 else
            "必须使用精确式"
        )
        color = ("#22c55e" if abs(error_pct) < 1.0
                 else "#f59e0b" if abs(error_pct) < 10.0 else "#dc2626")
        children.append(text(485, y + 8, verdict, fill=color, font_size=13, anchor="middle"))

        return svg_root(width, height, children)
