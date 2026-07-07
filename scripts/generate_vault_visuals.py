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


def draw_domain_selection_map() -> Path:
    """Decision-style diagram for choosing an optical domain."""
    fig, ax = plt.subplots(figsize=(10, 7))
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    # Root question
    ax.add_patch(FancyBboxPatch((0.35, 0.88), 0.3, 0.08, boxstyle="round,pad=0.02",
                                facecolor="#f3f4f6", edgecolor="#374151", linewidth=2))
    ax.text(0.5, 0.92, "你的核心目标是什么？", ha="center", va="center", fontsize=12, fontweight="bold")

    branches = [
        ("检测/测量尺寸、缺陷、位置", "工业视觉", "#60a5fa", 0.12),
        ("拍出好看/准确的照片", "摄影", "#f472b6", 0.37),
        ("观察微小结构", "显微镜", "#4ade80", 0.62),
        ("夜间/热/不可见光成像", "红外成像", "#fbbf24", 0.87),
    ]
    for label, domain, color, x in branches:
        # Question branch
        ax.add_patch(FancyBboxPatch((x - 0.1, 0.68), 0.2, 0.12, boxstyle="round,pad=0.02",
                                    facecolor="white", edgecolor="#9ca3af", linewidth=1.5))
        ax.text(x, 0.74, label, ha="center", va="center", fontsize=8, wrap=True)
        # Domain box
        ax.add_patch(FancyBboxPatch((x - 0.07, 0.45), 0.14, 0.12, boxstyle="round,pad=0.02",
                                    facecolor=color, edgecolor="#374151", linewidth=1.5, alpha=0.85))
        ax.text(x, 0.51, domain, ha="center", va="center", fontsize=10, fontweight="bold", color="white")
        # Arrows
        ax.annotate("", xy=(x, 0.57), xytext=(x, 0.68),
                    arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.5))

    # Spectroscopy as cross-domain
    ax.add_patch(FancyBboxPatch((0.35, 0.22), 0.3, 0.12, boxstyle="round,pad=0.02",
                                facecolor="#f87171", edgecolor="#374151", linewidth=1.5, alpha=0.85))
    ax.text(0.5, 0.28, "光谱成像 / 色彩科学\n（跨域分析工具）", ha="center", va="center",
            fontsize=10, fontweight="bold", color="white")
    for _, _, _, x in branches:
        ax.plot([x, 0.5], [0.45, 0.34], color="#9ca3af", lw=1, alpha=0.6)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("如何选择光学应用领域？", fontsize=15, fontweight="bold", pad=20)
    return save(fig, "domain-selection-map.svg")


def draw_matching_workflow() -> Path:
    """LensFit matching pipeline flowchart."""
    fig, ax = plt.subplots(figsize=(12, 4))
    from matplotlib.patches import FancyBboxPatch

    steps = [
        ("输入需求", "#e5e7eb"),
        ("领域路由", "#dbeafe"),
        ("数据库预过滤", "#bfdbfe"),
        ("物理约束评分", "#93c5fd"),
        ("What-if 分析", "#60a5fa"),
        ("Top-K 推荐", "#2563eb"),
        ("导出报告", "#1e40af"),
    ]
    x_positions = [i * 1.35 for i in range(len(steps))]
    for (label, color), x in zip(steps, x_positions):
        ax.add_patch(FancyBboxPatch((x, 0.35), 1.1, 0.3, boxstyle="round,pad=0.02",
                                    facecolor=color, edgecolor="#374151", linewidth=1.5))
        ax.text(x + 0.55, 0.5, label, ha="center", va="center", fontsize=10, fontweight="bold",
                color="white" if color in ("#2563eb", "#1e40af") else "#1f2937")
        if x < x_positions[-1]:
            ax.annotate("", xy=(x + 1.15, 0.5), xytext=(x + 1.1, 0.5),
                        arrowprops=dict(arrowstyle="->", color="#4b5563", lw=2))

    ax.set_xlim(-0.2, x_positions[-1] + 1.3)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("LensFit 自动匹配工作流程", fontsize=15, fontweight="bold", pad=20)
    return save(fig, "matching-workflow.svg")


