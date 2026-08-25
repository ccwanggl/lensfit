"""Snell's law and total internal reflection experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import arrow, line, polygon, svg_root, text


class SnellRefractionExperiment(OpticsExperiment):
    experiment_id = "snell-refraction"
    title = "斯涅尔定律与全反射实验"
    description = "改变入射角和两种介质的折射率，观察折射、反射和全反射现象。"
    difficulty = "foundation"
    # Snell's law is more fundamental than the thin lens; requiring thin-lens
    # first inverts the physics order (fixed in learning-first phase 1).
    prerequisites = []
    linked_concepts = [
        "refractive-index",
        "dispersion",
    ]
    linked_formulas = [
        "20-formulas/snell-law",
    ]
    learning_objectives = [
        "掌握 n₁ sin θ₁ = n₂ sin θ₂ 的折射定律。",
        "认识光从光密介质到光疏介质时的全反射临界角。",
        "了解反射率随入射角的变化趋势。",
    ]
    parameters = [
        Parameter(
            name="incident_angle_deg",
            label="入射角",
            type="float",
            default=30.0,
            min=0.0,
            max=89.9,
            step=0.5,
            unit="°",
        ),
        Parameter(
            name="n1",
            label="介质 1 折射率",
            type="float",
            default=1.0,
            min=1.0,
            max=3.0,
            step=0.01,
        ),
        Parameter(
            name="n2",
            label="介质 2 折射率",
            type="float",
            default=1.5,
            min=1.0,
            max=3.0,
            step=0.01,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        theta1_deg = float(params.get("incident_angle_deg", 30.0))
        n1 = float(params.get("n1", 1.0))
        n2 = float(params.get("n2", 1.5))

        theta1 = math.radians(theta1_deg)
        sin_theta2 = (n1 / n2) * math.sin(theta1)

        warnings: list[str] = []
        tir = False
        theta2 = None
        reflectance = 0.0

        if n1 > n2:
            theta_c = math.asin(n2 / n1)
            if theta1 > theta_c:
                tir = True
                theta2 = None
                reflectance = 1.0
                warnings.append(
                    f"入射角 ({theta1_deg:.1f}°) 超过临界角 "
                    f"({math.degrees(theta_c):.1f}°)，发生全反射。"
                )
            else:
                theta2 = math.asin(sin_theta2)
                reflectance = self._fresnel_unpolarized(n1, n2, theta1, theta2)
        else:
            theta2 = math.asin(sin_theta2)
            reflectance = self._fresnel_unpolarized(n1, n2, theta1, theta2)

        critical_deg = math.degrees(math.asin(n2 / n1)) if n1 > n2 else None

        svg = self._draw_svg(theta1_deg, theta2, n1, n2, tir)

        return ExperimentResult(
            data={
                "incident_angle_deg": round(theta1_deg, 2),
                "n1": n1,
                "n2": n2,
                "refracted_angle_deg": (
                    round(math.degrees(theta2), 2) if theta2 is not None else None
                ),
                "critical_angle_deg": (
                    round(critical_deg, 2) if critical_deg is not None else None
                ),
                "total_internal_reflection": tir,
                "reflectance": round(reflectance, 4),
                "transmittance": round(1.0 - reflectance, 4),
            },
            svg=svg,
            warnings=warnings,
            learning_hints=[
                "光从光疏介质进入光密介质时，折射角小于入射角。",
                "光从光密介质进入光疏介质且入射角大于临界角时，全部能量被反射。",
                "正入射时反射率 R = ((n₁ - n₂)/(n₁ + n₂))²。",
            ],
        )

    @staticmethod
    def _fresnel_unpolarized(
        n1: float, n2: float, theta1: float, theta2: float
    ) -> float:
        """Return unpolarized Fresnel reflectance."""
        cos1 = math.cos(theta1)
        cos2 = math.cos(theta2)
        rs = ((n1 * cos1 - n2 * cos2) / (n1 * cos1 + n2 * cos2)) ** 2
        rp = ((n1 * cos2 - n2 * cos1) / (n1 * cos2 + n2 * cos1)) ** 2
        return 0.5 * (rs + rp)

    def _draw_svg(
        self,
        theta1_deg: float,
        theta2: float | None,
        n1: float,
        n2: float,
        tir: bool,
    ) -> str:
        width, height = 600, 320
        ix = width // 2
        iy = height // 2

        children = [
            # Medium 1 (top)
            polygon(
                [(0, 0), (width, 0), (width, iy), (0, iy)],
                fill="rgba(14,165,233,0.08)",
                stroke="none",
            ),
            # Medium 2 (bottom)
            polygon(
                [(0, iy), (width, iy), (width, height), (0, height)],
                fill="rgba(16,185,129,0.08)",
                stroke="none",
            ),
            # Interface
            line(0, iy, width, iy, stroke="#64748b", stroke_width=2),
            # Normal
            line(ix, 20, ix, height - 20, stroke="#94a3b8", dash="4"),
            text(ix + 5, 35, "法线", fill="#64748b", font_size=10),
            # Labels
            text(20, 30, f"介质 1  n₁={n1:.2f}", fill="#0ea5e9", font_size=12),
            text(20, height - 20, f"介质 2  n₂={n2:.2f}", fill="#10b981", font_size=12),
            # Incident ray
            *self._ray_from_angle(
                ix, iy, theta1_deg, 110, color="#2563eb", label="入射", top=True,
            ),
            # Reflected ray (always exists)
            *self._ray_from_angle(
                ix, iy, theta1_deg, 110, color="#f59e0b", label="反射",
                top=False, mirror=True,
            ),
        ]

        if tir:
            children.append(
                text(
                    width - 20,
                    iy - 40,
                    "全反射",
                    fill="#dc2626",
                    font_size=14,
                    anchor="end",
                )
            )
        else:
            theta2_deg = math.degrees(theta2) if theta2 else 0.0
            children.extend(
                self._ray_from_angle(
                    ix, iy, theta2_deg, 110, color="#2563eb", label="折射", top=False
                )
            )

        return svg_root(width, height, children)

    def _ray_from_angle(
        self,
        cx: float,
        cy: float,
        angle_deg: float,
        length: float,
        color: str,
        label: str,
        top: bool,
        mirror: bool = False,
    ) -> list[str]:
        """Draw a ray from the interface point at the given angle from normal.

        - top=True: ray is in upper half; angle measured from normal upward.
        - top=False: ray is in lower half; if mirror=True, reflected back upward.
        """
        theta = math.radians(angle_deg)
        # Direction vector
        if top:
            # From source above-left toward interface
            dx = math.sin(theta)
            dy = -math.cos(theta)
            start_x = cx - length * dx
            start_y = cy + length * dy
            end_x = cx
            end_y = cy
        elif mirror:
            # Reflected ray upward-right
            dx = math.sin(theta)
            dy = -math.cos(theta)
            start_x = cx
            start_y = cy
            end_x = cx + length * dx
            end_y = cy + length * dy
        else:
            # Refracted ray downward-right
            dx = math.sin(theta)
            dy = math.cos(theta)
            start_x = cx
            start_y = cy
            end_x = cx + length * dx
            end_y = cy + length * dy

        return [
            arrow(start_x, start_y, end_x, end_y, color=color, stroke_width=2),
            text(end_x + 8, end_y - 8, label, fill=color, font_size=11),
        ]
