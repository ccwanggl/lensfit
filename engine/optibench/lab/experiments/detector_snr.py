"""Detector SNR budget experiment (shot / read / dark noise)."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import line, rect, svg_root, text

# Physical constants (SI units).
_H = 6.62607015e-34
_C = 2.99792458e8


class DetectorSnrExperiment(OpticsExperiment):
    experiment_id = "detector-snr"
    title = "探测器信噪比预算实验"
    description = (
        "给定辐照度、像元尺寸与积分时间，计算信号电子数，"
        "并与散粒噪声、读出噪声、暗电流噪声对比，理解信噪比预算。"
    )
    difficulty = "intermediate"
    prerequisites = []
    linked_concepts = [
        "quantum-efficiency",
        "responsivity",
        "photodiode",
        "noise-equivalent-power",
        "动态范围",
        "读出噪声",
    ]
    linked_formulas = [
        "detector-snr",
        "NEP",
    ]
    learning_objectives = [
        "掌握信号电子数 N_s = η·Φ·λ·A·t / (h·c)。",
        "理解三种主要噪声来源：散粒噪声 √N_s、读出噪声 N_r、暗电流 √(I_d·t)。",
        "掌握信噪比 SNR = N_s / √(N_s + N_d + N_r²)，并认识散粒噪声极限。",
    ]
    parameters = [
        Parameter(
            name="wavelength_nm",
            label="波长",
            type="float",
            default=550.0,
            min=300.0,
            max=1600.0,
            step=10.0,
            unit="nm",
        ),
        Parameter(
            name="irradiance_w_m2",
            label="像面辐照度",
            type="float",
            default=0.01,
            min=0.0001,
            max=1.0,
            step=0.001,
            unit="W/m²",
        ),
        Parameter(
            name="pixel_pitch_um",
            label="像元间距",
            type="float",
            default=3.3,
            min=1.0,
            max=10.0,
            step=0.1,
            unit="µm",
        ),
        Parameter(
            name="integration_ms",
            label="积分时间",
            type="float",
            default=10.0,
            min=0.01,
            max=1000.0,
            step=0.01,
            unit="ms",
        ),
        Parameter(
            name="quantum_efficiency",
            label="量子效率 η",
            type="float",
            default=0.6,
            min=0.05,
            max=0.95,
            step=0.05,
        ),
        Parameter(
            name="read_noise_e",
            label="读出噪声",
            type="float",
            default=5.0,
            min=0.5,
            max=50.0,
            step=0.5,
            unit="e⁻",
        ),
        Parameter(
            name="dark_current_e_s",
            label="暗电流",
            type="float",
            default=50.0,
            min=0.0,
            max=5000.0,
            step=10.0,
            unit="e⁻/s",
        ),
        Parameter(
            name="full_well_e",
            label="满阱容量",
            type="float",
            default=20000.0,
            min=1000.0,
            max=100000.0,
            step=1000.0,
            unit="e⁻",
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        lam_m = float(params.get("wavelength_nm", 550.0)) * 1e-9
        irradiance = float(params.get("irradiance_w_m2", 0.01))
        pitch_m = float(params.get("pixel_pitch_um", 3.3)) * 1e-6
        t_s = float(params.get("integration_ms", 10.0)) * 1e-3
        qe = float(params.get("quantum_efficiency", 0.6))
        read_noise = float(params.get("read_noise_e", 5.0))
        dark_rate = float(params.get("dark_current_e_s", 50.0))
        full_well = float(params.get("full_well_e", 20000.0))

        area_m2 = pitch_m**2
        photon_flux_m2_s = irradiance * lam_m / (_H * _C)
        signal_e = qe * photon_flux_m2_s * area_m2 * t_s
        dark_e = dark_rate * t_s

        shot_noise = math.sqrt(signal_e)
        dark_noise = math.sqrt(dark_e)
        snr = signal_e / math.sqrt(signal_e + dark_e + read_noise**2)

        shot_limited = read_noise**2 + dark_e < 0.25 * signal_e
        dynamic_range = full_well / read_noise if read_noise > 0 else float("inf")
        sat_time_s = (
            full_well / (qe * photon_flux_m2_s * area_m2)
            if qe * photon_flux_m2_s * area_m2 > 0
            else float("inf")
        )

        svg = self._draw_svg(shot_noise, dark_noise, read_noise, snr, signal_e)

        return ExperimentResult(
            data={
                "signal_electrons": round(signal_e, 1),
                "shot_noise_e": round(shot_noise, 2),
                "dark_noise_e": round(dark_noise, 2),
                "read_noise_e": round(read_noise, 2),
                "snr": round(snr, 2),
                "snr_db": round(20 * math.log10(snr), 1) if snr > 0 else None,
                "shot_limited": shot_limited,
                "dynamic_range_bits": round(math.log2(dynamic_range), 2)
                if math.isfinite(dynamic_range)
                else None,
                "saturation_time_ms": round(sat_time_s * 1e3, 2),
                "signal_photons": round(photon_flux_m2_s * area_m2 * t_s, 1),
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "散粒噪声来自光子到达的泊松统计，无法消除，只能靠增加光子数压低相对值。",
                "当读出噪声与暗电流远小于散粒噪声时达到「散粒噪声极限」，此时 SNR ∝ √N_s。",
                "制冷降低暗电流；相关双采样压低读出噪声；两者都不影响散粒噪声。",
            ],
        )

    def _draw_svg(
        self,
        shot: float,
        dark: float,
        read: float,
        snr: float,
        signal: float,
    ) -> str:
        width, height = 640, 280
        bar_x = 150.0
        bar_max_w = 380.0
        log_min, log_max = 0.0, 4.0  # electrons on log10 scale: 1 .. 10^4

        def bar_w(value: float) -> float:
            if value <= 0:
                return 0.0
            frac = (math.log10(value) - log_min) / (log_max - log_min)
            return max(2.0, min(1.0, frac)) * bar_max_w

        bars = [
            ("散粒噪声 √Ns", shot, "#f59e0b"),
            ("暗电流噪声", dark, "#a855f7"),
            ("读出噪声 Nr", read, "#3b82f6"),
        ]

        children: list[str] = [
            text(24, 24, f"信号电子数 Ns = {signal:.0f} e⁻", fill="#0f172a", font_size=13),
        ]
        y = 52.0
        row_h = 40.0
        for idx, (label, value, color) in enumerate(bars):
            top = y + idx * row_h
            children.append(text(24, top + 14, label, fill="#475569", font_size=11))
            children.append(rect(bar_x, top, bar_max_w, 20, fill="#e2e8f0"))
            children.append(rect(bar_x, top, bar_w(value), 20, fill=color))
            children.append(
                text(
                    bar_x + bar_max_w + 12,
                    top + 14,
                    f"{value:.1f} e⁻",
                    fill="#475569",
                    font_size=11,
                )
            )
        # Log-scale ruler under bars.
        for i in range(5):
            x = bar_x + i / 4 * bar_max_w
            children.append(line(x, y + 3 * row_h - 4, x, y + 3 * row_h, stroke="#94a3b8"))
            children.append(
                text(x, y + 3 * row_h + 14, f"1e{i}", fill="#94a3b8", font_size=9, anchor="middle")
            )

        children.append(
            text(
                width / 2,
                height - 42,
                f"SNR = Ns / √(Ns + Nd + Nr²) = {snr:.1f}"
                + (f"  ({20 * math.log10(snr):.0f} dB)" if snr > 0 else ""),
                fill="#0f172a",
                font_size=13,
                anchor="middle",
            )
        )
        children.append(
            text(
                width / 2,
                height - 18,
                "虚线条带：散粒噪声极限参考（Nr 与 Nd 可忽略时的理论最优）",
                fill="#94a3b8",
                font_size=10,
                anchor="middle",
            )
        )
        children.append(
            line(bar_x, height - 60, bar_x + bar_max_w, height - 60, stroke="#22c55e", dash="4")
        )
        # Reference bar: pure shot-noise-limited noise for the same signal.
        ref = math.sqrt(signal)
        children.append(rect(bar_x, y - 8, bar_w(ref), 8, fill="#22c55e"))

        return svg_root(width, height, children)
