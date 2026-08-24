"""Airy disk diffraction experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, svg_root, text


class DiffractionExperiment(OpticsExperiment):
    experiment_id = "diffraction"
    title = "圆孔衍射与艾里斑"
    description = "改变波长和光圈孔径，观察艾里斑大小和衍射图样的变化。"
    difficulty = "intermediate"
    linked_concepts = [
        "10-concepts/airy-disk",
        "10-concepts/衍射极限",
        "20-formulas/rayleigh-criterion",
        "10-concepts/艾里斑",
    ]
    learning_objectives = [
        "理解艾里斑是理想光学系统的极限点扩散函数。",
        "观察光圈越小、波长越长，艾里斑越大。",
    ]
    parameters = [
        Parameter(
            name="wavelength_nm",
            label="波长",
            type="float",
            default=550.0,
            min=380.0,
            max=700.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="aperture_mm",
            label="通光孔径",
            type="float",
            default=10.0,
            min=1.0,
            max=50.0,
            step=0.5,
            unit="mm",
        ),
        Parameter(
            name="focal_length_mm",
            label="焦距",
            type="float",
            default=50.0,
            min=10.0,
            max=200.0,
            step=1.0,
            unit="mm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        wavelength_nm = float(params.get("wavelength_nm", 550.0))
        aperture_mm = float(params.get("aperture_mm", 10.0))
        focal_mm = float(params.get("focal_length_mm", 50.0))

        wavelength_mm = wavelength_nm * 1e-6
        f_number = focal_mm / aperture_mm
        airy_radius_mm = 1.22 * wavelength_mm * f_number
        airy_diameter_um = airy_radius_mm * 2 * 1000

        svg = self._draw_svg(wavelength_nm, aperture_mm, focal_mm, airy_diameter_um)

        return ExperimentResult(
            data={
                "wavelength_nm": wavelength_nm,
                "aperture_mm": aperture_mm,
                "focal_length_mm": focal_mm,
                "f_number": round(f_number, 2),
                "airy_radius_mm": round(airy_radius_mm, 4),
                "airy_diameter_um": round(airy_diameter_um, 2),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "艾里斑直径 ≈ 2.44 λ F#，是衍射极限分辨率。",
                "缩小光圈（F# 变大）会让艾里斑变大，从而降低分辨率。",
            ],
        )

    def _draw_svg(
        self,
        wavelength_nm: float,
        aperture_mm: float,
        focal_mm: float,
        airy_diameter_um: float,
    ) -> str:
        width, height = 400, 400
        cx, cy = width // 2, height // 2
        max_radius = 140

        # Scale so first dark ring fits within max_radius
        first_zero_um = airy_diameter_um / 2
        scale = max_radius / max(first_zero_um, 5.0)
        first_zero_px = first_zero_um * scale

        r, g, b = self._wavelength_to_rgb(wavelength_nm)

        children = []
        # Approximate Airy pattern with concentric translucent rings
        for i in range(80, 0, -1):
            frac = i / 80.0
            radius_px = first_zero_px * math.sqrt(frac) * 1.8
            if radius_px > max_radius:
                continue
            # Approx intensity: (2 J1(x)/x)^2 mapped to a cos falloff
            intensity = max(0.05, math.cos(frac * math.pi / 2) ** 2)
            fill = f"rgba({r},{g},{b},{intensity:.2f})"
            children.append(circle(cx, cy, radius_px, fill=fill, stroke="none"))

        f_num = focal_mm / aperture_mm
        label = (
            f"λ={wavelength_nm:.0f} nm  D={aperture_mm:.1f} mm  "
            f"f/{f_num:.1f}  第一暗环={first_zero_um:.1f} μm"
        )
        children.extend([
            circle(cx, cy, first_zero_px, fill="none", stroke="white", dash="4"),
            text(cx, height - 35, label, fill="#e2e8f0", font_size=11, anchor="middle"),
        ])

        return svg_root(width, height, children, bg="#0f172a", dark_bg="#0f172a")

    @staticmethod
    def _wavelength_to_rgb(wavelength_nm: float) -> tuple[int, int, int]:
        w = wavelength_nm
        if w < 440:
            r = int((440 - w) / (440 - 380) * 255)
            g = 0
            b = 255
        elif w < 490:
            r = 0
            g = int((w - 440) / (490 - 440) * 255)
            b = 255
        elif w < 510:
            r = 0
            g = 255
            b = int((510 - w) / (510 - 490) * 255)
        elif w < 580:
            r = int((w - 510) / (580 - 510) * 255)
            g = 255
            b = 0
        elif w < 645:
            r = 255
            g = int((645 - w) / (645 - 580) * 255)
            b = 0
        else:
            r = 255
            g = 0
            b = int((w - 645) / (700 - 645) * 255)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
