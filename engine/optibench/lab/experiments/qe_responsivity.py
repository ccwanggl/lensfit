"""Quantum efficiency ↔ responsivity relation experiment."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, circle, line, path, svg_root, text

_Q = 1.602176634e-19  # elementary charge, C
_H = 6.62607015e-34
_C = 2.99792458e8


class QeResponsivityExperiment(OpticsExperiment):
    experiment_id = "qe-responsivity"
    title = "量子效率与响应度关系实验"
    description = (
        "调整量子效率 η，观察光电探测器的响应度 R = η·q·λ/(h·c) "
        "如何随波长线性增长——以及它为什么存在物理上限。"
    )
    difficulty = "foundation"
    prerequisites = ["concept-quantum-efficiency"]
    linked_concepts = [
        "quantum-efficiency",
        "responsivity",
        "photodiode",
    ]
    linked_formulas = [
        "qe-responsivity-relation",
        "responsivity",
    ]
    learning_objectives = [
        "掌握响应度定义 R = 光电流 / 光功率，单位 A/W。",
        "推导 R = η·q·λ/(h·c)：理想光子探测器响应度随波长线性上升。",
        "理解 η=100% 的外延线是所有真实探测器曲线的天花板。",
    ]
    parameters = [
        Parameter(
            name="quantum_efficiency",
            label="量子效率 η",
            type="float",
            default=0.7,
            min=0.05,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="wavelength_nm",
            label="工作波长",
            type="float",
            default=900.0,
            min=300.0,
            max=1600.0,
            step=10.0,
            unit="nm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        qe = float(params.get("quantum_efficiency", 0.7))
        lam_m = float(params.get("wavelength_nm", 900.0)) * 1e-9

        responsivity = qe * _Q * lam_m / (_H * _C)
        ideal_at_lambda = _Q * lam_m / (_H * _C)

        num_samples = 64
        sweep_nm = [300.0 + i * (1600.0 - 300.0) / (num_samples - 1) for i in range(num_samples)]
        curve_ideal = [_Q * (lam * 1e-9) / (_H * _C) for lam in sweep_nm]
        curve_eta = [r * qe for r in curve_ideal]

        svg = self._draw_svg(sweep_nm, curve_ideal, curve_eta, lam_m, qe, responsivity)

        return ExperimentResult(
            data={
                "quantum_efficiency": qe,
                "wavelength_nm": lam_m * 1e9,
                "responsivity_a_per_w": round(responsivity, 4),
                "ideal_responsivity_a_per_w": round(ideal_at_lambda, 4),
                "photocurrent_uw_w": round(responsivity * 1e6, 2),
                "slope_a_per_w_per_nm": round(qe * _Q * 1e-9 / (_H * _C), 6),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "每个光子最多释放一个电子：η=1 时 R = λ/1.24 (A/W @ µm)，斜率固定。",
                "波长越长同样功率对应的光子数越多，响应度越高——但超过带隙截止波长后骤降为零。",
                "硅探测器约在 1.1 µm 截止；本图只画到 1.6 µm 以覆盖 InGaAs 对比。",
            ],
        )

    def _draw_svg(
        self,
        sweep_nm: list[float],
        curve_ideal: list[float],
        curve_eta: list[float],
        lam_m: float,
        qe: float,
        responsivity: float,
    ) -> str:
        width, height = 640, 300
        margin_left, margin_top, margin_bottom = 58, 32, 50
        plot_w = width - margin_left - 24
        plot_h = height - margin_top - margin_bottom
        y_max = curve_ideal[-1] * 1.08

        def x_px(nm: float) -> float:
            return margin_left + (nm - 300.0) / 1300.0 * plot_w

        def y_px(r: float) -> float:
            return margin_top + plot_h - min(1.0, r / y_max) * plot_h

        ideal_pts = " ".join(
            f"{x_px(nm):.1f},{y_px(r):.1f}" for nm, r in zip(sweep_nm, curve_ideal)
        )
        eta_pts = " ".join(
            f"{x_px(nm):.1f},{y_px(r):.1f}" for nm, r in zip(sweep_nm, curve_eta)
        )

        marker_x = x_px(lam_m * 1e9)
        marker_y = y_px(responsivity)

        children: list[str] = [
            (
                f'<path d="M{ideal_pts}" fill="none" stroke="#22c55e" '
                'stroke-width="1.5" stroke-dasharray="4"/>'
            ),
            path("M" + eta_pts, fill="none", stroke="#3b82f6", stroke_width=2),
            line(marker_x, margin_top, marker_x, margin_top + plot_h, stroke="#94a3b8", dash="3"),
            circle(marker_x, marker_y, 4, fill="#dc2626"),
            text(marker_x + 6, marker_y - 6, f"R={responsivity:.3f} A/W",
                 fill="#dc2626", font_size=11),
            text(margin_left + plot_w - 6, margin_top + 16, "η=100% 理想线", fill="#22c55e",
                 font_size=10, anchor="end"),
            text(margin_left + plot_w - 6, margin_top + 30, f"η={qe*100:.0f}%", fill="#3b82f6",
                 font_size=10, anchor="end"),
        ]
        nm_ticks = [(i / 4 * plot_w, f"{300 + i / 4 * 1300:.0f}") for i in range(5)]
        children += axis_x(margin_left, height - margin_bottom, plot_w, "波长 (nm)", nm_ticks)
        r_ticks = [(i / 2 * plot_h, f"{y_max * (1 - i / 2):.2f}") for i in range(3)]
        children += axis_y(margin_left, height - margin_bottom, plot_h, "响应度 R (A/W)", r_ticks)

        return svg_root(width, height, children)
