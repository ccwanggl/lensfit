"""Rolling vs global shutter experiment with jelly-effect distortion."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import rect, svg_root, text


class ShutterTimingExperiment(OpticsExperiment):
    experiment_id = "shutter-timing"
    title = "快门时序实验（卷帘 vs 全局）"
    description = (
        "让目标高速横穿视场，对比全局快门（整帧同时曝光）与"
        "卷帘快门（逐行曝光）的成像差异——果冻效应的成因。"
    )
    difficulty = "foundation"
    prerequisites = []
    linked_concepts = [
        "卷帘快门",
        "全局快门",
        "果冻效应",
    ]
    linked_formulas: list[str] = []
    learning_objectives = [
        "理解卷帘快门逐行曝光：每行看到的是不同时刻的场景。",
        "理解果冻效应：行间时间差 × 目标速度 = 像内错位/倾斜。",
        "掌握选型直觉：拍摄高速运动优先全局快门。",
    ]
    parameters = [
        Parameter(
            name="shutter_mode",
            label="快门类型",
            type="choice",
            default="rolling",
            options=[
                {"value": "rolling", "label": "卷帘快门"},
                {"value": "global", "label": "全局快门"},
            ],
        ),
        Parameter(
            name="speed_px_per_frame",
            label="目标速度",
            type="float",
            default=180.0,
            min=0.0,
            max=600.0,
            step=10.0,
            unit="px/帧",
        ),
        Parameter(
            name="readout_fraction",
            label="读出时长占帧比",
            type="float",
            default=0.8,
            min=0.1,
            max=1.0,
            step=0.05,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        mode = params.get("shutter_mode", "rolling")
        speed = float(params.get("speed_px_per_frame", 180.0))
        readout_frac = float(params.get("readout_fraction", 0.8))

        width, height = 640, 300
        obj_w, obj_h = 70.0, 46.0
        base_x = -obj_w + (width + 2 * obj_w) * 0.55

        children: list[str] = [
            rect(8, 8, width - 16, height - 52, fill="#0f172a"),
        ]

        if mode == "global":
            x0 = base_x - speed / 2
            children.append(rect(x0, height / 2 - obj_h / 2 - 12, obj_w, obj_h,
                                 fill="#38bdf8"))
            children.append(text(x0 + obj_w / 2, height / 2 + obj_h / 2 + 4,
                                 "整帧同时曝光 → 形状无畸变", fill="#7dd3fc",
                                 font_size=10, anchor="middle"))
            skew_note = "全局快门：所有行同一时刻采样，快速目标也保持矩形。"
            shift_total = 0.0
        else:
            rows = 24
            row_h = (height - 52) / rows
            shift_total = speed * readout_frac
            for i in range(rows):
                frac = i / (rows - 1)          # 0 top .. 1 bottom
                row_time_frac = frac * readout_frac
                x0 = base_x - speed * row_time_frac
                y = 8 + i * row_h
                children.append(rect(x0, y, obj_w, row_h + 0.5, fill="#38bdf8"))
            skew_note = (
                f"逐行曝光：首行到末行时间差 {readout_frac*100:.0f}% 帧，"
                f"累计错位 {shift_total:.0f} px → 平行四边形倾斜（果冻效应）。"
            )

        children.append(text(width / 2, height - 30,
                             f"速度 {speed:.0f} px/帧　模式 {mode}", fill="#94a3b8",
                             font_size=11, anchor="middle"))
        children.append(text(width / 2, height - 12, skew_note,
                             fill="#475569", font_size=11, anchor="middle"))

        svg = svg_root(width, height, children)

        return ExperimentResult(
            data={
                "mode": mode,
                "speed_px_per_frame": speed,
                "readout_fraction": readout_frac,
                "max_skew_px": round(shift_total, 1),
                "shape_preserved": mode == "global",
            },
            svg=svg,
            warnings=[],
        )

        return ExperimentResult(
            data={
                "mode": mode,
                "speed_px_per_frame": speed,
                "readout_fraction": readout_frac,
                "max_skew_px": round(shift_total, 1),
                "shape_preserved": mode == "global",
            },
            svg=svg,
            warnings=[],
        )
