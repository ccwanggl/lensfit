"""
Prism refraction and dispersion simulation using rayoptics' opticalglass database.

This script traces parallel rays of different wavelengths through a triangular prism
and visualizes how material dispersion separates white light into a spectrum.
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
from opticalglass.glassfactory import create_glass


def snell(n1, n2, theta1):
    """Snell's law: return theta2 given n1, n2, theta1 (in radians)."""
    sin_theta2 = (n1 / n2) * np.sin(theta1)
    if np.abs(sin_theta2) > 1.0:
        return None
    return np.arcsin(sin_theta2)


def normalize(v):
    return v / np.linalg.norm(v)


def line_intersection(p1, d1, p2, d2):
    """Return intersection of two lines: p1 + t*d1 and p2 + s*d2."""
    A = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
    b = p2 - p1
    t, s = np.linalg.solve(A, b)
    return p1 + t * d1


def trace_prism_ray(wavelength_nm, incident_angle_deg=40.0,
                    prism_apex_deg=60.0, prism_height=4.0):
    """
    Trace a single ray through an equilateral prism using outward surface normals.

    Returns ray path segments, prism vertices, and refractive index.
    """
    glass = create_glass('N-BK7', 'Schott')
    n_glass = glass.rindex(wavelength_nm)
    n_air = 1.0

    theta_i = np.radians(incident_angle_deg)

    # Prism vertices: equilateral triangle, apex at top, base horizontal at bottom
    half_base = prism_height * np.tan(np.radians(30.0))
    apex = np.array([0.0, prism_height / 2.0])
    base_left = np.array([-half_base, -prism_height / 2.0])
    base_right = np.array([half_base, -prism_height / 2.0])

    # Surface vectors (along the surface, upward)
    surf1_vec = apex - base_left
    surf2_vec = apex - base_right
    surf1_unit = normalize(surf1_vec)
    surf2_unit = normalize(surf2_vec)

    # Outward normals (pointing from prism into air)
    # Left face: outward points left/up
    n1_out = normalize(np.array([-surf1_unit[1], surf1_unit[0]]))
    # Right face: outward points right/up
    n2_out = normalize(np.array([surf2_unit[1], -surf2_unit[0]]))

    # Incident ray: from left, hitting left face. Angle theta_i measured from normal.
    # Since n1_out points outward, incident direction has component opposite to n1_out.
    # i = -cos(theta_i)*n1_out + sin(theta_i)*s1_tangent
    # Choose tangent direction so ray goes rightward.
    s1_tangent = normalize(np.array([surf1_unit[0], surf1_unit[1]]))
    incident_dir = -np.cos(theta_i) * n1_out + np.sin(theta_i) * s1_tangent
    incident_dir = normalize(incident_dir)

    # Ensure incident ray goes toward the prism (rightward)
    if incident_dir[0] < 0:
        incident_dir = -incident_dir

    # Entry point on left surface
    entry_point = base_left + 0.45 * surf1_vec

    # --- First refraction: air -> glass ---
    cos_i1 = -np.dot(incident_dir, n1_out)
    if cos_i1 <= 0:
        return None
    theta1 = np.arccos(np.clip(cos_i1, -1.0, 1.0))
    theta2 = snell(n_air, n_glass, theta1)
    if theta2 is None:
        return None

    # Refracted direction inside prism
    # Parallel component (along surface, in direction of incident parallel projection)
    parallel1 = incident_dir + cos_i1 * n1_out
    parallel1 = normalize(parallel1)
    refracted1 = np.sin(theta2) * parallel1 - np.cos(theta2) * n1_out
    refracted1 = normalize(refracted1)

    # --- Intersect with second surface ---
    p2 = line_intersection(entry_point, refracted1, apex, -surf2_vec)

    # Check p2 is on the segment
    t2 = np.dot(p2 - apex, -surf2_unit)
    if t2 < 0 or t2 > np.linalg.norm(surf2_vec):
        return None

    # --- Second refraction: glass -> air ---
    # Inside ray direction relative to outward normal n2_out
    cos_i2 = np.dot(refracted1, n2_out)
    if cos_i2 >= 0:
        # Ray is heading outward, good
        theta3 = np.arccos(np.clip(cos_i2, -1.0, 1.0))
    else:
        # Use inward normal
        theta3 = np.arccos(np.clip(-cos_i2, -1.0, 1.0))

    theta4 = snell(n_glass, n_air, theta3)
    if theta4 is None:
        return None

    parallel2 = refracted1 - np.dot(refracted1, n2_out) * n2_out
    if np.linalg.norm(parallel2) < 1e-9:
        return None
    parallel2 = normalize(parallel2)

    # Exiting ray direction: on the air side of n2_out
    refracted2 = np.sin(theta4) * parallel2 + np.cos(theta4) * n2_out
    refracted2 = normalize(refracted2)

    # Extend rays for visualization
    incident_start = entry_point - 3.0 * incident_dir
    exit_end = p2 + 4.5 * refracted2

    segments = [
        np.array([incident_start, entry_point]),
        np.array([entry_point, p2]),
        np.array([p2, exit_end])
    ]

    return segments, (apex, base_left, base_right), n_glass


