"""Lateral magnification and pixel precision experiment."""

from __future__ import annotations

from typing import Any

from lensfit.core.thin_lens import ThinLensCalculator
from lensfit.lab.base import ExperimentResult, OpticsExperiment, Parameter
from lensfit.lab.renderer import arrow, line, svg_root, text


class MagnificationScaleExperiment(OpticsExperiment):
    experiment_id = "magnification-scale"
    title = "放大倍率与像素精度实验"
    description = (
        "给定焦距、工作距离和像元尺寸，计算横向放大倍率、像素精度及"
        "物体特征在传感器上占据的像素数。"
    )
    difficulty = "foundation"
    prerequisites = ["thin-lens", "angle-of-view"]
    linked_concepts = [
        "10-concepts/像素精度",
        "10-concepts/工作距离",
        "10-concepts/focal-length",
        "20-formulas/lateral-magnification",
        "20-formulas/pixel-precision",
        "20-formulas/focal-length-from-wd",
    ]
    learning_objectives = [
        "理解放大倍率 β = f / (WD - f) 的物理意义。",
        "认识像素精度 = 像元尺寸 / |β|。",
        "估算物体特征在成像平面上占据的像素数。",
    ]
    parameters = [
        Parameter(
            name="focal_length",
            label="焦距",
            type="float",
            default=25.0,
            min=5.0,
            max=200.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="working_distance",
            label="工作距离",
            type="float",
            default=200.0,
            min=20.0,
            max=2000.0,
            step=5.0,
            unit="mm",
        ),
        Parameter(
            name="pixel_size_um",
            label="像元尺寸",
            type="float",
            default=3.45,
            min=0.5,
            max=20.0,
            step=0.1,
            unit="μm",
        ),
        Parameter(
            name="object_feature_mm",
            label="物体特征尺寸",
            type="float",
            default=1.0,
            min=0.01,
            max=100.0,
            step=0.1,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f = float(params.get("focal_length", 25.0))
        wd = float(params.get("working_distance", 200.0))
        pixel_um = float(params.get("pixel_size_um", 3.45))
        feature_mm = float(params.get("object_feature_mm", 1.0))

        warnings: list[str] = []

        # Ensure WD > f for a real finite image
        if wd <= f:
            wd = f + 0.1
            warnings.append(
                "工作距离必须大于焦距才能成实像；已自动调整到略大于焦距。"
            )

        calc = ThinLensCalculator()
        beta = calc.magnification_from_focal_wd(f, wd)
        pixel_precision_um = pixel_um / abs(beta)  # object-space size per pixel
        projected_feature_mm = feature_mm * abs(beta)
        projected_feature_um = projected_feature_mm * 1000.0
        pixels_across = projected_feature_um / pixel_um

        # Image distance
        image_distance = (f * wd) / (wd - f)

        svg = self._draw_svg(f, wd, beta, feature_mm, projected_feature_mm)

        return ExperimentResult(
            data={
                "focal_length_mm": f,
                "working_distance_mm": wd,
                "image_distance_mm": round(image_distance, 2),
                "magnification": round(beta, 4),
                "pixel_size_um": pixel_um,
                "pixel_precision_um": round(pixel_precision_um, 3),
                "object_feature_mm": feature_mm,
                "projected_feature_mm": round(projected_feature_mm, 4),
                "projected_feature_pixels": round(pixels_across, 2),
            },
            svg=svg,
            warnings=warnings,
            learning_hints=[
                "放大倍率为负表示成倒像；我们关注的是绝对值。",
                "像素精度越小，系统能分辨的物体细节越细。",
                "当特征投影不足 2 个像素时，检测算法通常无法稳定识别。",
            ],
        )

    def _draw_svg(
        self,
        f: float,
        wd: float,
        beta: float,
        feature_mm: float,
        projected_feature_mm: float,
    ) -> str:
        width, height = 640, 280
        lens_x = 120
        # Use image distance for scale layout
        v = (f * wd) / (wd - f)
        image_x = lens_x + min(250, max(60, v * 0.5))
        obj_x = lens_x - min(200, max(40, wd * 0.2))
        cy = height // 2

        # Scale object and image arrows to fit
        max_feature = max(feature_mm, abs(projected_feature_mm), 1.0)
        arrow_scale = min(80, 120 / max_feature)
        obj_h = feature_mm * arrow_scale
        img_h = abs(projected_feature_mm) * arrow_scale
        image_top = cy + img_h if beta < 0 else cy - img_h

        children = [
            # Optical axis
            line(obj_x - 30, cy, image_x + 40, cy, stroke="#94a3b8", dash="4"),
            # Lens
            line(lens_x, cy - 60, lens_x, cy + 60, stroke="#374151", stroke_width=4),
            text(lens_x, cy + 80, "透镜", fill="#64748b", font_size=11, anchor="middle"),
            # Object arrow
            arrow(obj_x, cy, obj_x, cy - obj_h, color="#2563eb", stroke_width=2),
            text(
                obj_x - 8,
                cy - obj_h - 6,
                f"{feature_mm} mm",
                fill="#2563eb",
                font_size=10,
                anchor="end",
            ),
            text(obj_x - 8, cy + 15, "物体", fill="#2563eb", font_size=11, anchor="end"),
            # Image arrow (inverted if beta < 0)
            arrow(image_x, cy, image_x, image_top, color="#dc2626", stroke_width=2),
            text(
                image_x + 8,
                cy - img_h - 6,
                f"{abs(projected_feature_mm):.3f} mm",
                fill="#dc2626",
                font_size=10,
            ),
            text(image_x + 8, cy + 15, "像", fill="#dc2626", font_size=11),
            # Chief ray lines
            line(
                obj_x, cy - obj_h, lens_x, cy - obj_h,
                stroke="#2563eb", opacity=0.4, stroke_width=1.5,
            ),
            line(
                lens_x, cy - obj_h, image_x, image_top,
                stroke="#2563eb", opacity=0.4, stroke_width=1.5,
            ),
            # Labels
            text(
                width / 2,
                height - 25,
                f"WD={wd:.1f} mm  f={f:.1f} mm  β={beta:.3f}",
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)
