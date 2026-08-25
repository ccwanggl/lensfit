"""Laser threshold experiment: P-I curve knee and population clamping."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, circle, line, path, svg_root, text


class LaserThresholdExperiment(OpticsExperiment):
    experiment_id = "laser-threshold"
    title = "激光阈值实验（P-I 曲线）"
    description = (
        "调节抽运功率与腔损耗，观察输出功率在阈值处的拐点："
        "阈值以下只有自发辐射，以上粒子数反转被钳制、光子数线性增长。"
    )
    difficulty = "intermediate"
    prerequisites = []
    linked_concepts = [
        "gain-medium",
        "population-inversion",
        "optical-resonator",
    ]
    linked_formulas = [
        "laser-threshold",
    ]
    learning_objectives = [
        "理解阈值条件：单程增益恰好补偿腔内损耗。",
        "掌握 P-I 曲线：阈值以下输出≈0，以上 P_out = ηs·(P_pump − P_th) 线性增长。",
        "理解增益钳制：阈值之上反转数不再增加，多余抽运全部转化为受激辐射光子。",
    ]
    parameters = [
        Parameter(
            name="pump_power_mw",
            label="抽运功率",
            type="float",
            default=150.0,
            min=0.0,
            max=500.0,
            step=5.0,
            unit="mW",
        ),
        Parameter(
            name="loss_per_pass_pct",
            label="腔内往返损耗",
            type="float",
            default=8.0,
            min=2.0,
            max=30.0,
            step=1.0,
            unit="%",
        ),
    ]

    # 教学模型常数：增益系数把抽运功率映射为小信号单程增益百分比。
    _GAIN_COEFF_PCT_PER_MW = 0.12
    _SLOPE_EFFICIENCY = 0.25

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        pump = float(params.get("pump_power_mw", 150.0))
        loss_pct = float(params.get("loss_per_pass_pct", 8.0))

        gain_pct_per_mw = self._GAIN_COEFF_PCT_PER_MW
        threshold_pump_mw = loss_pct / gain_pct_per_mw

        if pump >= threshold_pump_mw:
            output_mw = self._SLOPE_EFFICIENCY * (pump - threshold_pump_mw)
            inversion_rel = 1.0  # 阈值之上反转被钳制
            regime = "受激辐射主导"
        else:
            output_mw = 0.0
            inversion_rel = pump / threshold_pump_mw if threshold_pump_mw > 0 else 0.0
            regime = "荧光区（未达阈值）"

        sweep_max = 500.0
        curve_pumps = [i * sweep_max / 60 for i in range(61)]
        curve_outputs = [
            max(0.0, self._SLOPE_EFFICIENCY * (p - threshold_pump_mw))
            for p in curve_pumps
        ]

        svg = self._draw_svg(
            curve_pumps, curve_outputs, pump, output_mw,
            threshold_pump_mw, inversion_rel, regime,
        )

        return ExperimentResult(
            data={
                "pump_power_mw": pump,
                "threshold_pump_mw": round(threshold_pump_mw, 1),
                "output_power_mw": round(output_mw, 2),
                "inversion_relative": round(inversion_rel, 3),
                "regime": regime,
                "slope_efficiency": self._SLOPE_EFFICIENCY,
                "above_threshold": pump >= threshold_pump_mw,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "增大腔损耗 → 阈值升高、斜率效率不变：低损耗谐振腔是低阈值的前提。",
                "阈值之上反转数被「钳制」在临界值——这就是输出功率线性增长的原因。",
                "曲线在阈值以下的微弱输出是自发辐射进入腔模的部分（本模型中记为 0）。",
            ],
        )

    def _draw_svg(
        self,
        pumps: list[float],
        outputs: list[float],
        pump_now: float,
        out_now: float,
        thr: float,
        inversion_rel: float,
        regime: str,
    ) -> str:
        width, height = 640, 300
        ox, oy, span_x, span_y = 58.0, 28.0, 330.0, 190.0
        y_max = max(outputs) * 1.15 or 1.0

        def px(p: float, o: float):
            return ox + p / pumps[-1] * span_x, oy + span_y - o / y_max * span_y

        pts = " ".join(f"{px(p, o)[0]:.1f},{px(p, o)[1]:.1f}"
                       for p, o in zip(pumps, outputs))

        children: list[str] = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
            path("M" + pts, fill="none", stroke="#dc2626", stroke_width=2.5),
        ]

        tx = px(thr, 0)[0]
        children.append(line(tx, oy, tx, oy + span_y, stroke="#22c55e", dash="4"))
        children.append(text(tx + 4, oy + 14, f"阈值 {thr:.0f} mW", fill="#22c55e", font_size=10))

        op_x, op_y = px(pump_now, out_now)
        children.append(circle(op_x, op_y, 4, fill="#2563eb"))
        children.append(
            text(op_x + 6, op_y - 8, f"({pump_now:.0f} mW, {out_now:.0f} mW)",
                 fill="#2563eb", font_size=10)
        )

        p_ticks = [(i / 5 * span_x, f"{i / 5 * pumps[-1]:.0f}") for i in range(6)]
        children += axis_x(ox, oy + span_y, span_x, "抽运功率 (mW)", p_ticks)
        children.append(text(width / 2, height - 14,
                             f"工作区：{regime}｜反转相对值 {inversion_rel:.2f}",
                             fill="#334155", font_size=11, anchor="middle"))
        return svg_root(width, height, children)
