"""CIE 1931 chromaticity diagram with sRGB gamut mapping."""

from __future__ import annotations

import math
from typing import Any

from optibench.lab.base import ExperimentResult, OpticsExperiment, Parameter
from optibench.lab.renderer import circle, line, path, svg_root, text

# CIE 1931 spectral locus, coarse samples (wavelength_nm -> (x, y)).
_LOCUS: list[tuple[float, float, float]] = [
    (380.0, 0.1741, 0.0050),
    (400.0, 0.1733, 0.0048),
    (420.0, 0.1714, 0.0051),
    (440.0, 0.1644, 0.0109),
    (460.0, 0.1440, 0.0297),
    (480.0, 0.0913, 0.1327),
    (500.0, 0.0082, 0.5384),
    (510.0, 0.0139, 0.7502),
    (520.0, 0.0743, 0.8338),
    (530.0, 0.1547, 0.8059),
    (540.0, 0.2296, 0.7543),
    (550.0, 0.3016, 0.6923),
    (560.0, 0.3731, 0.6245),
    (570.0, 0.4441, 0.5547),
    (580.0, 0.5125, 0.4866),
    (590.0, 0.5752, 0.4242),
    (600.0, 0.6270, 0.3725),
    (620.0, 0.6915, 0.3083),
    (640.0, 0.7190, 0.2809),
    (660.0, 0.7300, 0.2700),
    (700.0, 0.7347, 0.2653),
]

_SRGB_PRIMARIES = {
    "r": (0.6400, 0.3300),
    "g": (0.3000, 0.6000),
    "b": (0.1500, 0.0600),
}
_WHITE_D65 = (0.3127, 0.3290)


def _srgb_to_xy(r8: int, g8: int, b8: int) -> tuple[float, float]:
    """Convert sRGB 8-bit triple to CIE xy chromaticity."""

    def lin(v: float) -> float:
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    rl, gl, bl = lin(r8), lin(g8), lin(b8)
    x = 0.4124 * rl + 0.3576 * gl + 0.1805 * bl
    y = 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
    z = 0.0193 * rl + 0.1192 * gl + 0.9505 * bl
    total = x + y + z
    if total <= 0:
        return _WHITE_D65
    return x / total, y / total


