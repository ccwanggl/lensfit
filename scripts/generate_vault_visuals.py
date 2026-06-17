"""Generate static visualizations for the LensFit Obsidian knowledge vault.

Run from the repository root:

    python scripts/generate_vault_visuals.py

Requires a Python environment with matplotlib and networkx.
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import networkx as nx

# Use a CJK-capable font on Windows so Chinese titles/labels render in SVGs.
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans SC",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False

VAULT = Path("OpticKnowledgeSpace")
OUTDIR = VAULT / "attachments" / "visuals"


def save(fig: plt.Figure, name: str) -> Path:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = OUTDIR / name
    fig.savefig(path, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def draw_learning_path_roadmap() -> Path:
    """Horizontal roadmap of the 16 learning chapters grouped by phase."""
    phases = [
        ("入门", "#4ade80", 10),
        ("匹配", "#60a5fa", 4),
        ("像质", "#f472b6", 3),
        ("工程", "#fbbf24", 3),
        ("进阶", "#a78bfa", 4),
        ("光谱", "#f87171", 2),
    ]
    chapters = []
    labels = []
    for i in range(17):
        chapters.append(i)
        labels.append(f"第{i}章" if i else "绪论")

    fig, ax = plt.subplots(figsize=(16, 4))
    y = 0
    for i, (label, color, _size) in enumerate(phases):
        ax.scatter([i], [y], s=200, c=color, zorder=3)
        ax.text(i, y + 0.15, label, ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.plot(range(len(phases)), [y] * len(phases), "k-", linewidth=2, zorder=1)
    ax.set_xlim(-0.5, len(phases) - 0.5)
    ax.set_ylim(-0.5, 0.8)
    ax.axis("off")
    ax.set_title("LensFit 光学学习路径：从入门到光谱专项", fontsize=16, fontweight="bold", pad=20)

    # Subtitle with chapter ranges
    ranges = ["0–9", "10–13", "14", "15–16"]
    ax.text(0.5, -0.25, "建议顺序：先完成 0–9 章建立直觉 → 10–13 章深入物理 → 14 章计算成像 → 15–16 章工程与光谱",
            transform=ax.transAxes, ha="center", fontsize=10, color="#4b5563")
    return save(fig, "learning-path-roadmap.svg")


def draw_thin_lens_geometry() -> Path:
    """Simple thin-lens ray diagram."""
    fig, ax = plt.subplots(figsize=(8, 5))
    # Lens vertical line
    ax.axvline(0, ymin=0.2, ymax=0.8, color="#374151", linewidth=3)
    ax.text(0, 0.15, "薄透镜", ha="center", fontsize=11)

    # Optical axis
    ax.axhline(0.5, color="#9ca3af", linewidth=1, linestyle="--")

    # Object arrow
    ax.annotate("", xy=(-2.5, 0.5), xytext=(-2.5, 0.75),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=2))
    ax.text(-2.5, 0.82, "物体", ha="center", color="#2563eb", fontsize=10)
    ax.text(-2.5, 0.4, "物距 u", ha="center", fontsize=9)

    # Image arrow
    ax.annotate("", xy=(2.5, 0.5), xytext=(2.5, 0.25),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=2))
    ax.text(2.5, 0.18, "像", ha="center", color="#dc2626", fontsize=10)
    ax.text(2.5, 0.42, "像距 v", ha="center", fontsize=9)

    # Focal points
    ax.scatter([-1.2, 1.2], [0.5, 0.5], c="#f59e0b", s=80, zorder=3)
    ax.text(-1.2, 0.45, "F", ha="center", fontsize=10, color="#b45309")
    ax.text(1.2, 0.45, "F", ha="center", fontsize=10, color="#b45309")

    # Principal rays (simplified)
    ax.plot([-2.5, 0, 2.5], [0.75, 0.75, 0.25], color="#2563eb", lw=1.5, alpha=0.6)
    ax.plot([-2.5, 2.5], [0.75, 0.25], color="#2563eb", lw=1.5, alpha=0.6)

    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("薄透镜高斯公式：1/f = 1/u + 1/v", fontsize=14, fontweight="bold")
    return save(fig, "thin-lens-geometry.svg")


def draw_angle_of_view() -> Path:
    """Angle of view as a function of focal length and sensor width."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sensor_w = 36.0  # full frame mm
    focal_lengths = [14, 24, 35, 50, 85, 135, 200]
    afovs = [2 * 57.3 * __import__("math").atan(sensor_w / (2 * f)) for f in focal_lengths]

    bars = ax.bar(range(len(focal_lengths)), afovs, color="#60a5fa", edgecolor="#1e40af")
    ax.set_xticks(range(len(focal_lengths)))
    ax.set_xticklabels([f"{f}mm" for f in focal_lengths])
    ax.set_ylabel("水平视角 (°)")
    ax.set_xlabel("焦距 (全画幅 36mm 传感器)")
    ax.set_title("焦距越短，视角越宽；焦距越长，视角越窄", fontsize=14, fontweight="bold")
    for bar, val in zip(bars, afovs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.0f}°", ha="center", fontsize=9)
    ax.set_ylim(0, 110)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "angle-of-view.svg")