def draw_sensor_parameter_map() -> Path:
    """Spider-like parameter map for sensor selection."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    categories = ["分辨率", "像元尺寸", "动态范围", "读出噪声", "帧率", "快门方式"]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Example: global-shutter industrial sensor
    values = [0.7, 0.6, 0.7, 0.8, 0.8, 1.0]
    values += values[:1]
    ax.plot(angles, values, "o-", linewidth=2, label="工业传感器", color="#2563eb")
    ax.fill(angles, values, alpha=0.25, color="#2563eb")

    # Example: high-res photography sensor
    values2 = [1.0, 0.4, 0.8, 0.5, 0.4, 0.0]
    values2 += values2[:1]
    ax.plot(angles, values2, "o-", linewidth=2, label="摄影传感器", color="#f59e0b")
    ax.fill(angles, values2, alpha=0.15, color="#f59e0b")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_title("传感器选型雷达图（示意）", fontsize=14, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), frameon=False)
    return save(fig, "sensor-parameter-map.svg")


def draw_lens_selection_checklist() -> Path:
    """A checklist-style visualization for lens selection."""
    fig, ax = plt.subplots(figsize=(8, 7))
    from matplotlib.patches import FancyBboxPatch

    items = [
        ("1. 确定工作距离 (WD)", "#2563eb"),
        ("2. 计算所需焦距 / 视角", "#3b82f6"),
        ("3. 确认像圈 ≥ 传感器对角线", "#60a5fa"),
        ("4. 选择合适 F 值（进光/景深）", "#93c5fd"),
        ("5. 检查接口与法兰距", "#bfdbfe"),
        ("6. 评估畸变、色差等像质指标", "#dbeafe"),
        ("7. 考虑照明与波长范围", "#e5e7eb"),
    ]
    y = 0.88
    for text, color in items:
        ax.add_patch(FancyBboxPatch((0.1, y - 0.04), 0.8, 0.07, boxstyle="round,pad=0.015",
                                    facecolor=color, edgecolor="#1f2937", linewidth=1.2))
        ax.text(0.5, y, text, ha="center", va="center", fontsize=11, fontweight="bold",
                color="white" if color in ("#2563eb", "#3b82f6") else "#1f2937")
        y -= 0.12

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("镜头选型七步检查清单", fontsize=15, fontweight="bold", pad=20)
    return save(fig, "lens-selection-checklist.svg")


def draw_refractive_index() -> Path:
    """Light bending at an interface due to refractive index change."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.axhline(0, color="#374151", linewidth=2)
    ax.text(0.5, 0.08, "界面", ha="center", fontsize=11)

    # Incident ray
    ax.annotate("", xy=(0, 0), xytext=(-1.5, 1.2),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=2))
    ax.text(-1.2, 1.0, "入射光", color="#2563eb", fontsize=10)

    # Refracted ray
    ax.annotate("", xy=(1.5, 0.6), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=2))
    ax.text(1.2, 0.4, "折射光", color="#dc2626", fontsize=10)

    # Normal line
    ax.axvline(0, ymin=0.1, ymax=0.9, color="#9ca3af", linestyle="--", lw=1)
    ax.text(0.1, 1.3, "法线", color="#6b7280", fontsize=9)

    ax.text(-0.8, 0.35, r"$n_1$", fontsize=12, fontweight="bold")
    ax.text(0.8, -0.35, r"$n_2$", fontsize=12, fontweight="bold")
    ax.text(0.5, -0.7, "斯涅尔定律：$n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2$",
            fontsize=11, ha="center")

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.2, 1.6)
    ax.axis("off")
    ax.set_title("折射率：光在两种介质界面上的弯折", fontsize=14, fontweight="bold")
    return save(fig, "refractive-index.svg")


