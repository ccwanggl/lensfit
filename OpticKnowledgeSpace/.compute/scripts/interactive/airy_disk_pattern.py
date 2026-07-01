"""
Airy disk diffraction pattern visualization.

Shows the radial intensity profile of an ideal circular aperture (Airy pattern)
and overlays Airy disk diameters for different wavelengths and F-numbers.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import j1
from oks_mpl import setup_fonts


def airy_pattern(r, kR):
    """
    Normalized Airy intensity I/I0 for a circular aperture.
    r: radial coordinate in focal plane (um)
    kR: wave number * aperture radius = 2*pi/lambda * (D/2)
    For plot convenience we use dimensionless x = kR * r / f = pi*r/(lambda*F#)
    """
    x = kR * r
    # avoid division by zero at origin
    intensity = np.zeros_like(x)
    mask = x > 1e-8
    intensity[mask] = (2 * j1(x[mask]) / x[mask]) ** 2
    intensity[~mask] = 1.0
    return intensity


def main():
    setup_fonts()
    parser = argparse.ArgumentParser(description='艾里斑衍射图样可视化')
    parser.add_argument('--no-display', action='store_true',
                        help='不显示图像窗口，仅保存 PNG 文件')
    args = parser.parse_args()

    # Radial coordinate in um
    r = np.linspace(0, 15, 1000)

    # Parameters: wavelength (um) and F-number
    configs = [
        {'wl': 0.45, 'F': 2.8, 'color': '#377eb8', 'label': '蓝光 450nm, F/2.8'},
        {'wl': 0.55, 'F': 2.8, 'color': '#4daf4a', 'label': '绿光 550nm, F/2.8'},
        {'wl': 0.65, 'F': 2.8, 'color': '#e41a1c', 'label': '红光 650nm, F/2.8'},
        {'wl': 0.55, 'F': 5.6, 'color': '#984ea3', 'linestyle': '--',
         'label': '绿光 550nm, F/5.6'},
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=150)

    # Left: radial intensity profile
    ax = axes[0]
    for cfg in configs:
        kR = np.pi / (cfg['wl'] * cfg['F'])
        intensity = airy_pattern(r, kR)
        linestyle = cfg.get('linestyle', '-')
        ax.plot(r, intensity, color=cfg['color'], linestyle=linestyle,
                linewidth=2, label=cfg['label'])
        # Mark first dark ring
        dark_ring = 2.44 * cfg['wl'] * cfg['F']
        ax.axvline(x=dark_ring, color=cfg['color'], linestyle=':', alpha=0.5)

    ax.set_xlabel('径向距离 r (μm)')
    ax.set_ylabel('归一化强度 I/I₀')
    ax.set_title('圆孔径夫琅禾费衍射艾里图样')
    ax.set_xlim([0, 15])
    ax.set_ylim([0, 1.05])
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Right: 2D airy disk image
    ax = axes[1]
    # Use green light F/2.8 for 2D example
    wl = 0.55
    F = 2.8
    side = 16  # um
    x = np.linspace(-side, side, 400)
    X, Y = np.meshgrid(x, x)
    rho = np.sqrt(X**2 + Y**2)
    kR = np.pi / (wl * F)
    img = airy_pattern(rho, kR)
    im = ax.imshow(img, extent=[-side, side, -side, side], origin='lower',
                   cmap='hot', vmin=0, vmax=1)
    # Add first dark ring circle
    dark_ring = 2.44 * wl * F
    circle = plt.Circle((0, 0), dark_ring, fill=False, color='cyan',
                        linewidth=1.5, linestyle='--')
    ax.add_patch(circle)
    ax.set_title(f'艾里斑二维强度分布\n绿光 550nm, F/{F}, 第一暗环直径 ≈ {2*dark_ring:.2f} μm')
    ax.set_xlabel('x (μm)')
    ax.set_ylabel('y (μm)')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='I/I₀')

    # Annotation text
    fig.text(
        0.5, 0.01,
        '艾里斑第一暗环直径: d = 2.44 · λ · F#   （λ 以 μm 为单位）',
        ha='center', fontsize=11,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.4)
    )

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    output_path = '../../../attachments/visuals/airy_disk_pattern.png'
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', dpi=150)
    print(f'Saved figure to {output_path}')

    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    main()
