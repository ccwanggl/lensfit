"""Lambertian cosine law: angular intensity distribution of a diffuse emitter."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, line, path, svg_root, text


class LambertianRadianceExperiment(OpticsExperiment):
    experiment_id = "lambertian-radiance"
    title = "朗伯体角分布实验"
    description = (
        "观察朗伯（理想漫射）表面的辐射强度按 cosθ 余弦定律分布，"
        "理解「亮度与观察方向无关」的朗伯定义。"
    )
    difficulty = "foundation"
    prerequisites = []
    linked_concepts = [
        "lambertian-emitter",
        "lambertian-surface",
    ]
    linked_formulas = [
        "lambert-cosine",
    ]
    learning_objectives = [
        "掌握朗伯余弦定律 I(θ) = I₀·cosθ。",
        "理解强度按 cosθ 下降、投影面积也按 cosθ 缩小，两者相除使亮度 L 保持常数。",
        "认识白纸、氧化镁、毛玻璃等近似朗伯面的工程价值。",
    ]
    parameters = [
        Parameter(
            name="normal_intensity",
            label="法向辐射强度 I₀",
            type="float",
            default=60.0,
            min=10.0,
            max=100.0,
            step=5.0,
        ),
        Parameter(
            name="viewing_angle_deg",
            label="观察方向角 θ",
            type="float",
            default=30.0,
            min=0.0,
            max=85.0,
            step=1.0,
            unit="°",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        i0 = float(params.get("normal_intensity", 60.0))
        theta_deg = float(params.get("viewing_angle_deg", 30.0))
        cos_t = math.cos(math.radians(theta_deg))

        i_theta = i0 * cos_t
        radiance_relative = i_theta / cos_t if cos_t > 1e-9 else None

        svg = self._draw_svg(i0, theta_deg, i_theta)

        return ExperimentResult(
            data={
                "normal_intensity": i0,
                "viewing_angle_deg": theta_deg,
                "intensity_at_angle": round(i_theta, 2),
                "projected_area_cos": round(cos_t, 4),
                "radiance_relative": round(radiance_relative, 2)
                if radiance_relative is not None
                else None,
                "radiance_constant": True,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "I(θ)=I₀cosθ：每个方向的强度都在变小，但看到的发光面也按 cosθ 缩小。",
                "两者相除恰好抵消——朗伯面亮度 L 与观察方向无关，即「均匀亮面」。",
                "投影幕布、标准白板做成近似朗伯面，保证各角度观众看到相同亮度。",
            ],
        )

    def _draw_svg(self, i0: float, theta_deg: float, i_theta: float) -> str:
        width, height = 640, 320
        cx, cy = width / 2 - 30, height / 2 + 26
        r_max = 100.0
        scale = r_max / i0

        def polar_px(angle_deg: float, radius_val: float) -> tuple[float, float]:
            rad = math.radians(angle_deg - 90.0)
            rr = radius_val * scale
            return cx + rr * math.cos(rad), cy + rr * math.sin(rad)

        children: list[str] = []
        for frac in (0.25, 0.5, 0.75, 1.0):
            children.append(circle(cx, cy, r_max * frac, stroke="#e2e8f0"))
        for deg in range(-90, 91, 30):
            x2, y2 = polar_px(deg, i0)
            children.append(line(cx, cy, x2, y2, stroke="#f1f5f9"))

        lobe_pts = []
        for deg in range(-89, 90, 2):
            x2, y2 = polar_px(deg, i0 * math.cos(math.radians(deg)))
            lobe_pts.append(f"{x2:.1f},{y2:.1f}")
        children.append(
            path(f"M{cx:.1f},{cy:.1f} L" + " L".join(lobe_pts) + f" L{cx:.1f},{cy:.1f} Z",
                 fill="rgba(245,158,11,0.3)")
        )

        children.append(line(cx - 45, cy, cx + 45, cy, stroke="#334155", stroke_width=4))
        children.append(
            text(cx, cy + 24, "朗伯面（法向朝上）", fill="#334155", font_size=11, anchor="middle")
        )

        vx, vy = polar_px(theta_deg, max(i_theta, i0 * 0.12))
        children.append(line(cx, cy, vx, vy, stroke="#dc2626", stroke_width=2))
        children.append(text(vx + 6, vy - 6, f"I(θ)={i_theta:.1f}", fill="#dc2626", font_size=11))

        children.append(
            text(width / 2, height - 14,
                 f"I(θ) = I₀·cosθ = {i0:.0f}·cos{theta_deg:.0f}° = {i_theta:.1f}"
                 f"　｜　亮度 L = I(θ)/cosθ = 常数",
                 fill="#475569", font_size=11, anchor="middle")
        )
        return svg_root(width, height, children)