def draw_image_circle_coverage() -> Path:
    """Sensor rectangle inside lens image circle."""
    fig, ax = plt.subplots(figsize=(6, 6))
    from matplotlib.patches import Circle, Rectangle

    circle = Circle((0.5, 0.5), 0.45, fill=False, edgecolor="#2563eb", linewidth=3, label="像圈")
    sensor = Rectangle((0.25, 0.30), 0.5, 0.4, fill=True, facecolor="#f87171", alpha=0.4,
                       edgecolor="#dc2626", linewidth=2, label="传感器")
    ax.add_patch(circle)
    ax.add_patch(sensor)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("像圈必须完全覆盖传感器，否则边缘会发黑", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", frameon=False)
    return save(fig, "image-circle-coverage.svg")


def draw_nyquist_aliasing() -> Path:
    """Sampling a high-frequency signal below Nyquist rate causes aliasing."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.linspace(0, 2 * np.pi, 500)
    y_high = np.sin(6 * x)
    sample_points = np.arange(0, 2 * np.pi, np.pi / 3)
    y_samples = np.sin(6 * sample_points)
    y_alias = np.sin(2 * sample_points)  # perceived lower frequency

    ax.plot(x, y_high, color="#9ca3af", lw=2, label="实际高频信号")
    ax.scatter(sample_points, y_samples, color="#2563eb", s=50, zorder=3, label="采样点")
    ax.plot(sample_points, y_alias, "r--", lw=2, label="重建出的低频伪影（混叠）")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_ylim(-1.3, 1.3)
    ax.set_title("采样不足时，高频信号会被误判为低频（混叠）", fontsize=13, fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    ax.axis("off")
    return save(fig, "nyquist-aliasing.svg")


def draw_airy_disk() -> Path:
    """Cross-section of Airy disk intensity."""
    import numpy as np
    from scipy.special import j1

    fig, ax = plt.subplots(figsize=(7, 4))
    r = np.linspace(0.01, 10, 500)
    intensity = (2 * j1(r) / r) ** 2
    ax.plot(r, intensity, color="#2563eb", lw=2)
    ax.fill_between(r, intensity, alpha=0.2, color="#2563eb")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("归一化半径")
    ax.set_ylabel("相对光强")
    ax.set_title("艾里斑：圆孔衍射的极限光斑", fontsize=13, fontweight="bold")
    ax.text(2.5, 0.5, "第一暗环\n≈1.22 λF#", fontsize=10, color="#374151")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "airy-disk.svg")


def draw_depth_of_field() -> Path:
    """Depth of field: acceptable circle of confusion before/after focus plane."""
    fig, ax = plt.subplots(figsize=(8, 4))
    from matplotlib.patches import FancyArrowPatch

    # Lens and focus plane
    ax.axvline(0, ymin=0.3, ymax=0.7, color="#374151", linewidth=5)
    ax.axvline(3, ymin=0.1, ymax=0.9, color="#dc2626", linestyle="--", alpha=0.6)
    ax.text(3, 0.05, "对焦平面", ha="center", color="#dc2626", fontsize=10)

    # Object points and CoC circles
    ax.scatter([-1.5, 3, 6], [0.5, 0.5, 0.5], c="#2563eb", s=60, zorder=3)
    ax.text(-1.5, 0.42, "近处物\n(模糊)", ha="center", fontsize=9)
    ax.text(3, 0.55, "清晰成像", ha="center", fontsize=9)
    ax.text(6, 0.42, "远处物\n(模糊)", ha="center", fontsize=9)

    # CoC circles
    circle1 = plt.Circle((-1.5, 0.5), 0.12, fill=False, color="#f59e0b", lw=2)
    circle2 = plt.Circle((6, 0.5), 0.12, fill=False, color="#f59e0b", lw=2)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    ax.text(-1.5, 0.3, "弥散圆 CoC", ha="center", fontsize=8, color="#b45309")

    ax.annotate("", xy=(6.2, 0.5), xytext=(-1.7, 0.5),
                arrowprops=dict(arrowstyle="<->", color="#059669", lw=2))
    ax.text(2.25, 0.65, "景深范围", color="#059669", fontsize=10, fontweight="bold")

    ax.set_xlim(-3, 8)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("景深：超出对焦平面的物点会形成可接受的弥散圆", fontsize=13, fontweight="bold")
    return save(fig, "depth-of-field.svg")


def draw_aperture_f_number() -> Path:
    """Aperture diameter and f-number relationship."""
    fig, ax = plt.subplots(figsize=(6, 6))
    from matplotlib.patches import Circle

    f_numbers = [1.4, 2.0, 2.8, 4.0, 5.6, 8.0]
    colors = plt.cm.Blues_r([0.2 + 0.12 * i for i in range(len(f_numbers))])
    for i, (f, color) in enumerate(zip(f_numbers, colors)):
        r = 1.0 / f * 8  # arbitrary scaling for display
        circle = Circle((0, 0), r, fill=False, edgecolor=color, linewidth=3, label=f"F/{f}")
        ax.add_patch(circle)
        ax.text(r + 0.1, 0, f"F/{f}", va="center", fontsize=9, color=color)

    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("F 值越小，通光孔径越大，进光量越多", fontsize=13, fontweight="bold")
    return save(fig, "aperture-f-number.svg")


def draw_knowledge_graph() -> Path:
    """A small network graph connecting core concepts, formulas, domains and devices."""
    G = nx.Graph()
    core = [
        "焦距", "F值", "像圈", "奈奎斯特频率", "混叠", "艾里斑",
        "薄透镜公式", "视角公式", "覆盖比", "像素精度",
        "工业视觉", "摄影", "显微镜", "红外成像", "光谱成像",
        "远心镜头", "C-mount镜头", "显微镜物镜", "高光谱相机"
    ]
    G.add_nodes_from(core)
    edges = [
        ("焦距", "薄透镜公式"), ("焦距", "视角公式"), ("焦距", "摄影"),
        ("F值", "景深"), ("F值", "摄影"),
        ("像圈", "覆盖比"), ("像圈", "工业视觉"),
        ("奈奎斯特频率", "混叠"), ("像素精度", "奈奎斯特频率"),
        ("艾里斑", "显微镜"), ("艾里斑", "瑞利判据"),
        ("远心镜头", "工业视觉"), ("C-mount镜头", "工业视觉"),
        ("显微镜物镜", "显微镜"), ("高光谱相机", "光谱成像"),
    ]
    G.add_edges_from(edges)

    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42, k=1.5)
    node_colors = []
    for node in G.nodes():
        if node in {"工业视觉", "摄影", "显微镜", "红外成像", "光谱成像"}:
            node_colors.append("#f87171")
        elif node in {"远心镜头", "C-mount镜头", "显微镜物镜", "高光谱相机"}:
            node_colors.append("#fbbf24")
        elif "公式" in node or "比" in node or "精度" in node:
            node_colors.append("#60a5fa")
        else:
            node_colors.append("#4ade80")

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, ax=ax, alpha=0.9)
    nx.draw_networkx_edges(G, pos, alpha=0.4, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=9, ax=ax)
    ax.set_title("LensFit 核心知识关联图（示例子集）", fontsize=14, fontweight="bold")
    ax.axis("off")
    return save(fig, "knowledge-graph.svg")


def main():
    paths = []
    paths.append(draw_learning_path_roadmap())
    paths.append(draw_thin_lens_geometry())
    paths.append(draw_angle_of_view())
    paths.append(draw_image_circle_coverage())
    paths.append(draw_nyquist_aliasing())
    paths.append(draw_airy_disk())
    paths.append(draw_depth_of_field())
    paths.append(draw_aperture_f_number())
    paths.append(draw_knowledge_graph())
    print(f"Generated {len(paths)} visuals in {OUTDIR}:")
    for p in paths:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
