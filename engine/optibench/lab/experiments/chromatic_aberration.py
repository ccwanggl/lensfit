"""Longitudinal chromatic aberration experiment."""

from __future__ import annotations

from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, line, svg_root, text


class ChromaticAberrationExperiment(OpticsExperiment):
    experiment_id = "chromatic-aberration"
    title = "轴向色差实验"
    description = "给定镜头焦距和阿贝数，观察不同波长（红/绿/蓝）焦点沿光轴的分离。"
    difficulty = "intermediate"
    prerequisites = ["thin-lens", "snell-refraction"]
    linked_concepts = [
        "chromatic-aberration",
        "abbe-number",
        "dispersion",
    ]
    linked_formulas = [
        "longitudinal-chromatic-aberration",
    ]
    learning_objectives = [
        "理解阿贝数越小（色散越大），轴向色差越严重。",
        "观察蓝光焦点更近、红光焦点更远的正常色散规律。",
    ]
    parameters = [
        Parameter(
            name="focal_length",
            label="标称焦距（绿光）",
            type="float",
            default=50.0,
            min=10.0,
            max=200.0,
            step=1.0,
            unit="mm",
        ),
        Parameter(
            name="abbe_number",
            label="阿贝数 V_d",
            type="float",
            default=60.0,
            min=20.0,
            max=100.0,
            step=1.0,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f = float(params.get("focal_length", 50.0))
        v = float(params.get("abbe_number", 60.0))

        # Longitudinal chromatic aberration: total focal spread ≈ f / V
        # Blue focuses shorter, red focuses longer than green.
        total_shift = f / v
        f_red = f + total_shift / 2
        f_green = f
        f_blue = f - total_shift / 2

        svg = self._draw_svg(f, f_red, f_green, f_blue)

        return ExperimentResult(
            data={
                "focal_length_mm": f,
                "abbe_number": v,
                "total_chromatic_shift_mm": round(total_shift, 4),
                "red_focus_mm": round(f_red, 4),
                "green_focus_mm": round(f_green, 4),
                "blue_focus_mm": round(f_blue, 4),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "阿贝数 > 70 的玻璃通常被称为低色散（ED）玻璃。",
                "消色差双合透镜通过两种玻璃组合把红光和蓝光拉到同一焦点。",
                "此模型为线性近似，真实玻璃的色散曲线是非线性的。",
            ],
        )

    def _draw_svg(
        self,
        f: float,
        f_red: float,
        f_green: float,
        f_blue: float,
    ) -> str:
        width, height = 640, 260
        lens_x = 80
        cy = height // 2

        # Scale so that max focus distance fits with margin
        max_focus = max(f_red, f_green, f_blue, 100.0)
        scale = (width - 160) / max_focus

        red_x = lens_x + f_red * scale
        green_x = lens_x + f_green * scale
        blue_x = lens_x + f_blue * scale

        v_display = f / (f_red - f_blue)
        shift = f_red - f_blue
        children = [
            # Optical axis
            line(lens_x - 20, cy, width - 20, cy, stroke="#94a3b8", dash="4"),
            # Lens
            line(lens_x, cy - 60, lens_x, cy + 60, stroke="#374151", stroke_width=4),
            text(lens_x, cy + 80, "透镜", fill="#64748b", font_size=11, anchor="middle"),
            # Incoming parallel rays for R/G/B
            line(lens_x - 100, cy - 40, lens_x, cy - 40, stroke="#dc2626", opacity=0.5),
            line(lens_x - 100, cy, lens_x, cy, stroke="#16a34a", opacity=0.5),
            line(lens_x - 100, cy + 40, lens_x, cy + 40, stroke="#2563eb", opacity=0.5),
            # Converging rays to focal points
            line(lens_x, cy - 40, red_x, cy, stroke="#dc2626", opacity=0.5),
            line(lens_x, cy, green_x, cy, stroke="#16a34a", opacity=0.5),
            line(lens_x, cy + 40, blue_x, cy, stroke="#2563eb", opacity=0.5),
            # Focal points
            circle(red_x, cy, 4, fill="#dc2626", stroke="none"),
            circle(green_x, cy, 4, fill="#16a34a", stroke="none"),
            circle(blue_x, cy, 4, fill="#2563eb", stroke="none"),
            # Labels
            text(
                red_x, cy + 25, f"红光 {f_red:.1f} mm",
                fill="#dc2626", font_size=10, anchor="middle",
            ),
            text(
                green_x, cy - 20, f"绿光 {f_green:.1f} mm",
                fill="#16a34a", font_size=10, anchor="middle",
            ),
            text(
                blue_x, cy + 25, f"蓝光 {f_blue:.1f} mm",
                fill="#2563eb", font_size=10, anchor="middle",
            ),
            # Summary
            text(
                width / 2,
                height - 25,
                (
                    f"标称焦距 {f:.1f} mm  |  "
                    f"阿贝数 {v_display:.1f}  |  "
                    f"轴向色差 {shift:.3f} mm"
                ),
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)
