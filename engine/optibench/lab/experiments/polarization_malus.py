"""Polarization and Malus's law experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import arrow, circle, line, polygon, svg_root, text


class PolarizationMalusExperiment(OpticsExperiment):
    experiment_id = "polarization-malus"
    title = "偏振与马吕斯定律实验"
    description = "改变两个理想偏振片的透光轴夹角，观察透射光强如何按马吕斯定律变化。"
    difficulty = "foundation"
    # Malus's law only needs the concept of polarized light; a thin-lens
    # prerequisite is physically unmotivated (fixed in learning-first phase 1).
    prerequisites = []
    linked_concepts = [
        "polarization",
    ]
    linked_formulas = [
        "malus-law",
    ]
    learning_objectives = [
        "理解非偏振光通过第一个偏振片后光强减半。",
        "掌握马吕斯定律 I = I₀ cos²θ。",
        "观察当两个偏振片正交时透射光强为零。",
    ]
    parameters = [
        Parameter(
            name="incident_intensity",
            label="入射光强",
            type="float",
            default=1.0,
            min=0.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="polarizer1_angle_deg",
            label="偏振片 1 透光轴",
            type="float",
            default=0.0,
            min=0.0,
            max=180.0,
            step=1.0,
            unit="°",
        ),
        Parameter(
            name="polarizer2_angle_deg",
            label="偏振片 2 透光轴",
            type="float",
            default=45.0,
            min=0.0,
            max=180.0,
            step=1.0,
            unit="°",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        i0 = float(params.get("incident_intensity", 1.0))
        theta1 = float(params.get("polarizer1_angle_deg", 0.0))
        theta2 = float(params.get("polarizer2_angle_deg", 45.0))

        # Unpolarized light after first ideal polarizer is halved
        i1 = i0 * 0.5
        delta = math.radians(theta2 - theta1)
        i2 = i1 * math.cos(delta) ** 2

        svg = self._draw_svg(theta1, theta2, i0, i1, i2)

        return ExperimentResult(
            data={
                "incident_intensity": i0,
                "polarizer1_angle_deg": theta1,
                "polarizer2_angle_deg": theta2,
                "after_polarizer1": round(i1, 4),
                "after_polarizer2": round(i2, 4),
                "transmission_fraction": round(i2 / i0, 4) if i0 > 0 else 0.0,
                "relative_angle_deg": round(abs(theta2 - theta1) % 180, 2),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "理想偏振片只让与其透光轴平行的电场分量通过。",
                "两个偏振片透光轴平行时透射光强最大（忽略吸收）。",
                "两个偏振片透光轴垂直时发生消光，透射光强为零。",
            ],
        )

    def _draw_svg(
        self,
        theta1: float,
        theta2: float,
        i0: float,
        i1: float,
        i2: float,
    ) -> str:
        width, height = 640, 260
        y = height // 2
        p1_x = 160
        p2_x = 480

        children = [
            # Optical axis
            line(40, y, width - 40, y, stroke="#94a3b8", dash="4"),
            # Polarizer 1
            *self._polarizer(p1_x, y, 80, theta1, "P1"),
            # Polarizer 2
            *self._polarizer(p2_x, y, 80, theta2, "P2"),
            # Light rays with thickness proportional to intensity
            arrow(40, y, p1_x - 30, y, color="#f59e0b", stroke_width=2 + i0 * 6),
            arrow(p1_x + 30, y, p2_x - 30, y, color="#f59e0b", stroke_width=2 + i1 * 6),
            arrow(p2_x + 30, y, width - 40, y, color="#f59e0b", stroke_width=2 + i2 * 6),
            # Intensity labels
            text(p1_x - 70, y - 20, f"I₀={i0:.2f}", fill="#b45309", font_size=11, anchor="middle"),
            text(
                (p1_x + p2_x) // 2,
                y - 20,
                f"I₁={i1:.2f}",
                fill="#b45309",
                font_size=11,
                anchor="middle",
            ),
            text(p2_x + 70, y - 20, f"I₂={i2:.2f}", fill="#b45309", font_size=11, anchor="middle"),
            # Formula
            text(
                width / 2,
                height - 30,
                f"θ = {abs(theta2 - theta1) % 180:.0f}°  |  I₂ = I₀/2 · cos²θ = {i2:.3f}",
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)

    def _polarizer(
        self, cx: float, cy: float, size: float, angle_deg: float, label: str
    ) -> list[str]:
        """Draw a polarizer disk with its transmission axis."""
        half = size / 2
        elements = [
            polygon(
                [
                    (cx - half, cy - half),
                    (cx + half, cy - half),
                    (cx + half, cy + half),
                    (cx - half, cy + half),
                ],
                fill="rgba(99,102,241,0.15)",
                stroke="#4f46e5",
            ),
            circle(cx, cy, half - 4, fill="none", stroke="#4f46e5", stroke_width=2),
            text(cx, cy + half + 18, label, fill="#4f46e5", font_size=12, anchor="middle"),
        ]

        # Transmission axis line
        rad = math.radians(angle_deg)
        x1 = cx - (half - 10) * math.cos(rad)
        y1 = cy - (half - 10) * math.sin(rad)
        x2 = cx + (half - 10) * math.cos(rad)
        y2 = cy + (half - 10) * math.sin(rad)
        elements.append(
            line(x1, y1, x2, y2, stroke="#dc2626", stroke_width=3)
        )
        elements.append(
            text(
                cx,
                cy - half - 10,
                f"{angle_deg:.0f}°",
                fill="#dc2626",
                font_size=10,
                anchor="middle",
            )
        )
        return elements