class ColorGamutExperiment(OpticsExperiment):
    experiment_id = "color-gamut"
    title = "CIE 色域映射实验"
    description = (
        "在 CIE 1931 色度图上观察光谱轨迹、sRGB 三角色域，"
        "并定位任意 RGB 颜色的色度坐标。"
    )
    difficulty = "foundation"
    prerequisites = ["color-mixing"]
    linked_concepts = [
        "color-gamut",
        "chromaticity-diagram",
    ]
    linked_formulas: list[str] = []
    learning_objectives = [
        "理解光谱轨迹：单色光的 xy 坐标连成的马蹄形边界。",
        "理解色域是显示器三原色在色度图上围成的三角形。",
        "掌握 RGB → XYZ → xy 的标准转换链路。",
    ]
    parameters = [
        Parameter(
            name="rgb_r",
            label="R 通道",
            type="float",
            default=255.0,
            min=0.0,
            max=255.0,
            step=5.0,
        ),
        Parameter(
            name="rgb_g",
            label="G 通道",
            type="float",
            default=120.0,
            min=0.0,
            max=255.0,
            step=5.0,
        ),
        Parameter(
            name="rgb_b",
            label="B 通道",
            type="float",
            default=60.0,
            min=0.0,
            max=255.0,
            step=5.0,
        ),
    ]

    def run(self, params: dict[str, Any]) -> ExperimentResult:
        r8 = int(float(params.get("rgb_r", 255)))
        g8 = int(float(params.get("rgb_g", 120)))
        b8 = int(float(params.get("rgb_b", 60)))

        cx, cy = _srgb_to_xy(r8, g8, b8)

        # Point-in-triangle via cross products (sRGB gamut triangle).
        pr, pg, pb = _SRGB_PRIMARIES["r"], _SRGB_PRIMARIES["g"], _SRGB_PRIMARIES["b"]

        def sign(ax, ay, bx, by, px_, py_):
            return (px_ - bx) * (ay - by) - (ax - bx) * (py_ - by)

        d1 = sign(pr[0], pr[1], pg[0], pg[1], cx, cy)
        d2 = sign(pg[0], pg[1], pb[0], pb[1], cx, cy)
        d3 = sign(pb[0], pb[1], pr[0], pr[1], cx, cy)
        eps = 1e-4  # 边界上的颜色（如 R-G 混合谱色）视为在色域内
        inside = d1 >= -eps and d2 >= -eps and d3 >= -eps

        svg = self._draw_svg(cx, cy, inside, (r8, g8, b8))

        return ExperimentResult(
            data={
                "rgb": [r8, g8, b8],
                "cie_x": round(cx, 4),
                "cie_y": round(cy, 4),
                "inside_srgb_gamut": inside,
                "dominant_note": "全部可由 sRGB 三原色混合得到" if inside
                else "超出 sRGB 色域——真实显示器无法准确重现该颜色",
            },
            svg=svg,
            warnings=[],
            learning_hints=[
                "光谱轨迹内部任何一点都是一种真实存在的颜色；轨迹直线段（紫线）不是单色光。",
                "三角形面积越小，显示器能重现的颜色越少——广色域屏幕即扩大此三角。",
                "饱和单色光大多落在 sRGB 三角之外，这是所有常规显示器的根本限制。",
            ],
        )

    def _draw_svg(self, cx_pt: float, cy_pt: float, inside: bool, rgb: tuple[int, int, int]) -> str:
        width, height = 620, 340
        ox, oy, span = 46.0, 36.0, 250.0

        def px(x: float, y: float) -> tuple[float, float]:
            return ox + x * span, oy + (0.8 - y) * span

        children: list[str] = [
            line(ox, oy + 0.8 * span, ox + 0.8 * span, oy + 0.8 * span, stroke="#cbd5e1"),
            line(ox, oy, ox, oy + 0.8 * span, stroke="#cbd5e1"),
        ]

        locus_pts = []
        for lam, lx, ly in _LOCUS:
            px_x, px_y = px(lx, ly)
            locus_pts.append(f"{px_x:.1f},{px_y:.1f}")
            if lam % 100 == 0 or lam in (490.0, 510.0, 550.0):
                children.append(
                    text(px_x, px_y - 5, f"{lam:.0f}", fill="#94a3b8", font_size=8, anchor="middle")
                )
        violet_start = px(_LOCUS[-1][1], _LOCUS[-1][2])
        violet_end = px(_LOCUS[0][1], _LOCUS[0][2])
        children.append(path("M" + " L".join(locus_pts), fill="none", stroke="#0f172a", stroke_width=1.5))
        children.append(line(violet_start[0], violet_start[1], violet_end[0], violet_end[1],
                             stroke="#8b5cf6", dash="4"))

        tri_pts = []
        for key in ("r", "g", "b"):
            tx, ty = px(*_SRGB_PRIMARIES[key])
            tri_pts.append(f"{tx:.1f},{ty:.1f}")
        children.append(
            path("M" + " L".join(tri_pts) + " Z", fill="rgba(59,130,246,0.08)",
                 stroke="#3b82f6", stroke_width=1.5)
        )
        for key, color in (("r", "#dc2626"), ("g", "#16a34a"), ("b", "#2563eb")):
            tx, ty = px(*_SRGB_PRIMARIES[key])
            children.append(circle(tx, ty, 3, fill=color))
        wx, wy = px(*_WHITE_D65)
        children.append(circle(wx, wy, 3, fill="#334155"))
        children.append(text(wx + 5, wy + 3, "D65", fill="#334155", font_size=9))

        mx, my = px(cx_pt, cy_pt)
        marker_color = "#16a34a" if inside else "#dc2626"
        children.append(circle(mx, my, 4, fill=marker_color))
        swatch = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
        children.append(circle(ox + 0.72 * span + 26, oy + 24, 14, fill=swatch, stroke="#475569"))
        children.append(
            text(ox + 0.72 * span + 26, oy + 56, f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                 fill="#475569", font_size=10, anchor="middle")
        )
        verdict_color = "#16a34a" if inside else "#dc2626"
        children.append(
            text(ox + 0.72 * span + 26, oy + 74,
                 "sRGB 内" if inside else "sRGB 外", fill=verdict_color,
                 font_size=11, anchor="middle")
        )
        children.append(
            text(width / 2, height - 14,
                 f"xy = ({cx_pt:.3f}, {cy_pt:.3f})",
                 fill="#475569", font_size=11, anchor="middle")
        )
        return svg_root(width, height, children)
