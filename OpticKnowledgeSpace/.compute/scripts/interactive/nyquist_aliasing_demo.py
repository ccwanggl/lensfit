"""
Nyquist sampling and aliasing visualization.

Shows a sine wave sampled at different rates to illustrate:
- Proper sampling (fs > 2*f_signal)
- Critical sampling (fs = 2*f_signal)
- Undersampling / aliasing (fs < 2*f_signal)
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from oks_mpl import setup_fonts


def main():
    setup_fonts()
    parser = argparse.ArgumentParser(description='奈奎斯特采样与混叠可视化')
    parser.add_argument('--no-display', action='store_true',
                        help='不显示图像窗口，仅保存 PNG 文件')
    args = parser.parse_args()

    # Continuous signal
    f_signal = 5.0  # Hz
    t = np.linspace(0, 1, 1000)
    y = np.sin(2 * np.pi * f_signal * t)

    # Sampling rates
    cases = [
        {'fs': 20.0, 'title': '过采样：fs = 4 f信号（采样率 20 Hz）',
         'color': '#4daf4a', 'label': 'fs = 20 Hz'},
        {'fs': 10.0, 'title': '临界采样：fs = 2 f信号（采样率 10 Hz）',
         'color': '#ff7f00', 'label': 'fs = 10 Hz'},
        {'fs': 8.0, 'title': '欠采样：fs = 1.6 f信号（采样率 8 Hz）——出现混叠',
         'color': '#e41a1c', 'label': 'fs = 8 Hz'},
    ]

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), dpi=150)

    for ax, case in zip(axes, cases):
        fs = case['fs']
        ts = np.arange(0, 1 + 1/fs, 1/fs)
        ys = np.sin(2 * np.pi * f_signal * ts)

        ax.plot(t, y, 'b-', linewidth=1.5, alpha=0.4, label=f'连续信号 {f_signal} Hz')
        ax.stem(ts, ys, linefmt=case['color'], markerfmt='o', basefmt=' ',
                label=case['label'])
        ax.plot(ts, ys, 'o', color=case['color'], markersize=6)

        # Reconstruction attempt: zero-order hold
        for i in range(len(ts) - 1):
            ax.plot([ts[i], ts[i+1]], [ys[i], ys[i]], '--', color=case['color'],
                    alpha=0.5, linewidth=1)

        ax.set_title(case['title'])
        ax.set_xlabel('时间 t (s)')
        ax.set_ylabel('幅度')
        ax.set_xlim([0, 1])
        ax.set_ylim([-1.3, 1.3])
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)

    # Add Nyquist frequency annotation
    fig.text(
        0.5, 0.005,
        f'奈奎斯特定理：要无失真恢复频率为 f 的信号，采样率 fs 必须 ≥ 2f。\n'
        f'本例中信号频率 = {f_signal} Hz，因此最低采样率为 10 Hz。',
        ha='center', fontsize=11,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.4)
    )

    plt.tight_layout(rect=[0, 0.03, 1, 1])

    output_path = '../../../attachments/visuals/nyquist_aliasing_demo.png'
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', dpi=150)
    print(f'Saved figure to {output_path}')

    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    main()