def draw_dispersion() -> Path:
    """Prism splitting white light into spectrum."""
    fig, ax = plt.subplots(figsize=(8, 5))
    from matplotlib.patches import Polygon

    # White incident ray
    ax.annotate("", xy=(1.5, 0.5), xytext=(-0.5, 0.5),
                arrowprops=dict(arrowstyle="->", color="#374151", lw=3))
    ax.text(-0.3, 0.6, "白光", fontsize=10)

    # Prism
    prism = Polygon([[1.5, 0.2], [2.5, 0.8], [2.5, 0.2]], closed=True,
                    facecolor="#e5e7eb", edgecolor="#374151", linewidth=2)
    ax.add_patch(prism)
    ax.text(2.2, 0.35, "棱镜", fontsize=10)

    # Dispersed rays
    colors = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6", "#a855f7"]
    y_offsets = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7]
    for color, y in zip(colors, y_offsets):
        ax.plot([2.5, 5], [0.5, y], color=color, lw=2.5)
    ax.text(5.1, 0.55, "红", color="#ef4444", fontsize=9)
    ax.text(5.1, 0.72, "紫", color="#a855f7", fontsize=9)

    ax.set_xlim(-1, 6)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("色散：不同波长的光折射角度不同", fontsize=14, fontweight="bold")
    return save(fig, "dispersion.svg")


def draw_chromatic_aberration() -> Path:
    """Lens focusing blue and red light at different focal points."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axvline(0, ymin=0.3, ymax=0.7, color="#374151", linewidth=3)
    ax.text(0, 0.22, "透镜", ha="center", fontsize=10)

    # Optical axis
    ax.axhline(0.5, color="#9ca3af", linestyle="--", lw=1)

    # Blue ray (shorter focal length)
    ax.plot([-2, 0, 1.8], [0.7, 0.7, 0.5], color="#3b82f6", lw=2)
    ax.scatter([1.8], [0.5], color="#3b82f6", s=50, zorder=3)
    ax.text(1.8, 0.43, "蓝光焦点", ha="center", color="#3b82f6", fontsize=9)

    # Red ray (longer focal length)
    ax.plot([-2, 0, 2.8], [0.7, 0.7, 0.5], color="#ef4444", lw=2)
    ax.scatter([2.8], [0.5], color="#ef4444", s=50, zorder=3)
    ax.text(2.8, 0.43, "红光焦点", ha="center", color="#ef4444", fontsize=9)

    ax.set_xlim(-3, 4)
    ax.set_ylim(0.2, 0.9)
    ax.axis("off")
    ax.set_title("色差：不同波长焦距不同，导致彩色边缘", fontsize=14, fontweight="bold")
    return save(fig, "chromatic-aberration.svg")


def draw_color_temperature() -> Path:
    """Blackbody spectra at different temperatures."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 4))
    wavelengths = np.linspace(300, 1200, 500)

    def planck(w, T):
        h, c, k = 6.626e-34, 3e8, 1.381e-23
        return (2 * h * c**2 / w**5) / (np.exp(h * c / (w * k * T)) - 1)

    temps = [3000, 4500, 6500]
    colors = ["#f97316", "#facc15", "#3b82f6"]
    labels = ["3000K 暖白", "4500K 中性", "6500K 冷白"]
    for T, color, label in zip(temps, colors, labels):
        y = planck(wavelengths * 1e-9, T)
        ax.plot(wavelengths, y / y.max(), color=color, lw=2, label=label)

    ax.set_xlabel("波长 (nm)")
    ax.set_ylabel("归一化辐射强度")
    ax.set_title("色温：黑体辐射谱随温度变化", fontsize=14, fontweight="bold")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "color-temperature.svg")


def draw_multispectral_hyperspectral() -> Path:
    """Compare multispectral vs hyperspectral imaging band counts."""
    fig, ax = plt.subplots(figsize=(8, 4))
    import numpy as np
    x = np.linspace(400, 1000, 1000)

    # Hyperspectral: many narrow bands
    for i, center in enumerate(range(420, 980, 20)):
        y = np.exp(-((x - center) ** 2) / 50)
        ax.fill_between(x, y + i * 0.05, i * 0.05, color="#3b82f6", alpha=0.4)

    # Multispectral: few broad bands
    bands = [(450, 80, "#ef4444"), (550, 80, "#22c55e"), (650, 80, "#eab308"), (850, 100, "#a855f7")]
    offset = -0.25
    for center, width, color in bands:
        y = np.exp(-((x - center) ** 2) / (width**2 / 4))
        ax.fill_between(x, y + offset, offset, color=color, alpha=0.6)

    ax.text(1050, 2.2, "高光谱\n窄带、连续", fontsize=10, color="#3b82f6", fontweight="bold")
    ax.text(1050, -0.15, "多光谱\n宽带、离散", fontsize=10, color="#374151", fontweight="bold")
    ax.set_xlabel("波长 (nm)")
    ax.set_title("多光谱 vs 高光谱：波段数量与宽度", fontsize=14, fontweight="bold")
    ax.set_ylim(-0.4, 2.8)
    ax.axis("off")
    return save(fig, "multispectral-hyperspectral.svg")


