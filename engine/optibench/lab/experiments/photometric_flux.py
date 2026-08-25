"""Photopic luminous flux integration experiment (V(lambda)-weighted)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, path, svg_root, text

_KM = 683.0
_H = 6.62607015e-34
_C = 2.99792458e8
_K_B = 1.380649e-23

_V_LAMBDA = [
    (380.0, 0.0001), (400.0, 0.0004), (420.0, 0.0040), (440.0, 0.0230),
    (460.0, 0.0600), (480.0, 0.1390), (500.0, 0.3230), (520.0, 0.7100),
    (540.0, 0.9540), (560.0, 0.9950), (580.0, 0.8700), (600.0, 0.6310),
    (620.0, 0.3810), (640.0, 0.1750), (660.0, 0.0610), (680.0, 0.0170),
    (700.0, 0.0041), (720.0, 0.0010),
]


def _planck_relative(lambda_nm: float, t_k: float) -> float:
    lam_m = lambda_nm * 1e-9
    exponent = (_H * _C) / (lam_m * _K_B * t_k)
    if exponent > 700:
        return 0.0
    return 1.0 / (lam_m**5 * (math.exp(exponent) - 1.0))


def _trapezoid(values: list[float], xs: list[float]) -> float:
    total = 0.0
    for i in range(1, len(xs)):
        total += (values[i - 1] + values[i]) / 2 * (xs[i] - xs[i - 1])
    return total


def _radiant_integral_full(t_k: float) -> float:
    """Total radiant exitance ∫B dλ over the thermally relevant range."""
    xs = [250.0 + i * 25.0 for i in range(600)]  # 250 – 15225 nm
    return _trapezoid([_planck_relative(x, t_k) for x in xs], xs)


class PhotometricFluxExperiment(OpticsExperiment):
    experiment_id = "photometric-flux"
    title = "光通量可见度积分实验"
    description = (
        "改变黑体温度，观察明视觉 V(λ) 加权后的光通量——辐射功率相同时"
        "人眼感知的流明数可以相差数倍。"
    )
    difficulty = "intermediate"
    prerequisites = ["blackbody"]
    linked_concepts = [
        "luminous-flux",
        "luminous-intensity",
        "illuminance",
    ]
    linked_formulas = [
        "visible-flux-integral",
    ]
    learning_objectives = [
        "掌握光通量定义 Φv = Km·∫SPD(λ)·V(λ)dλ，Km = 683 lm/W。",
        "区分辐射通量（物理瓦特）与光通量（视觉流明）。",
        "理解低温黑体大量红外辐射对人眼贡献为零，发光效率因此受限。",
    ]
    parameters = [
        Parameter(
            name="temperature_k",
            label="黑体温度",
            type="float",
            default=5500.0,
            min=1500.0,
            max=10000.0,
            step=100.0,
            unit="K",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        t_k = float(params.get("temperature_k", 5500.0))

        lambdas_nm = [item[0] for item in _V_LAMBDA]
        v_vals = [item[1] for item in _V_LAMBDA]
        spd = [_planck_relative(lam, t_k) for lam in lambdas_nm]
        weighted = [s * v for s, v in zip(spd, v_vals)]

        radiant_integral = _radiant_integral_full(t_k)
        luminous_integral = _trapezoid(weighted, lambdas_nm)
        luminous_flux = _KM * luminous_integral
        efficacy = luminous_flux / radiant_integral if radiant_integral > 0 else 0.0

        svg = self._draw_svg(lambdas_nm, spd, weighted, v_vals)

        return ExperimentResult(
            data={
                "temperature_k": t_k,
                "radiant_flux_relative": round(radiant_integral, 2),
                "luminous_weighted_integral": round(luminous_integral, 3),
                "luminous_flux_relative_lm": round(luminous_flux, 1),
                "luminous_efficacy_lm_per_w": round(efficacy, 1),
                "max_possible_efficacy_lm_per_w": _KM,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "V(λ) 峰值在 555 nm（Km=683 lm/W），人眼对绿光最敏感、红蓝两端急剧下降。",
                "2800 K 白炽灯大量能量落在红外，发光效率仅约 15 lm/W；日光约 90+ lm/W。",
                "理论上限即 683 lm/W（555 nm 单色光），任何宽带光源都无法达到。",
            ],
        )

    def _draw_svg(
        self,
        lambdas_nm: list[float],
        spd: list[float],
        weighted: list[float],
        v_vals: list[float],
    ) -> str:
        width, height = 640, 300
        ox, oy, span_x, span_y = 50.0, 30.0, 520.0, 180.0

        def px(nm: float, val: float) -> tuple[float, float]:
            return ox + (nm - 380.0) / 340.0 * span_x, oy + span_y - val * span_y

        def pts_of(vals: list[float]) -> str:
            return " ".join(f"{px(nm, v)[0]:.1f},{px(nm, v)[1]:.1f}"
                            for nm, v in zip(lambdas_nm, vals))

        children = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
            path("M" + pts_of(spd), fill="none", stroke="#f59e0b", stroke_width=2),
            (
                f'<path d="M{pts_of(v_vals)}" fill="none" stroke="#22c55e" '
                'stroke-dasharray="4"/>'
            ),
            path("M" + pts_of(weighted), fill="none", stroke="#3b82f6", stroke_width=2),
            text(ox + span_x - 4, oy + 12, "SPD", fill="#f59e0b", font_size=10, anchor="end"),
            text(ox + span_x - 4, oy + 26, "V(λ)", fill="#22c55e", font_size=10, anchor="end"),
            text(ox + span_x - 4, oy + 40, "SPD×V(λ)", fill="#3b82f6", font_size=10, anchor="end"),
            text(ox + span_x / 2, height - 34, "波长 (nm)", fill="#64748b", font_size=11, anchor="middle"),
        ]
        for nm in (400, 500, 600, 700):
            x, _ = px(float(nm), 0)
            children.append(line(x, oy + span_y, x, oy + span_y + 4, stroke="#94a3b8"))
            children.append(text(x, oy + span_y + 16, str(nm), fill="#94a3b8", font_size=9, anchor="middle"))
        children.append(
            text(width / 2, height - 12,
                 "蓝线面积 ∝ 人眼实际感知的光通量；橙线与蓝线之间的差距被 V(λ) 滤掉",
                 fill="#475569", font_size=11, anchor="middle")
        )
        return svg_root(width, height, children)
