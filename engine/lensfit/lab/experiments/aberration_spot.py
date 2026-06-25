"""Lens aberration spot-diagram experiment."""

from __future__ import annotations

import math
from typing import Any

from lensfit.lab.base import ExperimentResult, OpticsExperiment, Parameter
from lensfit.lab.renderer import circle, line, svg_root, text


class AberrationSpotExperiment(OpticsExperiment):
    experiment_id = "aberration-spot"
    title = "透镜像差点列图实验"
    description = "用低阶赛德尔像差生成瞳面网格光线，计算横向像差并绘制点列图。"
    difficulty = "advanced"
    prerequisites = ["thin-lens", "chromatic-aberration", "mtf-explorer"]
    linked_concepts = [
        "50-learning/06-aberrations",
        "50-learning/11-optical-design-basics",
    ]
    learning_objectives = [
        "理解球差、彗差、像散、场曲、畸变对点列图形状的影响。",
        "观察同一组像差在不同视场高度下产生的点列差异。",
        "认识 RMS 点列半径与几何点列直径的物理意义。",
    ]
    parameters = [
        Parameter(
            name="spherical",
            label="球差系数 S1",
            type="float",
            default=0.0,
            min=-1.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="coma",
            label="彗差系数 S2",
            type="float",
            default=0.0,
            min=-1.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="astigmatism",
            label="像散系数 S3",
            type="float",
            default=0.0,
            min=-1.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="field_curvature",
            label="场曲系数 S4",
            type="float",
            default=0.0,
            min=-1.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="distortion",
            label="畸变系数 S5",
            type="float",
            default=0.0,
            min=-1.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="field_height",
            label="视场高度 (归一化)",
            type="float",
            default=0.5,
            min=0.0,
            max=1.0,
            step=0.05,
        ),
        Parameter(
            name="num_rays",
            label="光线数",
            type="int",
            default=128,
            min=32,
            max=512,
            step=32,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        s1 = float(params.get("spherical", 0.0))
        s2 = float(params.get("coma", 0.0))
        s3 = float(params.get("astigmatism", 0.0))
        s4 = float(params.get("field_curvature", 0.0))
        s5 = float(params.get("distortion", 0.0))
        h = float(params.get("field_height", 0.5))
        num_rays = int(params.get("num_rays", 128))

        rays = self._trace_rays(s1, s2, s3, s4, s5, h, num_rays)

        if rays:
            xs = [r[0] for r in rays]
            ys = [r[1] for r in rays]
            rms_radius = math.sqrt(sum(x**2 + y**2 for x, y in rays) / len(rays))
            geo_radius = max(math.hypot(x, y) for x, y in rays)
            centroid_x = sum(xs) / len(xs)
            centroid_y = sum(ys) / len(ys)
        else:
            rms_radius = geo_radius = centroid_x = centroid_y = 0.0

        svg = self._draw_svg(rays, rms_radius, geo_radius, centroid_x, centroid_y)

        return ExperimentResult(
            data={
                "spherical": s1,
                "coma": s2,
                "astigmatism": s3,
                "field_curvature": s4,
                "distortion": s5,
                "field_height": h,
                "num_rays": num_rays,
                "rms_radius": round(rms_radius, 4),
                "geometric_radius": round(geo_radius, 4),
                "centroid": [round(centroid_x, 4), round(centroid_y, 4)],
                "spot_rays": rays,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "球差使不同环带光线聚焦在不同像面位置，点列呈同心圆状展宽。",
                "彗差产生不对称的彗星状拖尾。",
                "像散使子午和弧矢光线聚焦在不同位置，点列呈椭圆形。",
                "畸变只改变像点位置而不扩大点列斑（理想点仍为一个点）。",
                "本实验使用简化赛德尔多项式；真实镜头需逐面光线追迹。",
            ],
        )

    @staticmethod
    def _trace_rays(
        s1: float,
        s2: float,
        s3: float,
        s4: float,
        s5: float,
        h: float,
        num_rays: int,
    ) -> list[tuple[float, float]]:
        """Trace a grid of rays through a Seidel aberration model.

        Returns a list of (δx, δy) transverse ray aberrations in normalized
        image-plane units.
        """
        # Scale factor maps dimensionless UI coefficients to image-plane units.
        scale = 80.0
        rays: list[tuple[float, float]] = []

        num_rings = max(3, int(math.sqrt(num_rays / 4)))
        num_angles = max(6, num_rays // num_rings)

        for i in range(1, num_rings + 1):
            rho = i / num_rings
            for j in range(num_angles):
                theta = 2.0 * math.pi * j / num_angles
                dx, dy = _seidel_transverse_aberration(s1, s2, s3, s4, s5, h, rho, theta)
                rays.append((scale * dx, scale * dy))

        # Add chief ray (pupil center) if distortion is present to show image shift.
        if s5 != 0.0 and h > 0.0:
            # For ρ -> 0, only distortion contributes: δx ≈ -scale * S5 * h³
            rays.append((-scale * s5 * h**3, 0.0))

        return rays

    def _draw_svg(
        self,
        rays: list[tuple[float, float]],
        rms_radius: float,
        geo_radius: float,
        centroid_x: float,
        centroid_y: float,
    ) -> str:
        width, height = 480, 480
        cx, cy = width // 2, height // 2
        plot_radius = 200

        children: list[str] = []

        # Plot frame.
        children.extend(
            [
                circle(cx, cy, plot_radius, fill="none", stroke="#334155", stroke_width=1),
                line(cx - plot_radius, cy, cx + plot_radius, cy, stroke="#475569", stroke_width=1),
                line(cx, cy - plot_radius, cx, cy + plot_radius, stroke="#475569", stroke_width=1),
            ]
        )

        # Auto-scale so the spot fits inside the plot.
        max_coord = max(
            [abs(v) for v in (centroid_x, centroid_y)]
            + [math.hypot(x, y) for x, y in rays]
            + [1e-6]
        )
        display_scale = (plot_radius * 0.85) / max_coord if max_coord > 0 else 1.0

        # Draw rays as small circles.
        for x, y in rays:
            px = cx + (x - centroid_x) * display_scale
            py = cy - (y - centroid_y) * display_scale
            children.append(circle(px, py, 1.5, fill="#38bdf8", stroke="none"))

        # Centroid marker.
        children.append(circle(cx, cy, 3, fill="#ef4444", stroke="none"))

        # RMS and geometric circles.
        children.extend(
            [
                circle(cx, cy, rms_radius * display_scale, fill="none", stroke="#22c55e", dash="4"),
                circle(cx, cy, geo_radius * display_scale, fill="none", stroke="#f59e0b", dash="2"),
            ]
        )

        children.extend(
            [
                text(
                    cx,
                    30,
                    "点列图（中心为光斑质心）",
                    fill="#334155",
                    font_size=13,
                    anchor="middle",
                ),
                text(
                    20,
                    height - 50,
                    f"RMS 半径 = {rms_radius:.2f} 单位",
                    fill="#22c55e",
                    font_size=11,
                ),
                text(
                    20,
                    height - 30,
                    f"几何半径 = {geo_radius:.2f} 单位",
                    fill="#f59e0b",
                    font_size=11,
                ),
            ]
        )

        return svg_root(width, height, children)


def _seidel_transverse_aberration(
    s1: float,
    s2: float,
    s3: float,
    s4: float,
    s5: float,
    h: float,
    rho: float,
    theta: float,
) -> tuple[float, float]:
    """Return (δx, δy) transverse aberration from Seidel wavefront derivatives.

    Wavefront aberration:
    W = S1 ρ⁴ + S2 h ρ³ cosθ + S3 h² ρ² cos²θ + S4 h² ρ² + S5 h³ ρ cosθ

    Transverse aberrations are proportional to the negative gradient of W in
    pupil coordinates.
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    dw_drho = (
        4.0 * s1 * rho**3
        + 3.0 * s2 * h * rho**2 * cos_t
        + 2.0 * s3 * h**2 * rho * cos_t**2
        + 2.0 * s4 * h**2 * rho
        + s5 * h**3 * cos_t
    )

    dw_dtheta = (
        -s2 * h * rho**3 * sin_t
        - 2.0 * s3 * h**2 * rho**2 * cos_t * sin_t
        - s5 * h**3 * rho * sin_t
    )

    if rho > 1e-9:
        dw_dx = dw_drho * cos_t - (dw_dtheta / rho) * sin_t
        dw_dy = dw_drho * sin_t + (dw_dtheta / rho) * cos_t
    else:
        dw_dx = dw_dy = 0.0

    # Negative gradient gives transverse ray aberration direction.
    return -dw_dx, -dw_dy