def draw_multispectral_filter_array() -> Path:
    """Compare a Bayer color filter array with a multispectral filter array."""
    from matplotlib.patches import Rectangle, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")

    def draw_grid(origin_x: float, origin_y: float, labels: list[list[str]], colors: dict[str, str], title: str) -> None:
        cell = 0.55
        rows = len(labels)
        cols = len(labels[0])
        for r, row in enumerate(labels):
            for c, label in enumerate(row):
                x = origin_x + c * cell
                y = origin_y + (rows - 1 - r) * cell
                ax.add_patch(Rectangle((x, y), cell, cell, facecolor=colors[label], edgecolor="white", linewidth=1.2))
                ax.text(x + cell / 2, y + cell / 2, label, ha="center", va="center", fontsize=9, fontweight="bold")
        ax.add_patch(Rectangle((origin_x, origin_y), cols * cell, rows * cell, fill=False, edgecolor="#374151", linewidth=1.5))
        ax.text(origin_x + cols * cell / 2, origin_y + rows * cell + 0.35, title, ha="center", fontsize=12, fontweight="bold")

    bayer = [
        ["G", "R", "G", "R"],
        ["B", "G", "B", "G"],
        ["G", "R", "G", "R"],
        ["B", "G", "B", "G"],
    ]
    bayer_colors = {"R": "#ef4444", "G": "#22c55e", "B": "#3b82f6"}
    draw_grid(0.7, 2.2, bayer, bayer_colors, "Bayer CFA：3 个宽光谱通道")

    msfa = [
        ["λ1", "λ2", "λ3", "λ4"],
        ["λ5", "λ6", "λ7", "λ8"],
        ["λ3", "λ4", "λ1", "λ2"],
        ["λ7", "λ8", "λ5", "λ6"],
    ]
    msfa_colors = {
        "λ1": "#7dd3fc", "λ2": "#38bdf8", "λ3": "#818cf8", "λ4": "#a78bfa",
        "λ5": "#f472b6", "λ6": "#fb7185", "λ7": "#fbbf24", "λ8": "#84cc16",
    }
    draw_grid(4.3, 2.2, msfa, msfa_colors, "MSFA：4-16+ 个窄光谱通道")

    ax.add_patch(FancyArrowPatch((3.15, 3.3), (4.0, 3.3), arrowstyle="->", mutation_scale=18, linewidth=2, color="#6b7280"))
    ax.text(3.55, 3.55, "扩展", ha="center", fontsize=10, color="#374151")

    # Spectral cube sketch.
    cube_x, cube_y = 8.2, 2.15
    for offset, color in [(0.45, "#bae6fd"), (0.25, "#ddd6fe"), (0.05, "#fecdd3")]:
        ax.add_patch(Rectangle((cube_x + offset, cube_y + offset), 1.75, 1.35, facecolor=color, edgecolor="#374151", alpha=0.85))
    ax.text(cube_x + 1.15, cube_y + 2.15, "重建后的光谱立方体", ha="center", fontsize=12, fontweight="bold")
    ax.text(cube_x + 1.15, cube_y + 1.05, "x, y, λ", ha="center", va="center", fontsize=13, fontweight="bold", color="#1f2937")
    ax.add_patch(FancyArrowPatch((7.05, 3.3), (8.15, 3.3), arrowstyle="->", mutation_scale=18, linewidth=2, color="#6b7280"))
    ax.text(7.6, 3.55, "去马赛克\n+ 光谱重建", ha="center", fontsize=10, color="#374151")

    ax.text(1.8, 1.35, "每个像素只测 R/G/B 中的一种", ha="center", fontsize=10, color="#4b5563")
    ax.text(5.4, 1.35, "每个像素只测一个窄波段", ha="center", fontsize=10, color="#4b5563")
    ax.text(9.25, 1.35, "空间分辨率与光谱通道数需要折中", ha="center", fontsize=10, color="#4b5563")
    ax.set_title("从 Bayer 到多光谱滤光片阵列：把颜色马赛克扩展为光谱马赛克", fontsize=15, fontweight="bold", pad=14)
    return save(fig, "multispectral-filter-array.svg")


