"""
Interactive-style thin-lens parameter sweep visualization.

Generates a multi-panel figure showing how image distance v, magnification beta,
and focused plane move as object distance u changes for a thin lens of focal length f.
Designed for beginner-friendly conceptual understanding.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from oks_mpl import setup_fonts


def main():
    setup_fonts()
    parser = argparse.ArgumentParser(description='薄透镜参数扫描：物距-像距-放大率关系')
    parser.add_argument('--no-display', action='store_true',
                        help='不显示图像窗口，仅保存 PNG 文件')
    args = parser.parse_args()

    f = 50.0  # focal length mm
    # Object distance range: just beyond focal length to 10x focal length
    u = np.linspace(f * 1.02, f * 10, 500)
    v = f * u / (u - f)
    beta = v / u
    working_distance_approx = u  # for conceptual plot, treat u as WD

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=150)

    # Panel 1: v vs u
    ax = axes[0, 0]
    ax.plot(u, v, 'b-', linewidth=2)
    ax.axvline(x=f, color='gray', linestyle='--', alpha=0.5, label='u = f')
    ax.axhline(y=f, color='gray', linestyle='--', alpha=0.5, label='v = f')
    ax.set_xlabel('物距 u (mm)')
    ax.set_ylabel('像距 v (mm)')
    ax.set_title('像距随物距的变化')
    ax.set_xlim([u.min(), u.max()])
    ax.set_ylim([0, v.max() * 1.05])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    # Annotate example points
    examples_u = [60, 100, 200, 500]
    for u0 in examples_u:
        v0 = f * u0 / (u0 - f)
        ax.plot(u0, v0, 'ro', markersize=5)
        ax.annotate(f'u={u0}mm\nv={v0:.1f}mm', xy=(u0, v0),
                    xytext=(u0 + 30, v0 - 10), fontsize=8,
                    arrowprops=dict(arrowstyle='->', color='red', lw=0.8),
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

    # Panel 2: magnification beta vs u
    ax = axes[0, 1]
    ax.plot(u, beta, 'g-', linewidth=2)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('物距 u (mm)')
    ax.set_ylabel('横向放大率 β')
    ax.set_title('放大率随物距的变化')
    ax.set_xlim([u.min(), u.max()])
    ax.set_ylim([0, beta.max() * 1.05])
    ax.grid(True, alpha=0.3)

    for u0 in examples_u:
        b0 = f / (u0 - f)
        ax.plot(u0, b0, 'ro', markersize=5)
        ax.annotate(f'u={u0}mm\nβ={b0:.2f}', xy=(u0, b0),
                    xytext=(u0 + 30, b0 + 0.05), fontsize=8,
                    arrowprops=dict(arrowstyle='->', color='red', lw=0.8),
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

    # Panel 3: focal length vs object distance for fixed FOV and sensor
    ax = axes[1, 0]
    # Suppose WD = u, sensor width s = 8.8mm, FOV = s * u / f (for u >> f)
    s = 8.8  # mm, 2/3" sensor width
    fov = s * u / f
    ax.plot(u, fov, 'm-', linewidth=2)
    ax.set_xlabel('物距 u (mm)')
    ax.set_ylabel('视场 FOV (mm)')
    ax.set_title(f'固定焦距 f={f}mm、传感器宽 {s}mm 时的视场')
    ax.set_xlim([u.min(), u.max()])
    ax.grid(True, alpha=0.3)

    # Panel 4: conceptual ray diagram for a few object distances
    ax = axes[1, 1]
    draw_ray_diagram(ax, f, u_examples=[60, 100, 200])

    fig.suptitle(f'薄透镜成像参数关系（f = {f} mm）', fontsize=14, y=1.02)
    plt.tight_layout()

    output_path = '../../../attachments/visuals/thin_lens_parameter_sweep.png'
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', dpi=150)
    print(f'Saved figure to {output_path}')

    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)


def draw_ray_diagram(ax, f, u_examples):
    """Draw a simplified ray diagram for a few object distances."""
    ax.set_aspect('equal')
    ax.set_xlim([-20, 120])
    ax.set_ylim([-25, 25])
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_xlabel('光轴方向距离 (mm)')
    ax.set_ylabel('高度 (mm)')
    ax.set_title('典型物距下的成像光路')

    # Draw thin lens as vertical line at x=0
    ax.plot([0, 0], [-20, 20], 'b-', linewidth=3, solid_capstyle='round')
    ax.text(0, 22, '透镜', ha='center', fontsize=9, color='blue')

    # Focal points
    ax.plot([-f, f], [0, 0], 'ko', markersize=5)
    ax.text(-f, -3, 'F', ha='center', fontsize=9)
    ax.text(f, -3, 'F\'', ha='center', fontsize=9)

    colors = ['#e41a1c', '#377eb8', '#4daf4a']
    for i, u0 in enumerate(u_examples):
        color = colors[i % len(colors)]
        v0 = f * u0 / (u0 - f)
        beta0 = v0 / u0
        h_obj = 10.0  # object height
        h_img = beta0 * h_obj

        # Object arrow
        ax.arrow(-u0, 0, 0, h_obj, head_width=2, head_length=2,
                 fc=color, ec=color, linewidth=1.5, length_includes_head=True)
        # Image arrow (inverted if real)
        ax.arrow(v0, 0, 0, -h_img, head_width=2, head_length=2,
                 fc=color, ec=color, linewidth=1.5, alpha=0.7,
                 length_includes_head=True)

        # Ray 1: parallel to axis, then through focal point on image side
        ax.plot([-u0, 0], [h_obj, h_obj], '--', color=color, linewidth=1.2)
        ax.plot([0, v0 + 10], [h_obj, -h_img / v0 * 10],
                '-', color=color, linewidth=1.2)

        # Ray 2: through center (straight line)
        ax.plot([-u0, v0 + 10],
                [h_obj, -h_img / v0 * 10],
                '-', color=color, linewidth=1.2, alpha=0.6)

        ax.text(-u0, h_obj + 2, f'u={u0:.0f}', color=color, fontsize=8, ha='center')
        ax.text(v0, -h_img - 4, f'v={v0:.1f}\nβ={beta0:.2f}',
                color=color, fontsize=8, ha='center')

    ax.grid(True, alpha=0.2)


if __name__ == '__main__':
    main()
