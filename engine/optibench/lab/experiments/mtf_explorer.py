"""MTF/OTF explorer experiment."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, path, svg_root, text


class MtfExplorerExperiment(OpticsExperiment):
    experiment_id = "mtf-explorer"
    title = "MTF/OTF 探索实验"
    description = "合成衍射极限 MTF、离焦模糊 MTF 与总 MTF，并观察对应的 PSF。"
    difficulty = "intermediate"
    prerequisites = ["nyquist-sampling", "diffraction"]
    linked_concepts = [
        "10-concepts/mtf",
        "10-concepts/otf",
        "10-concepts/psf",
        "10-concepts/调制传递函数",
        "10-concepts/光学传递函数",
        "10-concepts/点扩散函数",
    ]
    linked_formulas = [
        "20-formulas/airy-disk-diameter",
    ]
    learning_objectives = [
        "理解衍射极限给出了光学系统的最高空间频率截止。",
        "观察离焦如何在中低频先衰减 MTF。",
        "认识 MTF 与 PSF 是同一系统在不同域的描述。",
    ]
    parameters = [
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
        Parameter(
            name="f_number",
            label="光圈 F 数",
            type="float",
            default=4.0,
            min=1.4,
            max=22.0,
            step=0.1,
            unit="F",
        ),
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
            name="focus_distance_mm",
            label="对焦距离",
            type="float",
            default=1000.0,
            min=100.0,
            max=10000.0,
            step=50.0,
            unit="mm",
        ),
        Parameter(
            name="defocus_distance_mm",
            label="实际物距",
            type="float",
            default=1000.0,
            min=100.0,
            max=10000.0,
            step=50.0,
            unit="mm",
        ),
        Parameter(
            name="pixel_size_um",
            label="像元尺寸",
            type="float",
            default=3.45,
            min=1.0,
            max=20.0,
            step=0.1,
            unit="μm",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        f_mm = float(params.get("focal_length_mm", 50.0))
        n = float(params.get("f_number", 4.0))
        lambda_nm = float(params.get("wavelength_nm", 550.0))
        u_focus = float(params.get("focus_distance_mm", 1000.0))
        u_actual = float(params.get("defocus_distance_mm", 1000.0))
        pixel_um = float(params.get("pixel_size_um", 3.45))

        lambda_mm = lambda_nm * 1e-6

        # Image distances for focused and defocused object distances.
        v_focus = 1.0 / (1.0 / f_mm - 1.0 / u_focus)
        v_actual = 1.0 / (1.0 / f_mm - 1.0 / u_actual)
        # Geometric circle of confusion diameter on the sensor (mm).
        coc_mm = n * abs(v_actual - v_focus) / max(v_actual, 1e-9)

        # Diffraction-limited cutoff spatial frequency (cycles/mm).
        cutoff_lp_mm = 1.0 / (lambda_mm * n)

        # Build frequency grid up to slightly above cutoff.
        num_freq = 512
        f_max = max(cutoff_lp_mm * 1.05, 50.0)
        freqs = np.linspace(0.0, f_max, num_freq)

        # Diffraction-limited MTF for a circular aperture.
        rho = freqs / cutoff_lp_mm
        rho = np.clip(rho, 0.0, 1.0)
        mtf_diff = np.where(
            freqs < cutoff_lp_mm,
            (2.0 / math.pi) * (np.arccos(rho) - rho * np.sqrt(1.0 - rho**2)),
            0.0,
        )
        mtf_diff = np.where(freqs == 0.0, 1.0, mtf_diff)

        # Defocus MTF: Gaussian approximation from geometric CoC.
        # sigma of a uniform-disk PSF ~= COC / (2 * sqrt(2)).
        sigma_mm = coc_mm / (2.0 * math.sqrt(2.0)) if coc_mm > 0 else 1e-9
        mtf_defocus = np.exp(-2.0 * (np.pi * sigma_mm * freqs) ** 2)

        # Combined MTF (cascaded linear systems).
        mtf_total = mtf_diff * mtf_defocus

        # MTF50 by linear interpolation.
        mtf50 = self._find_mtf50(freqs, mtf_total)

        # PSF via inverse FFT of the real, even OTF = MTF.
        psf_x_um, psf_profile = self._compute_psf(freqs, mtf_total)

        # Sensor Nyquist frequency (lp/mm).
        sensor_nyquist_lp_mm = 1.0 / (2.0 * pixel_um / 1000.0)

        # Airy disk radius for reference.
        airy_radius_um = 1.22 * lambda_mm * n * 1000.0

        svg = self._draw_svg(
            freqs,
            mtf_diff,
            mtf_defocus,
            mtf_total,
            psf_x_um,
            psf_profile,
            cutoff_lp_mm,
            mtf50,
            sensor_nyquist_lp_mm,
        )

        return ExperimentResult(
            data={
                "focal_length_mm": f_mm,
                "f_number": n,
                "wavelength_nm": lambda_nm,
                "focus_distance_mm": u_focus,
                "defocus_distance_mm": u_actual,
                "circle_of_confusion_um": round(coc_mm * 1000.0, 2),
                "diffraction_cutoff_lp_mm": round(cutoff_lp_mm, 2),
                "mtf50_lp_mm": round(mtf50, 2) if mtf50 else None,
                "sensor_nyquist_lp_mm": round(sensor_nyquist_lp_mm, 2),
                "airy_radius_um": round(airy_radius_um, 2),
                "frequencies_lp_mm": freqs.tolist(),
                "mtf_diffraction": mtf_diff.tolist(),
                "mtf_defocus": mtf_defocus.tolist(),
                "mtf_total": mtf_total.tolist(),
                "psf_x_um": psf_x_um.tolist(),
                "psf_profile": psf_profile.tolist(),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "衍射极限 MTF 的截止频率 f_c = 1 / (λ F#)。",
                "离焦会首先衰减中低频 MTF，使图像整体发虚。",
                "MTF 是 OTF 的模；对实偶 OTF 做逆傅里叶变换可得到 PSF。",
                "传感器奈奎斯特频率是系统能记录的最高频率，超过它的镜头细节会被混叠。",
            ],
        )

    @staticmethod
    def _find_mtf50(freqs: np.ndarray, mtf: np.ndarray) -> float | None:
        """Return the spatial frequency where MTF crosses 0.5."""
        above = np.where(mtf >= 0.5)[0]
        if len(above) == 0 or above[-1] == len(freqs) - 1:
            return None
        i = above[-1]
        # Linear interpolation between (freqs[i], mtf[i]) and (freqs[i+1], mtf[i+1]).
        f0, f1 = freqs[i], freqs[i + 1]
        m0, m1 = mtf[i], mtf[i + 1]
        if m0 == m1:
            return float(f0)
        return float(f0 + (0.5 - m0) * (f1 - f0) / (m1 - m0))

    @staticmethod
    def _compute_psf(freqs: np.ndarray, mtf: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Compute radial PSF from a real, even MTF using the inverse FFT.

        The frequency grid is assumed to start at 0 and be evenly spaced.
        We mirror MTF to negative frequencies, take the real inverse FFT,
        and return a centered, normalized 1-D radial profile.
        """
        # Spatial sampling: dx = 1 / (2 * f_max) for a grid from -f_max to f_max.
        f_max = float(freqs[-1])
        dx_mm = 1.0 / (2.0 * f_max)

        # Build symmetric OTF on a uniform grid.
        mtf_pos = np.asarray(mtf, dtype=np.float64)
        otf = np.concatenate([mtf_pos[::-1], mtf_pos[1:]])
        psf_complex = np.fft.ifft(np.fft.ifftshift(otf))
        psf = np.real(psf_complex)
        psf = np.fft.fftshift(psf)
        psf = np.maximum(psf, 0.0)

        n = len(psf)
        x_mm = (np.arange(n) - n // 2) * dx_mm
        x_um = x_mm * 1000.0

        # Normalize peak to 1.
        max_val = np.max(psf)
        if max_val > 0:
            psf = psf / max_val
        return x_um, psf

    def _draw_svg(
        self,
        freqs: np.ndarray,
        mtf_diff: np.ndarray,
        mtf_defocus: np.ndarray,
        mtf_total: np.ndarray,
        psf_x_um: np.ndarray,
        psf_profile: np.ndarray,
        cutoff_lp_mm: float,
        mtf50: float | None,
        sensor_nyquist_lp_mm: float,
    ) -> str:
        width, height = 720, 360
        plot_w, plot_h = 320, 240
        margin_left, margin_top = 50, 40

        # Left plot: MTF curves.
        px = margin_left
        py = margin_top
        x_max = max(cutoff_lp_mm * 1.05, sensor_nyquist_lp_mm * 1.05, 50.0)

        def tx(f: float) -> float:
            return px + (f / x_max) * plot_w

        def ty(m: float) -> float:
            return py + plot_h - m * plot_h

        mtf_diff_pts = " ".join(f"{tx(f)},{ty(m)}" for f, m in zip(freqs, mtf_diff))
        mtf_def_pts = " ".join(f"{tx(f)},{ty(m)}" for f, m in zip(freqs, mtf_defocus))
        mtf_total_pts = " ".join(f"{tx(f)},{ty(m)}" for f, m in zip(freqs, mtf_total))

        children = [
            # Axes for MTF plot.
            self._axis(px, py, plot_w, plot_h, x_max),
            path(mtf_diff_pts, stroke="#94a3b8", fill="none", stroke_width=1.5),
            path(mtf_def_pts, stroke="#f59e0b", fill="none", stroke_width=1.5),
            path(mtf_total_pts, stroke="#22c55e", fill="none", stroke_width=2.5),
            text(px + plot_w - 10, py + 15, "衍射", fill="#94a3b8", font_size=10, anchor="end"),
            text(px + plot_w - 10, py + 30, "离焦", fill="#f59e0b", font_size=10, anchor="end"),
            text(px + plot_w - 10, py + 45, "总 MTF", fill="#22c55e", font_size=10, anchor="end"),
            text(
                px + plot_w // 2,
                py + plot_h + 30,
                "空间频率 (lp/mm)",
                fill="#64748b",
                font_size=11,
                anchor="middle",
            ),
            text(px - 30, py - 10, "MTF", fill="#64748b", font_size=11, anchor="middle"),
        ]

        # MTF50 and cutoff markers.
        if mtf50:
            children.extend(
                [
                    line(
                        tx(mtf50),
                        py,
                        tx(mtf50),
                        py + plot_h,
                        stroke="#22c55e",
                        dash="4",
                        stroke_width=1,
                    ),
                    text(
                        tx(mtf50),
                        py + plot_h - 5,
                        f"MTF50={mtf50:.1f}",
                        fill="#22c55e",
                        font_size=9,
                        anchor="middle",
                    ),
                ]
            )
        children.extend(
            [
                line(
                    tx(cutoff_lp_mm),
                    py,
                    tx(cutoff_lp_mm),
                    py + plot_h,
                    stroke="#94a3b8",
                    dash="4",
                    stroke_width=1,
                ),
                text(
                    tx(cutoff_lp_mm),
                    py + 10,
                    f"f_c={cutoff_lp_mm:.1f}",
                    fill="#94a3b8",
                    font_size=9,
                    anchor="middle",
                ),
            ]
        )

        # Right plot: PSF.
        psf_px = px + plot_w + 80
        psf_py = py
        x_min_um = float(np.min(psf_x_um))
        x_max_um = float(np.max(psf_x_um))
        psf_x_scale = plot_w / (x_max_um - x_min_um)
        psf_y_scale = plot_h / max(float(np.max(psf_profile)), 1e-6)
        psf_pts = " ".join(
            f"{psf_px + (x - x_min_um) * psf_x_scale},{psf_py + plot_h - y * psf_y_scale}"
            for x, y in zip(psf_x_um, psf_profile)
        )

        children.extend(
            [
                self._axis(psf_px, psf_py, plot_w, plot_h, x_max_um - x_min_um),
                path(psf_pts, stroke="#38bdf8", fill="none", stroke_width=2),
                text(
                    psf_px + plot_w // 2,
                    psf_py + plot_h + 30,
                    "像面位置 (μm)",
                    fill="#64748b",
                    font_size=11,
                    anchor="middle",
                ),
                text(
                    psf_px - 30, psf_py - 10, "PSF", fill="#64748b", font_size=11, anchor="middle"
                ),
            ]
        )

        return svg_root(width, height, children)

    def _axis(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        x_range: float,
    ) -> str:
        parts = [
            line(x, y + h, x + w, y + h, stroke="#475569", stroke_width=1),
            line(x, y, x, y + h, stroke="#475569", stroke_width=1),
        ]
        # A few tick marks on x axis.
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            tx = x + frac * w
            parts.append(line(tx, y + h, tx, y + h + 4, stroke="#475569", stroke_width=1))
            parts.append(
                text(
                    tx,
                    y + h + 16,
                    f"{frac * x_range:.1f}",
                    fill="#64748b",
                    font_size=9,
                    anchor="middle",
                )
            )
        # Y ticks.
        for frac in [0.0, 0.5, 1.0]:
            ty = y + h - frac * h
            parts.append(line(x, ty, x - 4, ty, stroke="#475569", stroke_width=1))
            parts.append(
                text(x - 8, ty + 3, f"{frac:.1f}", fill="#64748b", font_size=9, anchor="end")
            )
        return "".join(parts)
