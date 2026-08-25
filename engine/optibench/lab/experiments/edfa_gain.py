"""EDFA gain saturation experiment (teaching model)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, circle, line, path, svg_root, text


class EdfaGainExperiment(OpticsExperiment):
    experiment_id = "edfa-gain"
    title = "EDFA 增益饱和实验"
    description = (
        "调整最大增益与饱和输出功率，观察 EDFA 增益随输入功率的"
        "饱和曲线，以及输出功率如何趋于上限。"
    )
    difficulty = "advanced"
    prerequisites = []
    linked_concepts = [
        "edfa",
        "gain-medium",
    ]
    linked_formulas = [
        "edfa-gain-model",
    ]
    learning_objectives = [
        "掌握小信号增益 G₀ 与饱和输出功率 P_sat 的定义。",
        "掌握饱和模型 G(P_in) = G₀/(1 + P_in/P_sat)。",
        "理解「增益钳制」：深度饱和下输出功率趋近恒定，多出的泵浦转为 ASE。",
    ]
    parameters = [
        Parameter(
            name="small_signal_gain_db",
            label="小信号增益 G₀",
            type="float",
            default=30.0,
            min=10.0,
            max=40.0,
            step=1.0,
            unit="dB",
        ),
        Parameter(
            name="saturation_output_dbm",
            label="饱和输出功率",
            type="float",
            default=17.0,
            min=5.0,
            max=30.0,
            step=1.0,
            unit="dBm",
        ),
        Parameter(
            name="input_power_dbm",
            label="输入功率（工作点）",
            type="float",
            default=-15.0,
            min=-35.0,
            max=5.0,
            step=1.0,
            unit="dBm",
        ),
    ]

    @staticmethod
    def _dbm_to_mw(dbm: float) -> float:
        return 10 ** (dbm / 10)

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        g0_db = float(params.get("small_signal_gain_db", 30.0))
        p_sat_dbm = float(params.get("saturation_output_dbm", 17.0))
        pin_dbm = float(params.get("input_power_dbm", -15.0))

        g0_lin = 10 ** (g0_db / 10)
        p_sat_mw = self._dbm_to_mw(p_sat_dbm)

        def gain_at(pin_dbm_val: float) -> float:
            pin_lin = self._dbm_to_mw(pin_dbm_val)
            return g0_lin / (1 + pin_lin / p_sat_mw)

        sweep_dbm = [-35.0 + i * (5.0 - (-35.0)) / 60 for i in range(61)]
        gain_curve = []
        for dbm in sweep_dbm:
            g = gain_at(dbm)
            pout = g * self._dbm_to_mw(dbm)
            gain_curve.append((dbm, 10 * math.log10(g), 10 * math.log10(pout)))

        g_op = gain_at(pin_dbm)
        p_out_dbm = 10 * math.log10(g_op * self._dbm_to_mw(pin_dbm))

        svg = self._draw_svg(sweep_dbm, gain_curve, pin_dbm, g_op, p_out_dbm, g0_db)

        return ExperimentResult(
            data={
                "input_power_dbm": pin_dbm,
                "gain_db": round(g_op, 2),
                "output_power_dbm": round(p_out_dbm, 2),
                "output_power_mw": round(self._dbm_to_mw(p_out_dbm), 3),
                "small_signal_gain_db": g0_db,
                "in_deep_saturation": p_out_dbm > p_sat_dbm - 3,
                "model": "G = G0/(1+Pin/Psat)",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "小信号区增益恒为 G₀；输入增大后增益被反转粒子数耗尽压低——即增益饱和。",
                "P_sat 定义为「增益跌落一半（3 dB）时的输出功率」。",
                "深度饱和时输出功率近似恒定 ≈ P_sat：这就是功率放大器的工作方式。",
            ],
        )

    def _draw_svg(self, sweep_dbm, gain_curve, pin_dbm: float, g_op: float,
                  p_out_dbm: float, g0_db: float) -> str:
        width, height = 640, 300
        ox, oy, span_x, span_y = 56.0, 28.0, 330.0, 190.0
        y_min_db, y_max_db = 0.0, math.ceil(g0_db / 5) * 5

        def px(dbm: float, gain_db: float):
            xx = ox + (dbm - sweep_dbm[0]) / (sweep_dbm[-1] - sweep_dbm[0]) * span_x
            yy = oy + span_y - gain_db / y_max_db * span_y
            return xx, yy

        pts = " ".join(
            f"{px(d, g)[0]:.1f},{px(d, g)[1]:.1f}" for d, g, _pout in gain_curve
        )
        children: list[str] = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
            path("M" + pts, fill="none", stroke="#0ea5e9", stroke_width=2.5),
            line(ox, oy + span_y - g0_db / y_max_db * span_y,
                 ox + span_x, oy + span_y - g0_db / y_max_db * span_y,
                 stroke="#22c55e", dash="4"),
            text(ox + span_x - 4, oy + span_y - g0_db / y_max_db * span_y - 6,
                 f"G₀ = {g0_db:.0f} dB", fill="#22c55e", font_size=10, anchor="end"),
        ]
        opx, opy = px(pin_dbm, g_op)
        children.append(circle(opx, opy, 4, fill="#dc2626"))
        children.append(text(opx + 6, opy - 8, f"G={g_op:.1f} dB", fill="#dc2626", font_size=10))
        in_ticks = [(i / 4 * span_x, f"{-35 + i / 4 * 40:.0f}") for i in range(5)]
        children += axis_x(ox, oy + span_y, span_x, "输入功率 (dBm)", in_ticks)
        g_ticks = [(i / 4 * span_y, f"{y_max_db * (1 - i / 4):.0f}") for i in range(5)]
        children += axis_y(ox, oy + span_y, span_y, "增益 (dB)", g_ticks)
        children.append(
            text(width / 2, height - 14,
                 f"工作点：输入 {pin_dbm:.0f} dBm → 增益 {g_op:.1f} dB → 输出 {p_out_dbm:.1f} dBm",
                 fill="#334155", font_size=11, anchor="middle")
        )
        return svg_root(width, height, children)
