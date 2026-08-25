"""Total internal reflection critical angle and fiber numerical aperture."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, line, svg_root, text


class TirCriticalAngleExperiment(OpticsExperiment):
    experiment_id = "tir-critical-angle"
    title = "全反射临界角与光纤 NA 实验"
    description = (
        "调整纤芯/包层（或玻璃/空气）折射率，观察全反射临界角、"
        "光纤数值孔径与受光半角的变化。"
    )
    difficulty = "foundation"
    prerequisites = ["snell-refraction"]
    linked_concepts = [
        "acceptance-angle",
        "multi-mode-fiber",
        "refractive-index",
    ]
    linked_formulas = [
        "tir-critical-angle",
        "fiber-na",
    ]
    learning_objectives = [
        "掌握全反射临界角 θc = arcsin(n₂/n₁)。",
        "掌握光纤数值孔径 NA = √(n₁² − n₂²)。",
        "理解受光半角 θa = arcsin(NA)：NA 越大，光纤收集光的能力越强。",
    ]
    parameters = [
        Parameter(
            name="n_core",
            label="纤芯折射率 n₁",
            type="float",
            default=1.46,
            min=1.3,
            max=1.8,
            step=0.01,
        ),
        Parameter(
            name="n_clad",
            label="包层折射率 n₂",
            type="float",
            default=1.44,
            min=1.0,
            max=1.45,
            step=0.01,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        n_core = float(params.get("n_core", 1.46))
        n_clad = float(params.get("n_clad", 1.44))

        ratio = n_clad / n_core
        theta_c_deg = math.degrees(math.asin(min(1.0, ratio)))
        na = math.sqrt(max(0.0, n_core**2 - n_clad**2))
        theta_acc_deg = math.degrees(math.asin(min(1.0, na)))

        svg = self._draw_svg(n_core, n_clad, theta_c_deg, na, theta_acc_deg)

        return ExperimentResult(
            data={
                "n_core": n_core,
                "n_cladding": n_clad,
                "critical_angle_deg": round(theta_c_deg, 2),
                "numerical_aperture": round(na, 4),
                "acceptance_half_angle_deg": round(theta_acc_deg, 2),
                "guiding": ratio < 1.0,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "只有入射角大于临界角的射线才发生全反射；小于临界角时部分能量折射流失。",
                "纤芯与包层折射率差越小，NA 越小，耦合越难，但带宽越高。",
                "从空气端面入射时，只要入射半角小于 θa，光线就满足纤芯-包层界的全反射条件。",
            ],
        )

    def _draw_svg(
        self,
        n_core: float,
        n_clad: float,
        theta_c_deg: float,
        na: float,
        theta_acc_deg: float,
    ) -> str:
        width, height = 640, 300
        children: list[str] = []

        # ── Left panel: interface TIR demo ──
        ix, iy = 200.0, 130.0
        panel_half = 120.0
        children.append(
            line(ix - panel_half, iy, ix + panel_half, iy, stroke="#475569", stroke_width=2)
        )
        children.append(text(ix - panel_half - 6, iy + 4, "n₂", fill="#475569", font_size=11, anchor="end"))
        children.append(text(ix - panel_half - 6, iy - 10, "n₁", fill="#475569", font_size=11, anchor="end"))
        # Normal.
        children.append(line(ix, iy - 70, ix, iy + 60, stroke="#94a3b8", dash="4"))
        children.append(text(ix + 4, iy - 74, "法线", fill="#94a3b8", font_size=9))

        ray_len = 95.0
        cases = [
            (theta_c_deg - 14.0, "#3b82f6", "θ<θc 折射"),
            (theta_c_deg, "#22c55e", "θ=θc 沿界面"),
            (theta_c_deg + 12.0, "#dc2626", "θ>θc 全反射"),
        ]
        for angle_deg, color, label in cases:
            rad_in = math.radians(angle_deg)
            # Incident from lower-right medium toward origin along normal-up direction.
            x1 = ix + ray_len * math.sin(rad_in)
            y1 = iy + ray_len * math.cos(rad_in)
            children.append(line(x1, y1, ix, iy, stroke=color, stroke_width=2))
            if angle_deg >= theta_c_deg:
                # Total reflection back into dense medium (mirror about normal).
                x2 = ix - ray_len * math.sin(rad_in)
                y2 = iy + ray_len * math.cos(rad_in)
                children.append(line(ix, iy, x2 * 0.9 + ix * 0.1, y2 * 0.9 + iy * 0.1, stroke=color, stroke_width=2))
            else:
                refr = math.degrees(math.asin(min(1.0, n_core * math.sin(rad_in) / n_clad)))
                rad_r = math.radians(refr)
                x2 = ix + 55.0 * math.sin(rad_r)
                y2 = iy - 55.0 * math.cos(rad_r)
                children.append(line(ix, iy, x2, y2, stroke=color, dash="4"))
            children.append(
                text(x1 + (6 if x1 >= ix else -6), y1 + 2, label, fill=color, font_size=9,
                     anchor="start" if x1 >= ix else "end")
            )

        children.append(
            text(
                ix,
                iy + 84,
                f"θc = arcsin(n₂/n₁) = {theta_c_deg:.1f}°",
                fill="#0f172a",
                font_size=12,
                anchor="middle",
            )
        )

        # ── Right panel: fiber acceptance cone ──
        cx, cy = 470.0, 150.0
        core_r = 26.0
        clad_r = 40.0
        children.append(circle(cx, cy, clad_r, fill="#e2e8f0", stroke="#94a3b8"))
        children.append(circle(cx, cy, core_r, fill="#fde68a", stroke="#d97706"))
        cone_len = 92.0
        if na > 0 and na <= 1:
            rad_a = math.radians(theta_acc_deg)
            for sgn in (-1.0, 1.0):
                dx = cone_len * math.sin(rad_a) * sgn
                dy = -cone_len * math.cos(rad_a)
                children.append(line(cx, cy, cx + dx, cy + dy, stroke="#d97706", stroke_width=2))
            children.append(
                text(cx, cy - cone_len - 10, f"受光半角 {theta_acc_deg:.1f}°", fill="#b45309",
                     font_size=11, anchor="middle")
            )
        children.append(
            text(cx, cy + clad_r + 20, f"NA = √(n₁²−n₂²) = {na:.3f}", fill="#0f172a",
                 font_size=12, anchor="middle")
        )
        if not (n_core > n_clad):
            children.append(
                text(cx, cy + clad_r + 38, "⚠ 需要 n₁ > n₂ 才能导光", fill="#dc2626",
                     font_size=11, anchor="middle")
            )

        return svg_root(width, height, children)