def main():
    parser = argparse.ArgumentParser(description='Prism refraction and dispersion simulation')
    parser.add_argument('--no-display', action='store_true',
                        help='Do not open matplotlib window, only save PNG file')
    parser.add_argument('--output', type=str, default=None,
                        help='Custom output path (default: ../../attachments/visuals/prism_refraction_rayoptics.png)')
    args = parser.parse_args()

    wavelengths = {
        'Red (656 nm)': 656.3,
        'Yellow (589 nm)': 589.3,
        'Green (546 nm)': 546.1,
        'Blue (486 nm)': 486.1,
        'Violet (434 nm)': 434.0,
    }

    colors = {
        'Red (656 nm)': '#e41a1c',
        'Yellow (589 nm)': '#ff7f00',
        'Green (546 nm)': '#4daf4a',
        'Blue (486 nm)': '#377eb8',
        'Violet (434 nm)': '#984ea3',
    }

    # Incident angle relative to first surface normal.
    # For BK7 equilateral prism, ~40° avoids TIR and shows nice dispersion.
    incident_angle_deg = 40.0

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = '../../attachments/visuals/prism_refraction_rayoptics.png'

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    # ... (keep existing plotting code) ...

    vertices = None
    for i, (label, wl) in enumerate(wavelengths.items()):
        result = trace_prism_ray(wl, incident_angle_deg)
        if result is None:
            print(f"Trace failed for {label}")
            continue
        segments, vertices, n_glass = result
        for j, seg in enumerate(segments):
            # Only label the exiting ray segment to avoid duplicate legend entries
            show_label = (j == 2)
            ax.plot(seg[:, 0], seg[:, 1], color=colors[label], linewidth=2.2,
                    label=(f"{label}, n={n_glass:.4f}" if show_label else None))

    if vertices is None:
        raise RuntimeError("All ray traces failed")

    apex, base_left, base_right = vertices
    prism_x = [base_left[0], apex[0], base_right[0], base_left[0]]
    prism_y = [base_left[1], apex[1], base_right[1], base_left[1]]
    ax.fill(prism_x, prism_y, color='#a6cee3', alpha=0.35,
            edgecolor='#1f78b4', linewidth=2)

    # Annotations
    ax.annotate('Incident white light\n(parallel rays)', xy=(-3.8, 0.5), fontsize=10,
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax.annotate('Dispersed spectrum', xy=(5.0, -1.8), fontsize=10,
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    ax.set_aspect('equal')
    ax.set_xlim(-6, 8)
    ax.set_ylim(-3.5, 3.5)
    ax.set_title('Prism Refraction and Dispersion (N-BK7, opticalglass + Snell\'s law)',
                 fontsize=13)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.axis('off')

    output_path = args.output if args.output else '../../attachments/visuals/prism_refraction_rayoptics.png'
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    print(f"Saved figure to {output_path}")

    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)

    print("\nRefractive indices used (N-BK7):")
    for label, wl in wavelengths.items():
        glass = create_glass('N-BK7', 'Schott')
        n = glass.rindex(wl)
        print(f"  {label}: n = {n:.5f}")


if __name__ == '__main__':
    main()
