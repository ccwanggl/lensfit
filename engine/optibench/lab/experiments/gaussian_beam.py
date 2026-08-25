"""Gaussian beam propagation experiment (waist, Rayleigh range, divergence)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, line, path, svg_root, text


class GaussianBeamExperiment(OpticsExperiment):
    experiment_id = "gaussian-beam"
    title = "高斯光束传播实验"
    description = (
        "改变波长与束腰半径，观察高斯光束半径沿传播方向的演化、"
        "瑞利范围与远场发散角。"
    )
    difficulty = "intermediate"
    prerequisites = []
    linked_concepts = [
        "gaussian-beam",
        "rayleigh-range",
        "beam-quality-m2",
    ]
    linked_formulas = [
        "gaussian-beam-waist",
    ]
    learning_objectives = [
        "掌握高斯光束束腰半径 w(z) = w₀·√(1+(z/z_R)²)。",
        "理解瑞利范围 z_R = πw₀²/λ 与束腰面积成正比。",
        "理解远场半发散角 θ = λ/(πw₀)：束腰越小，发散越快。",
    ]
    parameters = [
        Parameter(
            name="wavelength_nm",
            label="波长",
            type="float",
            default=632.8,
            min=200.0,
            max=2000.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="waist_radius_um",
            label="束腰半径 w₀ (1/e²)",
            type="float",
            default=50.0,
            min=5.0,
            max=500.0,
            step=5.0,
            unit="µm",
        ),
        Parameter(
            name="propagation_mm",
            label="传播距离",
            type="float",
            default=200.0,
            min=10.0,
            max=1000.0,
            step=10.0,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        lam_m = float(params.get("wavelength_nm", 632.8)) * 1e-9
        w0_m = float(params.get("waist_radius_um", 50.0)) * 1e-6
        l_m = float(params.get("propagation_mm", 200.0)) * 1e-3

        z_r = math.pi * w0_m**2 / lam_m
        theta_half = lam_m / (math.pi * w0_m)

        num_samples = 128
        zs_m = [l_m * i / (num_samples - 1) for i in range(num_samples)]
        ws_m = [w0_m * math.sqrt(1.0 + (z / z_r) ** 2) for z in zs_m]

        svg = self._draw_svg(zs_m, ws_m, w0_m, lam_m, theta_half, z_r)

        return ExperimentResult(
            data={
                "wavelength_nm": round(lam_m * 1e9, 1),
                "waist_radius_um": round(w0_m * 1e6, 1),
                "rayleigh_range_mm": round(z_r * 1e3, 3),
                "divergence_half_angle_mrad": round(theta_half * 1e3, 3),
                "beam_radius_at_end_mm": round(ws_m[-1] * 1e3, 4),
                "waist_growth_ratio": round(ws_m[-1] / w0_m, 3),
                "zr_within_range": z_r <= l_m,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "瑞利范围内（|z| < z_R）光束近似准直；超出后按线性发散。",
                "z = z_R 处光束半径增大到 √2·w₀，波前曲率半径最小。",
                "聚焦光斑越小（w₀ 小），发散越快——衍射反比关系的直接体现。",
            ],
        )

    def _draw_svg(
        self,
        zs_m: list[float],
        ws_m: list[float],
        w0_m: float,
        lam_m: float,
        theta_half: float,
        z_r: float,
    ) -> str:
        width, height = 640, 300
        margin_left, margin_top, margin_bottom = 56, 36, 52
        plot_w = width - margin_left - 24
        plot_h = height - margin_top - margin_bottom
        z_max = zs_m[-1] if zs_m[-1] > 0 else 1.0
        w_display_max = max(max(ws_m), w0_m, z_r / 8) * 1.15

        def x_px(z_m: float) -> float:
            return margin_left + z_m / z_max * plot_w

        def y_px(w_m: float) -> float:
            frac = min(1.0, abs(w_m) / w_display_max)
            return margin_top + plot_h - frac * plot_h

        upper_pts = " ".join(f"{x_px(z):.1f},{y_px(w):.1f}" for z, w in zip(zs_m, ws_m))
        lower_pts = " ".join(
            f"{x_px(z):.1f},{y_px(-w):.1f}" for z, w in zip(reversed(zs_m), reversed(ws_m))
        )

        children: list[str] = [
            path(f"M{upper_pts} L{lower_pts} Z", fill="rgba(245,158,11,0.25)"),
            path("M" + upper_pts, fill="none", stroke="#f59e0b", stroke_width=2),
            path("M" + lower_pts, fill="none", stroke="#f59e0b", stroke_width=2),
            line(
                margin_left,
                height - margin_bottom,
                width - 24,
                height - margin_bottom,
                stroke="#94a3b8",
                dash="4",
            ),
        ]

        if z_r <= z_max:
            xr = x_px(z_r)
            children.append(
                line(xr, margin_top, xr, height - margin_bottom, stroke="#22c55e", dash="4")
            )
            children.append(
                text(
                    xr + 4,
                    margin_top + 14,
                    f"z_R = {z_r * 1e3:.0f} mm",
                    fill="#22c55e",
                    font_size=10,
                )
            )
        else:
            children.append(
                text(
                    margin_left + plot_w / 2,
                    margin_top + 14,
                    f"z_R = {z_r * 1e3:.0f} mm 超出显示范围",
                    fill="#22c55e",
                    font_size=10,
                    anchor="middle",
                )
            )

        z_ticks = [(i / 4 * plot_w, f"{i / 4 * z_max * 1e3:.0f}") for i in range(5)]
        children += axis_x(
            margin_left, height - margin_bottom, plot_w, "传播距离 z (mm)", z_ticks
        )
        half_tick_mm = w_display_max / 2 * 1e3
        children += axis_y(
            margin_left,
            height - margin_bottom,
            plot_h,
            "光束半径 ±w(z) (mm)",
            [(plot_h / 2, f"{half_tick_mm:.1f}"), (plot_h, f"{w_display_max * 1e3:.1f}")],
        )
        children.append(
            text(
                width / 2,
                height - 12,
                f"w₀={w0_m * 1e6:.0f} µm   λ={lam_m * 1e9:.0f} nm   "
                f"θ½={theta_half * 1e3:.2f} mrad   w(L)={ws_m[-1] * 1e3:.2f} mm",
                fill="#475569",
                font_size=11,
                anchor="middle",
            )
        )

        return svg_root(width, height, children)