def draw_spectral_power_distribution() -> Path:
    """Example SPD curve with peak wavelength."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.linspace(380, 780, 500)
    y = np.exp(-((x - 550) ** 2) / 2000)
    ax.fill_between(x, y, alpha=0.3, color="#2563eb")
    ax.plot(x, y, color="#2563eb", lw=2)
    ax.axvline(550, color="#dc2626", linestyle="--", lw=1.5)
    ax.text(560, 0.85, "峰值波长", color="#dc2626", fontsize=10)
    ax.set_xlabel("波长 (nm)")
    ax.set_ylabel("相对功率")
    ax.set_title("光谱功率分布 (SPD) 示例", fontsize=14, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "spectral-power-distribution.svg")


def draw_fluorescence() -> Path:
    """Simplified Jablonski diagram for fluorescence."""
    fig, ax = plt.subplots(figsize=(7, 5))
    # Ground and excited states
    ax.hlines(0.2, 0.1, 0.9, color="#374151", linewidth=3)
    ax.hlines(0.8, 0.1, 0.9, color="#374151", linewidth=3)
    ax.text(0.5, 0.1, "基态 S0", ha="center", fontsize=11)
    ax.text(0.5, 0.88, "激发态 S1", ha="center", fontsize=11)

    # Absorption
    ax.annotate("", xy=(0.35, 0.8), xytext=(0.35, 0.2),
                arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))
    ax.text(0.15, 0.55, "吸收", color="#ef4444", fontsize=10)

    # Non-radiative relaxation
    ax.plot([0.5, 0.5], [0.8, 0.65], color="#9ca3af", lw=2)
    ax.text(0.55, 0.72, "无辐射弛豫", color="#6b7280", fontsize=9)

    # Emission
    ax.annotate("", xy=(0.65, 0.2), xytext=(0.65, 0.65),
                arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
    ax.text(0.7, 0.4, "荧光发射", color="#22c55e", fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("荧光：吸收高能光后发射低能光", fontsize=14, fontweight="bold")
    return save(fig, "fluorescence.svg")


def draw_raman_scattering() -> Path:
    """Energy diagram for Raman scattering."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hlines(0.2, 0.1, 0.9, color="#374151", linewidth=3)
    ax.hlines(0.8, 0.1, 0.9, color="#374151", linewidth=3)
    ax.text(0.5, 0.1, "虚能级 / 基态", ha="center", fontsize=11)
    ax.text(0.5, 0.88, "实能级", ha="center", fontsize=11)

    # Rayleigh
    ax.annotate("", xy=(0.35, 0.2), xytext=(0.35, 0.8),
                arrowprops=dict(arrowstyle="->", color="#9ca3af", lw=2))
    ax.text(0.15, 0.55, "瑞利散射", color="#6b7280", fontsize=10)

    # Stokes
    ax.annotate("", xy=(0.6, 0.2), xytext=(0.6, 0.8),
                arrowprops=dict(arrowstyle="->", color="#2563eb", lw=2))
    ax.plot([0.6, 0.6], [0.2, 0.12], color="#2563eb", lw=2)
    ax.hlines(0.12, 0.55, 0.65, color="#2563eb", linewidth=3)
    ax.text(0.7, 0.5, "斯托克斯拉曼", color="#2563eb", fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("拉曼散射：光子与分子交换能量，波长发生偏移", fontsize=14, fontweight="bold")
    return save(fig, "raman-scattering.svg")


def draw_global_vs_rolling_shutter() -> Path:
    """Compare global and rolling shutter readout."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    import numpy as np

    def draw_sensor(ax, title, rolling=False):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=12, fontweight="bold")
        # Draw rows
        for i in range(5):
            color = "#bfdbfe" if (not rolling or i == 2) else "#e5e7eb"
            ax.add_patch(plt.Rectangle((0.1, 0.1 + i * 0.15), 0.8, 0.12,
                                         facecolor=color, edgecolor="#374151"))
            ax.text(0.5, 0.16 + i * 0.15, f"行 {i+1}", ha="center", va="center", fontsize=8)
        if rolling:
            ax.annotate("", xy=(0.95, 0.55), xytext=(0.95, 0.85),
                        arrowprops=dict(arrowstyle="->", color="#dc2626", lw=2))
            ax.text(1.0, 0.7, "逐行\n扫描", color="#dc2626", fontsize=9)
        else:
            ax.text(0.5, 0.05, "同时曝光/读出", ha="center", fontsize=9, color="#2563eb")

    draw_sensor(ax1, "全局快门 (Global Shutter)", rolling=False)
    draw_sensor(ax2, "卷帘快门 (Rolling Shutter)", rolling=True)
    fig.suptitle("全局快门 vs 卷帘快门：运动物体的形变差异", fontsize=14, fontweight="bold")
    return save(fig, "global-vs-rolling-shutter.svg")


def draw_telecentricity() -> Path:
    """Telecentric lens: chief rays parallel to optical axis."""
    fig, ax = plt.subplots(figsize=(8, 5))
    # Lens
    ax.axvline(0, ymin=0.2, ymax=0.8, color="#374151", linewidth=4)
    ax.text(0, 0.12, "远心镜头", ha="center", fontsize=10)

    # Parallel rays from object points
    y_positions = [0.35, 0.5, 0.65]
    for y in y_positions:
        ax.plot([-2, 2], [y, y], color="#2563eb", lw=1.5, alpha=0.7)
        ax.scatter([-1.5], [y], color="#f59e0b", s=40, zorder=3)
        ax.text(-1.6, y, "物点", ha="right", va="center", fontsize=8)
        ax.scatter([1.5], [y], color="#dc2626", s=40, zorder=3)
        ax.text(1.6, y, "像点", ha="left", va="center", fontsize=8)

    ax.axhline(0.5, color="#9ca3af", linestyle="--", lw=1)
    ax.text(0.5, 0.52, "光轴", fontsize=9, color="#6b7280")
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0.1, 0.9)
    ax.axis("off")
    ax.set_title("远心镜头：主光线与光轴平行，消除透视畸变", fontsize=14, fontweight="bold")
    return save(fig, "telecentricity.svg")


def draw_abbe_number() -> Path:
    """Abbe diagram: refractive index vs Abbe number."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 5))
    # Mock glass types
    np.random.seed(0)
    nd = np.random.uniform(1.45, 2.0, 40)
    vd = 80 - 60 * (nd - 1.45) / 0.55 + np.random.normal(0, 5, 40)
    ax.scatter(nd, vd, c="#3b82f6", alpha=0.6, s=60)
    ax.set_xlabel("折射率 n_d")
    ax.set_ylabel("阿贝数 V_d")
    ax.set_title("阿贝图：折射率越高，阿贝数通常越低（色散越大）", fontsize=13, fontweight="bold")
    ax.text(1.55, 35, "高色散\n（低阿贝数）", fontsize=9, color="#7f1d1d")
    ax.text(1.85, 70, "低色散\n（高阿贝数）", fontsize=9, color="#064e3b")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "abbe-number.svg")


