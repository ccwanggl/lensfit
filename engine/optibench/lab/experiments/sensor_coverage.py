"""Sensor image-circle coverage experiment."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import axis_x, axis_y, circle, polygon, rect, svg_root, text
from optibench.visualization.coverage import CoveragePlotData


class SensorCoverageExperiment(OpticsExperiment):
    experiment_id = "sensor-coverage"
    title = "像圈与传感器覆盖实验"
    description = "调整传感器尺寸和镜头像圈，观察覆盖率与渐晕区域。"
    difficulty = "foundation"
    linked_concepts = [
        "image-circle",
        "渐晕",
    ]
    linked_formulas = [
        "coverage-ratio",
    ]
    learning_objectives = [
        "理解像圈直径必须大于传感器对角线才能无渐晕。",
        "观察四角超出像圈时出现的渐晕区域。",
    ]
    parameters = [
        Parameter(
            name="sensor_w_mm",
            label="传感器宽度",
            type="float",
            default=12.8,
            min=1.0,
            max=50.0,
            step=0.1,
            unit="mm",
        ),
        Parameter(
            name="sensor_h_mm",
            label="传感器高度",
            type="float",
            default=9.6,
            min=1.0,
            max=50.0,
            step=0.1,
            unit="mm",
        ),
        Parameter(
            name="image_circle_mm",
            label="像圈直径",
            type="float",
            default=16.0,
            min=1.0,
            max=80.0,
            step=0.5,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        sensor_w = float(params.get("sensor_w_mm", 12.8))
        sensor_h = float(params.get("sensor_h_mm", 9.6))
        image_circle = float(params.get("image_circle_mm", 16.0))

        coverage = CoveragePlotData(sensor_w, sensor_h, image_circle).generate()

        svg = self._draw_svg(coverage, sensor_w, sensor_h, image_circle)

        warnings: list[str] = []
        if coverage["coverage_ratio"] < 1.0:
            warnings.append(
                f"传感器对角线 ({(sensor_w**2 + sensor_h**2)**0.5:.2f} mm) 超过像圈直径，"
                f"四角将出现渐晕（覆盖率 {coverage['coverage_ratio']:.1%}）。"
            )

        return ExperimentResult(
            data=coverage,
            svg=svg,
            warnings=warnings,
            learning_hints=[
                "当像圈直径 ≥ 传感器对角线时，整幅画面亮度均匀。",
                "工业视觉选型中通常要求像圈比传感器对角线大 10% 以上，以保留余量。",
            ],
        )

    def _draw_svg(
        self, coverage: dict[str, Any], sensor_w: float, sensor_h: float, image_circle: float
    ) -> str:
        width, height = 500, 400
        # Compute scale so that max(sensor_diag, image_circle) fits with margin
        max_dim = max(sensor_w, sensor_h, image_circle)
        margin = 60
        scale = min((width - 2 * margin) / max_dim, (height - 2 * margin) / max_dim)
        cx, cy = width // 2, height // 2

        r = (image_circle / 2) * scale
        hw = (sensor_w / 2) * scale
        hh = (sensor_h / 2) * scale

        children = [
            # Image circle
            circle(cx, cy, r, fill="#e2e8f0", stroke="#64748b", stroke_width=2),
            text(cx + r - 10, cy - r - 8, "像圈", fill="#64748b", font_size=11, anchor="middle"),
            # Sensor rectangle
            rect(
                cx - hw,
                cy - hh,
                hw * 2,
                hh * 2,
                fill="rgba(99,102,241,0.15)",
                stroke="#4f46e5",
                stroke_width=2,
            ),
            text(cx + hw + 8, cy - hh, "传感器", fill="#4f46e5", font_size=11),
            # Vignetting regions
            *self._vignette_polygons(coverage, cx, cy, scale),
            # Center cross
            f'<line x1="{cx-4}" y1="{cy}" x2="{cx+4}" y2="{cy}" stroke="#94a3b8"/>',
            f'<line x1="{cx}" y1="{cy-4}" x2="{cx}" y2="{cy+4}" stroke="#94a3b8"/>',
            # Stats
            text(
                width / 2,
                height - 30,
                (
                    f"传感器 {sensor_w:.1f}×{sensor_h:.1f} mm  |  "
                    f"像圈 ∅{image_circle:.1f} mm  |  "
                    f"覆盖率 {coverage['coverage_ratio']:.1%}"
                ),
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        # Axes for scale reference
        children.extend(axis_x(margin, height - 50, width - 2 * margin, label="mm (按中心对齐)"))
        children.extend(axis_y(margin, height - 50, height - 2 * margin))

        return svg_root(width, height, children)

    def _vignette_polygons(
        self, coverage: dict[str, Any], cx: float, cy: float, scale: float
    ) -> list[str]:
        regions = coverage.get("vignetting_regions", [])
        if not regions:
            return []
        elements = []
        for region in regions:
            pts = [(p["x"] * scale + cx, p["y"] * scale + cy) for p in region["points"]]
            elements.append(polygon(pts, fill="rgba(220,38,38,0.25)", stroke="#dc2626"))
        return elements
