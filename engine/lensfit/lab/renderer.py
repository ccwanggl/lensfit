"""Lightweight SVG rendering helpers for optics experiments.

These helpers avoid a matplotlib dependency in the engine sidecar.
"""

from __future__ import annotations

from typing import Any


def svg_root(
    width: int,
    height: int,
    children: list[str],
    bg: str = "#f8fafc",
    dark_bg: str = "#0f172a",
) -> str:
    """Wrap children in a self-contained SVG with a CSS-variable-aware background."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" class="lab-svg">\n'
        f'  <rect width="{width}" height="{height}" fill="{bg}" class="lab-svg-bg"/>\n'
        + "\n".join(f"  {child}" for child in children)
        + "\n</svg>"
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str = "#94a3b8",
    stroke_width: float = 1,
    dash: str | None = None,
    opacity: float = 1.0,
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr} opacity="{opacity}"/>'
    )


def circle(
    cx: float,
    cy: float,
    r: float,
    fill: str = "none",
    stroke: str = "#94a3b8",
    stroke_width: float = 1,
    opacity: float = 1.0,
    dash: str | None = None,
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" opacity="{opacity}"{dash_attr}/>'
    )


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = "none",
    stroke: str = "#94a3b8",
    stroke_width: float = 1,
    opacity: float = 1.0,
) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" opacity="{opacity}"/>'
    )


def arrow(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = "#2563eb",
    stroke_width: float = 2,
    head_size: float = 6,
) -> str:
    """Draw a line with an arrowhead at (x2, y2)."""
    import math

    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    hx1 = x2 - head_size * math.cos(angle - math.pi / 6)
    hy1 = y2 - head_size * math.sin(angle - math.pi / 6)
    hx2 = x2 - head_size * math.cos(angle + math.pi / 6)
    hy2 = y2 - head_size * math.sin(angle + math.pi / 6)
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{stroke_width}"/>\n'
        f'<polygon points="{x2:.1f},{y2:.1f} {hx1:.1f},{hy1:.1f} {hx2:.1f},{hy2:.1f}" '
        f'fill="{color}"/>'
    )


def text(
    x: float,
    y: float,
    content: str,
    fill: str = "#475569",
    font_size: int = 11,
    anchor: str = "start",
    class_name: str | None = None,
) -> str:
    cls = f' class="{class_name}"' if class_name else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{font_size}" '
        f'fill="{fill}" text-anchor="{anchor}"{cls}>{_escape_xml(content)}</text>'
    )


def path(d: str, fill: str = "none", stroke: str = "#94a3b8", stroke_width: float = 1) -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def polygon(points: list[tuple[float, float]], fill: str, stroke: str = "none") -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}"/>'


def _escape_xml(value: Any) -> str:
    s = str(value)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def axis_x(
    x: float,
    y: float,
    length: float,
    label: str = "",
    ticks: list[tuple[float, str]] | None = None,
) -> list[str]:
    """Return SVG elements for a horizontal axis with optional ticks."""
    elements = [line(x, y, x + length, y, stroke="#64748b")]
    if ticks:
        for tx, tl in ticks:
            elements.append(line(x + tx, y, x + tx, y + 4, stroke="#64748b"))
            elements.append(
                text(x + tx, y + 16, tl, fill="#64748b", font_size=9, anchor="middle")
            )
    if label:
        elements.append(
            text(
                x + length / 2,
                y + 28,
                label,
                fill="#475569",
                font_size=11,
                anchor="middle",
            )
        )
    return elements


def axis_y(
    x: float,
    y: float,
    length: float,
    label: str = "",
    ticks: list[tuple[float, str]] | None = None,
) -> list[str]:
    """Return SVG elements for a vertical axis with optional ticks."""
    elements = [line(x, y, x, y - length, stroke="#64748b")]
    if ticks:
        for ty, tl in ticks:
            elements.append(line(x - 4, y - ty, x, y - ty, stroke="#64748b"))
            elements.append(
                text(x - 8, y - ty + 3, tl, fill="#64748b", font_size=9, anchor="end")
            )
    if label:
        # Use a rotated text group via transform
        lx = x - 30
        ly = y - length / 2
        elements.append(
            f'<text x="{lx}" y="{ly}" font-size="11" fill="#475569" '
            f'text-anchor="middle" transform="rotate(-90 {lx} {ly})">'
            f"{_escape_xml(label)}</text>"
        )
    return elements