def draw_chromaticity_diagram() -> Path:
    """Simplified CIE 1931 chromaticity diagram."""
    fig, ax = plt.subplots(figsize=(7, 6))
    from matplotlib.patches import Polygon
    # Approximate horseshoe boundary
    x = [0.17, 0.0, 0.13, 0.43, 0.73, 0.83, 0.73, 0.52, 0.27, 0.17]
    y = [0.01, 0.0, 0.55, 0.83, 0.83, 0.55, 0.27, 0.08, 0.01, 0.01]
    ax.fill(x, y, color="#e0f2fe", alpha=0.6)
    ax.plot(x + [x[0]], y + [y[0]], color="#0369a1", lw=2)
    # RGB gamut triangle
    ax.plot([0.64, 0.30, 0.15, 0.64], [0.33, 0.60, 0.06, 0.33], "r--", lw=2)
    ax.text(0.33, 0.33, "sRGB 色域", color="#b91c1c", fontsize=10)
    ax.scatter([0.3127], [0.3290], color="#000", s=40, zorder=3)
    ax.text(0.33, 0.34, "D65 白点", fontsize=9)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("CIE 1931 色度图（示意）：马蹄形色域与 sRGB 三角", fontsize=13, fontweight="bold")
    ax.set_aspect("equal")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save(fig, "chromaticity-diagram.svg")


