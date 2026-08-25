"""Two-point resolution experiment (Rayleigh criterion cross-section)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, line, path, svg_root, text


_AIRY_FIRST_ZERO = 3.83170597  # first zero of J1, in pattern-units


def _airy_amplitude(x: float) -> float:
    """Amplitude of Airy pattern: 2·J1(x)/x (x in units of 1.22λf/D half)."""
    if abs(x) < 1e-9:
        return 1.0
    ax = abs(x)
    half = ax / 2
    term = half
    j1 = term
    for k in range(1, 40):
        term *= -(half**2) / (k * (k + 1))
        j1 += term
        if abs(term) < 1e-14:
            break
    return 2 * j1 / x


class RayleighTwoPointExperiment(OpticsExperiment):
    experiment_id = "rayleigh-two-point"
    title = "双点分辨与瑞利判据实验"
    description = (
        "调节两个点源的间距（以艾里半径为单位），观察合成强度剖面的"
        "中心凹陷如何变化，直观理解瑞利判据 26% 凹陷标准。"
    )
    difficulty = "intermediate"
    prerequisites = ["diffraction"]
    linked_concepts = [
        "瑞利判据",
        "airy-disk",
        "cutoff-frequency",
    ]
    linked_formulas = [
        "瑞利分辨率",
    ]
    learning_objectives = [
        "掌握瑞利判据：两像点间距等于艾里斑第一暗环半径时刚好可分辨。",
        "理解分辨极限由孔径衍射决定：r₀ = 1.22·λ·N（N 为 F 数）。",
        "观察间距小于 r₀ 时中心凹陷消失，两点融为一个亮斑。",
    ]
    parameters = [
        Parameter(
            name="separation_ratio",
            label="间距 / 艾里半径 r₀",
            type="float",
            default=1.0,
            min=0.3,
            max=3.0,
            step=0.05,
        ),
        Parameter(
            name="wavelength_nm",
            label="波长",
            type="float",
            default=550.0,
            min=400.0,
            max=700.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="f_number",
            label="F 数 N",
            type="float",
            default=8.0,
            min=1.0,
            max=22.0,
            step=0.5,
        ),
    ]

    @staticmethod
    def _intensity(x: float, separation: float) -> float:
        """Sum of two Airy intensities centered at ±separation/2."""
        i_left = _airy_amplitude(x + separation / 2) ** 2
        i_right = _airy_amplitude(x - separation / 2) ** 2
        return i_left + i_right

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        ratio = float(params.get("separation_ratio", 1.0))
        lam_m = float(params.get("wavelength_nm", 550.0)) * 1e-9
        f_number = float(params.get("f_number", 8.0))

        airy_radius_um = 1.22 * lam_m * f_number * 1e6
        separation = ratio * _AIRY_FIRST_ZERO
        separation_um = ratio * airy_radius_um

        num = 241
        x_half = max(3.0, separation * 1.15)
        xs = [-x_half + i * (2 * x_half) / (num - 1) for i in range(num)]
        profile = [self._intensity(x, separation) for x in xs]

        center_val = self._intensity(0.0, separation)
        peak_val = max(profile)
        dip_pct = (1.0 - center_val / peak_val) * 100.0 if peak_val > 0 else 0.0

        svg = self._draw_svg(xs, profile, separation, dip_pct)

        return ExperimentResult(
            data={
                "airy_radius_um": round(airy_radius_um, 3),
                "separation_um": round(separation_um, 3),
                "separation_ratio": ratio,
                "center_dip_pct": round(dip_pct, 1),
                "resolved_by_rayleigh": ratio >= 1.0,
                "resolved_by_sparrow": center_val < peak_val,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "瑞利判据：等亮度双点的中心凹陷达到峰值的约 74%（即凹陷 26%）即可分辨。",
                "Sparrow 极限更宽松：只要中心出现极小值就算分辨，实际人眼/传感器判据介于两者之间。",
                "缩小 F 数或缩短波长都能减小 r₀，从而提高分辨率——与衍射极限一致。",
            ],
        )

    def _draw_svg(self, xs: list[float], profile: list[float], separation: float,
                  dip_pct: float) -> str:
        width, height = 640, 300
        ox, oy, span_x, span_y = 50.0, 30.0, 520.0, 190.0
        peak = max(profile) if profile else 1.0
        x_min, x_max = xs[0], xs[-1]

        def px(x: float, val: float) -> tuple[float, float]:
            xx = ox + (x - x_min) / (x_max - x_min) * span_x
            yy = oy + span_y - val / peak * span_y
            return xx, yy

        combined_pts = " ".join(f"{px(x, v)[0]:.1f},{px(x, v)[1]:.1f}"
                                for x, v in zip(xs, profile))

        children: list[str] = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
        ]

        half = separation / 2
        ind_l = []
        ind_r = []
        for x in [x_min + i * (x_max - x_min) / 120 for i in range(121)]:
            il = _airy_amplitude(x + half) ** 2
            ir = _airy_amplitude(x - half) ** 2
            a, b = px(x, il)
            c, d = px(x, ir)
            ind_l.append(f"{a:.1f},{b:.1f}")
            ind_r.append(f"{c:.1f},{d:.1f}")
        children.append(path("M" + " L".join(ind_l), fill="none", stroke="#94a3b8", stroke_width=1))
        children.append(path("M" + " L".join(ind_r), fill="none", stroke="#94a3b8", stroke_width=1))
        children.append(path("M" + combined_pts, fill="none", stroke="#f59e0b", stroke_width=2.5))

        cx_px = px(0.0, 0.0)[0]
        children.append(line(cx_px, oy + 10, cx_px, oy + span_y, stroke="#94a3b8", dash="3"))
        for sgn, label in ((-half, "-s/2"), (half, "+s/2")):
            mx, _ = px(sgn, 0)
            children.append(line(mx, oy + span_y - 6, mx, oy + span_y, stroke="#dc2626"))

        children += axis_x(ox, oy + span_y, span_x, "像面位置 (单位: 艾里半径)", [])
        children.append(text(width / 2, height - 14,
                             f"间距 {separation:.2f} r₀　中心凹陷 {dip_pct:.0f}%"
                             f"（瑞利判据 ≈26%）",
                             fill="#475569", font_size=11, anchor="middle"))
        return svg_root(width, height, children)
