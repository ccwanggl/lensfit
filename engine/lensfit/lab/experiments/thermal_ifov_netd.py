"""Thermal imaging IFOV and NETD experiment."""

from __future__ import annotations

import math
from typing import Any

from lensfit.lab.base import ExperimentResult, OpticsExperiment, Parameter
from lensfit.lab.renderer import line, polygon, svg_root, text


class ThermalIfovNetdExperiment(OpticsExperiment):
    experiment_id = "thermal-ifov-netd"
    title = "热成像 IFOV 与 NETD 实验"
    description = (
        "给定焦距、像元尺寸、目标距离与 NETD，"
        "计算瞬时视场角、投影像元尺寸、目标覆盖像素数及温度分辨能力。"
    )
    difficulty = "advanced"
    prerequisites = ["magnification-scale", "angle-of-view"]
    linked_concepts = [
        "10-concepts/NETD",
        "10-concepts/微测辐射热计",
    ]
    learning_objectives = [
        "理解 IFOV = 像元尺寸 / 焦距。",
        "掌握投影像元尺寸随目标距离线性增长。",
        "认识 NETD 是系统能分辨的最小温差，目标温差必须大于 NETD 才能可靠检测。",
    ]
    parameters = [
        Parameter(
            name="focal_length_mm",
            label="焦距",
            type="float",
            default=25.0,
            min=5.0,
            max=100.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="pixel_size_um",
            label="像元尺寸",
            type="float",
            default=17.0,
            min=5.0,
            max=50.0,
            step=1.0,
            unit="μm",
        ),
        Parameter(
            name="target_distance_m",
            label="目标距离",
            type="float",
            default=5.0,
            min=0.5,
            max=100.0,
            step=0.5,
            unit="m",
        ),
        Parameter(
            name="target_size_mm",
            label="目标尺寸",
            type="float",
            default=50.0,
            min=1.0,
            max=500.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="netd_mk",
            label="NETD",
            type="float",
            default=50.0,
            min=10.0,
            max=200.0,
            step=5.0,
            unit="mK",
        ),
        Parameter(
            name="target_delta_t_k",
            label="目标与背景温差",
            type="float",
            default=5.0,
            min=0.1,
            max=50.0,
            step=0.1,
            unit="K",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f_mm = float(params.get("focal_length_mm", 25.0))
        pixel_um = float(params.get("pixel_size_um", 17.0))
        distance_m = float(params.get("target_distance_m", 5.0))
        target_mm = float(params.get("target_size_mm", 50.0))
        netd_mk = float(params.get("netd_mk", 50.0))
        delta_t_k = float(params.get("target_delta_t_k", 5.0))

        # IFOV (rad) = pixel pitch / focal length.
        ifov_rad = (pixel_um / 1000.0) / f_mm
        ifov_mrad = ifov_rad * 1000.0

        # Projected pixel / spot size at target distance.
        projected_pixel_mm = ifov_rad * distance_m * 1000.0
        pixels_across = target_mm / projected_pixel_mm

        # SNR relative to NETD.
        netd_k = netd_mk / 1000.0
        snr = delta_t_k / netd_k
        detectable = snr >= 3.0

        # Total FOV for a small 640x480 sensor (just for reference).
        sensor_width_mm = 640 * pixel_um / 1000.0
        hfov_deg = 2.0 * math.degrees(math.atan((sensor_width_mm / 2.0) / f_mm))

        svg = self._draw_svg(
            f_mm,
            pixel_um,
            distance_m,
            target_mm,
            projected_pixel_mm,
            ifov_mrad,
            delta_t_k,
            netd_mk,
            detectable,
        )

        return ExperimentResult(
            data={
                "focal_length_mm": f_mm,
                "pixel_size_um": pixel_um,
                "target_distance_m": distance_m,
                "target_size_mm": target_mm,
                "netd_mk": netd_mk,
                "target_delta_t_k": delta_t_k,
                "ifov_rad": round(ifov_rad, 6),
                "ifov_mrad": round(ifov_mrad, 3),
                "projected_pixel_size_mm": round(projected_pixel_mm, 3),
                "pixels_across_target": round(pixels_across, 2),
                "horizontal_fov_deg": round(hfov_deg, 2),
                "snr": round(snr, 2),
                "detectable": detectable,
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "IFOV 只由像元尺寸和焦距决定，与目标距离无关。",
                "投影像元尺寸 = IFOV × 目标距离，因此远距离目标需要更多像素覆盖。",
                "NETD 是系统噪声决定的温度分辨极限；信噪比 SNR = ΔT / NETD，通常要求 SNR > 3。",
                "本实验未考虑大气衰减、镜头透过率和探测器 fill factor。",
            ],
        )

    def _draw_svg(
        self,
        f_mm: float,
        pixel_um: float,
        distance_m: float,
        target_mm: float,
        projected_pixel_mm: float,
        ifov_mrad: float,
        delta_t_k: float,
        netd_mk: float,
        detectable: bool,
    ) -> str:
        width, height = 640, 360
        lens_x, lens_y = 80, 180
        sensor_x, sensor_y = 30, 180
        target_x = 520

        # Vertical scale: target size and projected pixel.
        max_draw_height = 160
        # Draw target with height proportional to its size, capped.
        target_draw_h = min(max_draw_height, target_mm * 2.0)
        target_top = lens_y - target_draw_h / 2
        target_bottom = lens_y + target_draw_h / 2

        children: list[str] = []

        # Optical axis.
        children.append(
            line(lens_x, lens_y, target_x + 40, lens_y, stroke="#475569", stroke_width=1)
        )

        # Lens.
        children.extend(
            [
                line(lens_x, lens_y - 40, lens_x, lens_y + 40, stroke="#334155", stroke_width=6),
                text(
                    lens_x,
                    lens_y + 60,
                    f"f={f_mm:.0f} mm",
                    fill="#64748b",
                    font_size=10,
                    anchor="middle",
                ),
            ]
        )

        # Sensor.
        children.extend(
            [
                line(
                    sensor_x,
                    sensor_y - 25,
                    sensor_x,
                    sensor_y + 25,
                    stroke="#ef4444",
                    stroke_width=4,
                ),
                text(
                    sensor_x,
                    sensor_y + 45,
                    f"p={pixel_um:.1f} μm",
                    fill="#64748b",
                    font_size=10,
                    anchor="middle",
                ),
            ]
        )

        # Target rectangle (hot object).
        target_color = "#ef4444" if detectable else "#94a3b8"
        children.extend(
            [
                polygon(
                    [
                        (target_x, target_top),
                        (target_x + 30, target_top),
                        (target_x + 30, target_bottom),
                        (target_x, target_bottom),
                    ],
                    fill=target_color,
                    stroke="#475569",
                ),
                text(
                    target_x + 15,
                    target_bottom + 20,
                    f"目标 {target_mm:.0f} mm",
                    fill="#64748b",
                    font_size=10,
                    anchor="middle",
                ),
            ]
        )

        # Distance label.
        children.append(
            text(
                (lens_x + target_x) / 2,
                lens_y + 40,
                f"D={distance_m:.1f} m",
                fill="#64748b",
                font_size=11,
                anchor="middle",
            )
        )

        # Field cone (IFOV).
        half_angle_px = 120  # arbitrary visual cone length
        cone_top_y = lens_y - half_angle_px * (ifov_mrad / 5.0)
        cone_bottom_y = lens_y + half_angle_px * (ifov_mrad / 5.0)
        children.extend(
            [
                line(
                    lens_x,
                    lens_y,
                    target_x,
                    cone_top_y,
                    stroke="#f59e0b",
                    stroke_width=1,
                    dash="4",
                    opacity=0.7,
                ),
                line(
                    lens_x,
                    lens_y,
                    target_x,
                    cone_bottom_y,
                    stroke="#f59e0b",
                    stroke_width=1,
                    dash="4",
                    opacity=0.7,
                ),
                text(
                    target_x - 10,
                    cone_top_y - 10,
                    f"IFOV={ifov_mrad:.3f} mrad",
                    fill="#f59e0b",
                    font_size=10,
                    anchor="end",
                ),
            ]
        )

        # Projected pixel size marker on target.
        proj_draw_h = min(target_draw_h * 0.3, projected_pixel_mm * 2.0)
        children.extend(
            [
                line(
                    target_x + 35,
                    lens_y - proj_draw_h / 2,
                    target_x + 35,
                    lens_y + proj_draw_h / 2,
                    stroke="#22c55e",
                    stroke_width=3,
                ),
                text(
                    target_x + 45,
                    lens_y,
                    f"≈{projected_pixel_mm:.2f} mm/px",
                    fill="#22c55e",
                    font_size=10,
                    anchor="start",
                ),
            ]
        )

        # Info panel.
        status_text = "可检测" if detectable else "不可检测（SNR<3）"
        snr_value = delta_t_k / (netd_mk / 1000.0)
        children.extend(
            [
                polygon(
                    [(20, 20), (620, 20), (620, 60), (20, 60)],
                    fill="#f1f5f9",
                    stroke="#cbd5e1",
                ),
                text(
                    30,
                    40,
                    (
                        f"温差 ΔT={delta_t_k:.1f} K  |  NETD={netd_mk:.0f} mK  "
                        f"|  SNR={snr_value:.1f} — {status_text}"
                    ),
                    fill="#334155",
                    font_size=12,
                ),
                text(
                    30,
                    340,
                    "注：未考虑大气衰减、镜头透过率与探测器 fill factor。",
                    fill="#64748b",
                    font_size=10,
                ),
            ]
        )

        return svg_root(width, height, children)
