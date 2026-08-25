"""Fiber normalized frequency (V-number), mode count and cutoff."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, circle, line, path, svg_root, text

_V_SINGLE_MODE_CUTOFF = 2.405  # first zero of J0


class FiberVParameterExperiment(OpticsExperiment):
    experiment_id = "fiber-v-parameter"
    title = "光纤归一化频率（V 数）实验"
    description = (
        "调整纤芯直径、数值孔径与波长，计算归一化频率 V、"
        "支持的模式数，并判定单模/多模工作状态。"
    )
    difficulty = "intermediate"
    prerequisites = []
    linked_concepts = [
        "single-mode-fiber",
        "multi-mode-fiber",
        "acceptance-angle",
    ]
    linked_formulas = [
        "fiber-v-parameter",
        "fiber-na",
    ]
    learning_objectives = [
        "掌握 V = (2πa/λ)·NA 的物理含义：归一化频率决定可传播模式数。",
        "掌握阶跃折射率光纤模式数 ≈ V²/2。",
        "掌握单模条件 V < 2.405 及截止波长 λc = π·d·NA / 2.405。",
    ]
    parameters = [
        Parameter(
            name="core_diameter_um",
            label="纤芯直径 d",
            type="float",
            default=9.0,
            min=4.0,
            max=100.0,
            step=0.2,
            unit="µm",
        ),
        Parameter(
            name="numerical_aperture",
            label="数值孔径 NA",
            type="float",
            default=0.13,
            min=0.05,
            max=0.5,
            step=0.01,
        ),
        Parameter(
            name="wavelength_nm",
            label="工作波长",
            type="float",
            default=1550.0,
            min=600.0,
            max=2000.0,
            step=10.0,
            unit="nm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        d_um = float(params.get("core_diameter_um", 9.0))
        na = float(params.get("numerical_aperture", 0.13))
        lam_nm = float(params.get("wavelength_nm", 1550.0))

        v_number = math.pi * d_um * na / lam_nm
        modes_approx = max(1, round(v_number**2 / 2)) if v_number > 0 else 1
        single_mode = v_number < _V_SINGLE_MODE_CUTOFF
        cutoff_nm = math.pi * d_um * na / _V_SINGLE_MODE_CUTOFF * 1e3

        svg = self._draw_svg(lam_nm, d_um, na, single_mode)

        return ExperimentResult(
            data={
                "core_diameter_um": d_um,
                "numerical_aperture": na,
                "wavelength_nm": lam_nm,
                "v_number": round(v_number, 3),
                "mode_count_approx": modes_approx if not single_mode else 2,
                "single_mode": single_mode,
                "cutoff_wavelength_nm": round(cutoff_nm, 1),
                "regime": "单模" if single_mode else "少模/多模",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "V < 2.405 时只有基模（LP₀₁）传播——这就是单模光纤的定义。",
                "工作波长高于截止波长 λc 时进入单模区：长波反而更容易单模。",
                "通信常用 G.652 光纤：d≈9 µm，NA≈0.14，λc≈1260 nm。",
            ],
        )

    def _draw_svg(self, lam_nm: float, d_um: float, na: float, single_mode: bool) -> str:
        width, height = 640, 300
        ox, oy, span_x, span_y = 56.0, 28.0, 300.0, 170.0

        # V vs wavelength curve over 600–2000 nm.
        lam_min, lam_max = 600.0, 2000.0
        pts = []
        for i in range(61):
            lam = lam_min + i * (lam_max - lam_min) / 60
            v = math.pi * d_um * na / lam
            x = ox + (lam - lam_min) / (lam_max - lam_min) * span_x
            y = oy + span_y - min(1.0, v / 12.0) * span_y
            pts.append(f"{x:.1f},{y:.1f}")
            if i == 0:
                vx, vy = x, oy + span_y - min(1.0, _V_SINGLE_MODE_CUTOFF / 12.0) * span_y

        children: list[str] = [
            line(ox, oy + span_y, ox + span_x, oy + span_y, stroke="#475569"),
            path("M" + " ".join(pts), fill="none", stroke="#3b82f6", stroke_width=2),
            line(ox, vy, ox + span_x, vy, stroke="#dc2626", dash="4"),
            text(ox + span_x - 4, vy - 6, "V = 2.405 单模截止线", fill="#dc2626",
                 font_size=10, anchor="end"),
        ]
        op_x = ox + (lam_nm - lam_min) / (lam_max - lam_min) * span_x
        v_op = math.pi * d_um * na / lam_nm
        op_y = oy + span_y - min(1.0, v_op / 12.0) * span_y
        children.append(circle(op_x, op_y, 4, fill="#16a34a"))
        children.append(
            text(op_x + 6, op_y - 6, f"λ={lam_nm:.0f} nm\nV={v_op:.2f}".split(chr(10))[0],
                 fill="#16a34a", font_size=10)
        )
        nm_ticks = [(i / 4 * span_x, f"{600 + i / 4 * 1400:.0f}") for i in range(5)]
        children += axis_x(ox, oy + span_y, span_x, "波长 (nm)", nm_ticks)
        v_ticks = [(i / 3 * span_y, f"{12 * (1 - i / 3):.0f}") for i in range(4)]
        children += axis_y(ox, oy + span_y, span_y, "V 数", v_ticks)

        status_color = "#16a34a" if single_mode else "#b45309"
        panel_x = ox + span_x + 30.0
        children += [
            text(panel_x, 70.0, f"V = {v_number:.2f}", fill="#0f172a", font_size=15),
            text(panel_x, 96.0, f"模式数 ≈ {modes_approx}", fill="#334155", font_size=12),
            text(panel_x, 122.0, f"状态：{'单模' if single_mode else '多模'}",
                 fill=status_color, font_size=13),
            text(panel_x, 148.0, f"截止波长 λc ≈ {cutoff_nm:.0f} nm", fill="#475569",
                 font_size=11),
            text(panel_x, 176.0, f"d={d_um:.1f} µm  NA={na:.2f}", fill="#94a3b8",
                 font_size=10),
        ]
        return svg_root(width, height, children)
