"""GVD pulse broadening experiment: Gaussian pulse width vs fiber length."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, circle, line, path, svg_root, text


class GvdPulseBroadeningExperiment(OpticsExperiment):
    experiment_id = "gvd-pulse-broadening"
    title = "群速度色散脉冲展宽实验"
    description = (
        "高斯脉冲在色散光纤中传播：观察脉宽展宽因子随距离/色散系数的"
        "增长，以及色散长度 L_D 的物理含义。"
    )
    difficulty = "advanced"
    prerequisites = []
    linked_concepts = [
        "chromatic-dispersion",
    ]
    linked_formulas = [
        "pulse-broadening-gvd",
    ]
    learning_objectives = [
        "掌握高斯脉冲展宽公式 T(L) = T₀·√(1+(L/L_D)²)。",
        "掌握色散长度 L_D = T₀²/|β₂|——脉宽越短越容易展宽。",
        "理解为什么 40G+ 长距传输必须做色散管理。",
    ]
    parameters = [
        Parameter(
            name="pulse_width_fs",
            label="初始脉宽 T₀",
            type="float",
            default=100.0,
            min=10.0,
            max=5000.0,
            step=10.0,
            unit="fs",
        ),
        Parameter(
            name="beta2_ps2_km",
            label="群速度色散 β₂",
            type="float",
            default=21.0,
            min=0.1,
            max=50.0,
            step=0.1,
            unit="ps²/km",
        ),
        Parameter(
            name="length_km",
            label="传输长度",
            type="float",
            default=10.0,
            min=0.1,
            max=100.0,
            step=0.1,
            unit="km",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        t0_ps = float(params.get("pulse_width_fs", 100.0)) / 1000.0
        beta2 = float(params.get("beta2_ps2_km", 21.0))
        length_km = float(params.get("length_km", 10.0))

        ld_km = t0_ps**2 / abs(beta2)
        broaden = math.sqrt(1.0 + (length_km / ld_km) ** 2)
        t_out_ps = t0_ps * broaden

        sweep = [length_km * i / 60 for i in range(61)]
        widths = [t0_ps * math.sqrt(1.0 + (dist_km / ld_km) ** 2)
                  for dist_km in sweep]

        svg = self._draw_svg(sweep, widths, t0_ps, ld_km, length_km, broaden, beta2)

        return ExperimentResult(
            data={
                "initial_width_ps": round(t0_ps, 3),
                "output_width_ps": round(t_out_ps, 3),
                "broadening_factor": round(broaden, 3),
                "dispersion_length_km": round(ld_km, 3),
                "transmission_length_km": length_km,
                "regime": "色散主导" if length_km > ld_km else "未展宽区（L < L_D）",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "L_D 是「脉冲自身走散」的特征长度：L ≪ L_D 几乎不展宽，L ≫ L_D 线性暴涨。",
                "T₀=100 ps、β₂=21 ps²/km 时 L_D≈476 km；T₀=1 ps 时骤降到 0.05 km。",
                "符号（正/负色散）不影响高斯脉宽，只影响啁啾方向。",
            ],
        )

    def _draw_svg(self, sweep: list[float], widths: list[float], t0_ps: float,
                  ld_km: float, length_now: float, broaden: float, beta2: float) -> str:
        width, height = 640, 300
        ox, oy, span_x, span_y = 56.0, 28.0, 330.0, 190.0
        y_max = max(widths[-1], t0_ps * 1.15)

        def px(dist_km: float, w: float):
            return ox + dist_km / sweep[-1] * span_x, oy + span_y - w / y_max * span_y

        pts = " ".join(f"{px(dist_km, w)[0]:.1f},{px(dist_km, w)[1]:.1f}"
                       for dist_km, w in zip(sweep, widths))
        children: list[str] = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
            path("M" + pts, fill="none", stroke="#8b5cf6", stroke_width=2.5),
        ]
        if ld_km <= sweep[-1]:
            lx = ox + ld_km / sweep[-1] * span_x
            children.append(line(lx, oy, lx, oy + span_y, stroke="#22c55e", dash="4"))
            children.append(text(lx + 4, oy + 14,
                                 f"L_D={ld_km:.1f} km", fill="#22c55e", font_size=10))
        else:
            children.append(text(ox + span_x / 2, oy + 14,
                                 f"L_D = {ld_km:.0f} km 超出图示范围", fill="#22c55e",
                                 font_size=10, anchor="middle"))
        opx, opy = px(length_now, t0_ps * broaden)
        children.append(circle(opx, opy, 4, fill="#dc2626"))
        children.append(text(opx + 6, opy - 6,
                             f"{t0_ps*broaden:.1f} ps", fill="#dc2626", font_size=10))

        l_ticks = [(i / 4 * span_x, f"{i / 4 * sweep[-1]:.1f}") for i in range(5)]
        children += axis_x(ox, oy + span_y, span_x, "传输长度 (km)", l_ticks)
        w_ticks = [(i / 2 * span_y, f"{y_max * (1 - i / 2):.1f}") for i in range(3)]
        children += axis_y(ox, oy + span_y, span_y, "输出脉宽 (ps)", w_ticks)
        children.append(text(width / 2, height - 14,
                             f"T₀={t0_ps:.0f} ps　β₂={beta2:.1f} ps²/km　展宽 ×{broaden:.2f}",
                             fill="#334155", font_size=11, anchor="middle"))
        return svg_root(width, height, children)

