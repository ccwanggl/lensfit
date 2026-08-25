"""Perspective distortion: pinhole projection of a ground-plane grid."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, svg_root, text


class PerspectiveDistortionExperiment(OpticsExperiment):
    experiment_id = "perspective-distortion"
    title = "透视畸变实验"
    description = (
        "针孔相机俯仰拍摄地面方格网：观察「近大远小」造成的梯形收缩、"
        "平行线向灭点汇聚，以及它们与镜头畸变的本质区别。"
    )
    difficulty = "intermediate"
    prerequisites = ["thin-lens"]
    linked_concepts = [
        "透视畸变",
    ]
    linked_formulas: list[str] = []
    learning_objectives = [
        "理解透视投影 x' = f·X/Z：像点位置与物距成反比。",
        "区分透视畸变（投影几何必然）与镜头畸变（光学缺陷，可标定校正）。",
        "观察俯仰拍摄时地面平行线在像面上汇聚于灭点。",
    ]
    parameters = [
        Parameter(
            name="focal_mm",
            label="焦距",
            type="float",
            default=24.0,
            min=8.0,
            max=85.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="camera_height_m",
            label="相机高度",
            type="float",
            default=1.5,
            min=0.3,
            max=4.0,
            step=0.1,
            unit="m",
        ),
        Parameter(
            name="pitch_deg",
            label="俯仰角",
            type="float",
            default=30.0,
            min=5.0,
            max=60.0,
            step=5.0,
            unit="°",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f_mm = float(params.get("focal_mm", 24.0))
        h_m = float(params.get("camera_height_m", 1.5))
        pitch_deg = float(params.get("pitch_deg", 30.0))

        svg = self._draw_svg(f_mm, h_m, pitch_deg)

        return ExperimentResult(
            data={
                "focal_mm": f_mm,
                "camera_height_m": h_m,
                "pitch_deg": pitch_deg,
                "model": "pinhole",
                "note": "直线仍为直线（无弯曲）；变形来自投影几何，非镜头质量",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "x' = f·X/Z：同一物宽在近处占据更多像素——「近大远小」的解析形式。",
                "地面平行线在像面上汇聚于灭点（深度方向无穷远的投影）。",
                "透视变形由拍摄几何决定，换镜头不会消失；镜头畸变则可标定去除。",
            ],
        )

    def _draw_svg(self, f_mm: float, h_m: float, pitch_deg: float) -> str:
        width, height = 640, 320
        cx, cy = width / 2, 150.0
        px_per_mm = 6.0
        pitch = math.radians(pitch_deg)

        def project(world_x: float, world_z: float):
            zc = world_z * math.cos(pitch) + h_m * math.sin(pitch)
            yc = h_m * math.cos(pitch) - world_z * math.sin(pitch)
            if zc <= 0.05:
                return None
            u = f_mm * world_x / zc
            v = -f_mm * yc / zc
            if abs(u) > 260 or v > 130 or v < -120:
                return None
            return cx + u * px_per_mm, cy - v * px_per_mm

        children: list[str] = []

        depth_rows = [round(0.5 + i * 0.5, 1) for i in range(20)]
        for z in depth_rows:
            a = project(-2.5, z)
            b = project(2.5, z)
            if a and b:
                children.append(line(a[0], a[1], b[0], b[1], stroke="#94a3b8"))
        for xw in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
            near = project(xw, 0.4)
            far = project(xw, 12.0)
            if near and far:
                children.append(
                    line(near[0], near[1], far[0], far[1], stroke="#cbd5e1", dash="3")
                )

        children.append(
            text(width / 2, height - 40,
                 "↑ 远处行间距趋近于 0，两侧横线向灭点收敛",
                 fill="#22c55e", font_size=10, anchor="middle")
        )
        children.append(
            text(width / 2, height - 20,
                 f"f={f_mm:.0f} mm　h={h_m:.1f} m　俯仰 {pitch_deg:.0f}°　"
                 "方格网为等距真实网格",
                 fill="#475569", font_size=11, anchor="middle")
        )
        return svg_root(width, height, children)
