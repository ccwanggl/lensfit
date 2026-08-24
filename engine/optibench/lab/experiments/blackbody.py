"""Blackbody radiation and color temperature experiment."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import path, polygon, svg_root, text

# Physical constants (SI units).
_H = 6.62607015e-34  # Planck constant, J·s
_C = 2.99792458e8  # Speed of light, m/s
_K_B = 1.380649e-23  # Boltzmann constant, J/K
_WIEN_B_M_K = 2.897771955e-3  # Wien displacement constant, m·K


class BlackbodyExperiment(OpticsExperiment):
    experiment_id = "blackbody"
    title = "黑体辐射与色温实验"
    description = "改变黑体温度，观察光谱辐射分布、峰值波长和感知颜色如何变化。"
    difficulty = "intermediate"
    prerequisites = ["color-mixing"]
    linked_concepts = [
        "10-concepts/color-temperature",
        "10-concepts/色温",
        "10-concepts/spectral-power-distribution",
    ]
    linked_formulas = [
        "20-formulas/planck-blackbody",
    ]
    learning_objectives = [
        "掌握普朗克黑体辐射定律 B(λ, T)。",
        "理解维恩位移定律 λ_max = b / T。",
        "观察色温从低到高时颜色由红橙向蓝白变化。",
    ]
    parameters = [
        Parameter(
            name="temperature_k",
            label="黑体温度",
            type="float",
            default=5500.0,
            min=1000.0,
            max=10000.0,
            step=100.0,
            unit="K",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        t_k = float(params.get("temperature_k", 5500.0))

        # Sample spectrum over a range that captures the visible peak for
        # temperatures up to 10,000 K.
        lambda_min_nm = 300.0
        lambda_max_nm = 1000.0
        num_samples = 256
        lambdas_nm = [
            lambda_min_nm + i * (lambda_max_nm - lambda_min_nm) / (num_samples - 1)
            for i in range(num_samples)
        ]

        radiance = [self._planck_radiance(lam_nm, t_k) for lam_nm in lambdas_nm]
        max_radiance = max(radiance)
        normalized = [r / max_radiance for r in radiance]

        peak_nm = _WIEN_B_M_K / t_k * 1e9

        # Approximate perceived RGB by weighting the heuristic per-wavelength RGB
        # with the radiance at each sample.
        rgb = self._spectrum_to_rgb(lambdas_nm, radiance)

        svg = self._draw_svg(
            t_k, lambdas_nm, normalized, peak_nm, rgb, lambda_min_nm, lambda_max_nm
        )

        return ExperimentResult(
            data={
                "temperature_k": t_k,
                "peak_wavelength_nm": round(peak_nm, 1),
                "radiance": radiance,
                "normalized_radiance": normalized,
                "wavelengths_nm": lambdas_nm,
                "perceived_rgb": rgb,
                "perceived_hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "温度越高，峰值波长越短（维恩位移定律）。",
                "总辐射功率随 T⁴ 增长（斯特藩-玻尔兹曼定律），这里只显示相对光谱。",
                "感知的 RGB 是粗略近似，未经过 CIE 标准色度学精确计算。",
            ],
        )

    @staticmethod
    def _planck_radiance(lambda_nm: float, t_k: float) -> float:
        """Return Planck spectral radiance B(λ, T) in arbitrary relative units."""
        lam_m = lambda_nm * 1e-9
        # B(λ,T) ∝ λ⁻⁵ / (exp(hc / λkT) - 1)
        exponent = (_H * _C) / (lam_m * _K_B * t_k)
        if exponent > 700:
            return 0.0
        return 1.0 / (lam_m**5 * (math.exp(exponent) - 1.0))

    @staticmethod
    def _spectrum_to_rgb(lambdas_nm: list[float], radiance: list[float]) -> tuple[int, int, int]:
        """Map a sampled SPD to an approximate sRGB triple."""
        total = sum(radiance)
        if total <= 0:
            return 0, 0, 0

        r_acc = g_acc = b_acc = 0.0
        for lam_nm, rad in zip(lambdas_nm, radiance):
            r, g, b = _wavelength_to_rgb(lam_nm)
            weight = rad / total
            r_acc += r * weight
            g_acc += g * weight
            b_acc += b * weight

        # Apply a simple gamma-like compression so the displayed color stays
        # within a reasonable range.
        def compress(v: float) -> int:
            v = max(0.0, min(255.0, v))
            return int(255.0 * (v / 255.0) ** 0.8)

        return compress(r_acc), compress(g_acc), compress(b_acc)

    def _draw_svg(
        self,
        t_k: float,
        lambdas_nm: list[float],
        normalized: list[float],
        peak_nm: float,
        rgb: tuple[int, int, int],
        lambda_min_nm: float,
        lambda_max_nm: float,
    ) -> str:
        width, height = 640, 320
        plot_x, plot_y = 50, 40
        plot_w, plot_h = 420, 180

        def x_to_px(lam_nm: float) -> float:
            return plot_x + (lam_nm - lambda_min_nm) / (lambda_max_nm - lambda_min_nm) * plot_w

        def y_to_px(norm: float) -> float:
            return plot_y + plot_h - norm * plot_h

        # Spectrum curve path.
        pts = " ".join(
            f"{x_to_px(lam):.1f},{y_to_px(norm):.1f}" for lam, norm in zip(lambdas_nm, normalized)
        )

        color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

        children = [
            # Axes.
            f'<line x1="{plot_x:.1f}" y1="{plot_y + plot_h:.1f}" '
            f'x2="{plot_x + plot_w:.1f}" y2="{plot_y + plot_h:.1f}" stroke="#475569"/>',
            f'<line x1="{plot_x:.1f}" y1="{plot_y:.1f}" '
            f'x2="{plot_x:.1f}" y2="{plot_y + plot_h:.1f}" stroke="#475569"/>',
            path(pts, fill="none", stroke="#f59e0b", stroke_width=2),
            # Peak marker.
            f'<line x1="{x_to_px(peak_nm):.1f}" y1="{plot_y:.1f}" '
            f'x2="{x_to_px(peak_nm):.1f}" y2="{plot_y + plot_h:.1f}" '
            f'stroke="#22c55e" stroke-dasharray="4"/>',
            text(
                x_to_px(peak_nm),
                plot_y + 20,
                f"峰值 {peak_nm:.0f} nm",
                fill="#22c55e",
                font_size=10,
                anchor="middle",
            ),
            # Axis labels.
            text(
                plot_x + plot_w / 2,
                plot_y + plot_h + 30,
                "波长 (nm)",
                fill="#64748b",
                font_size=11,
                anchor="middle",
            ),
            text(
                plot_x - 30,
                plot_y + plot_h / 2,
                "相对辐射",
                fill="#64748b",
                font_size=11,
                anchor="middle",
            ),
            # Color swatch.
            polygon(
                [
                    (plot_x + plot_w + 30, plot_y),
                    (plot_x + plot_w + 130, plot_y),
                    (plot_x + plot_w + 130, plot_y + 80),
                    (plot_x + plot_w + 30, plot_y + 80),
                ],
                fill=color,
                stroke="#475569",
            ),
            text(
                plot_x + plot_w + 80,
                plot_y + 100,
                f"{t_k:.0f} K",
                fill="#475569",
                font_size=12,
                anchor="middle",
            ),
            text(
                plot_x + plot_w + 80,
                plot_y + 120,
                f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                fill="#64748b",
                font_size=10,
                anchor="middle",
            ),
        ]

        return svg_root(width, height, children)


def _wavelength_to_rgb(wavelength_nm: float) -> tuple[int, int, int]:
    """Heuristic wavelength to RGB mapping."""
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