def draw_spectral_resolution() -> Path:
    """Two close spectral peaks separated vs unresolved."""
    import numpy as np
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    x = np.linspace(600, 700, 500)
    y1 = np.exp(-((x - 640) ** 2) / 50) + np.exp(-((x - 660) ** 2) / 50)
    y2 = np.exp(-((x - 640) ** 2) / 400) + np.exp(-((x - 660) ** 2) / 400)

    ax1.plot(x, y1, color="#2563eb", lw=2)
    ax1.set_title("高光谱分辨率：两峰可分辨", fontsize=12, fontweight="bold")
    ax1.set_xlabel("波长 (nm)")
    ax1.set_ylabel("强度")

    ax2.plot(x, y2, color="#dc2626", lw=2)
    ax2.set_title("低光谱分辨率：两峰合并", fontsize=12, fontweight="bold")
    ax2.set_xlabel("波长 (nm)")

    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    return save(fig, "spectral-resolution.svg")


def draw_numerical_aperture() -> Path:
    """Cone angle for numerical aperture."""
    fig, ax = plt.subplots(figsize=(6, 6))
    from matplotlib.patches import Arc
    # Object point and lens
    ax.scatter([0], [0], color="#f59e0b", s=80, zorder=3)
    ax.text(-0.15, 0.05, "物点", fontsize=10, color="#b45309")
    ax.axvline(1.5, ymin=0.2, ymax=0.8, color="#374151", linewidth=4)
    ax.text(1.5, 0.12, "物镜", ha="center", fontsize=10)

    # Cone
    ax.plot([0, 1.5], [0, 0.7], color="#2563eb", lw=1.5)
    ax.plot([0, 1.5], [0, -0.7], color="#2563eb", lw=1.5)
    ax.plot([0.3, 1.5], [0, 0.14], color="#9ca3af", linestyle="--", lw=1)
    ax.text(0.5, 0.18, "θ", fontsize=11)
    ax.text(0.75, -0.35, "NA = n · sin θ", fontsize=12, fontweight="bold", color="#1e40af")

    ax.set_xlim(-0.5, 2.2)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("数值孔径 NA：半孔径角越大，NA 越大", fontsize=13, fontweight="bold")
    return save(fig, "numerical-aperture.svg")


def draw_vignetting() -> Path:
    """Brightness falloff from center to corner."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(6, 6))
    x = np.linspace(-1, 1, 200)
    y = np.linspace(-1, 1, 200)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.cos(R * np.pi / 2.2) ** 2
    Z[R > 1] = np.nan
    ax.imshow(Z, extent=[-1, 1, -1, 1], origin="lower", cmap="gray")
    ax.set_title("渐晕：图像边缘亮度低于中心", fontsize=13, fontweight="bold")
    ax.axis("off")
    return save(fig, "vignetting.svg")


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
    paths.append(draw_domain_selection_map())
    paths.append(draw_matching_workflow())
    paths.append(draw_sensor_parameter_map())
    paths.append(draw_lens_selection_checklist())
    paths.append(draw_refractive_index())
    paths.append(draw_dispersion())
    paths.append(draw_chromatic_aberration())
    paths.append(draw_color_temperature())
    paths.append(draw_multispectral_hyperspectral())
    paths.append(draw_multispectral_filter_array())
    paths.append(draw_spectral_power_distribution())
    paths.append(draw_fluorescence())
    paths.append(draw_raman_scattering())
    paths.append(draw_global_vs_rolling_shutter())
    paths.append(draw_telecentricity())
    paths.append(draw_abbe_number())
    paths.append(draw_chromaticity_diagram())
    paths.append(draw_spectral_resolution())
    paths.append(draw_numerical_aperture())
    paths.append(draw_vignetting())
    print(f"Generated {len(paths)} visuals in {OUTDIR}:")
    for p in paths:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
