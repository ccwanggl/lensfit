#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F值可视化：不同光圈下的入瞳光锥角度对比 (f-number-cone)
概念: F值 (f-number)

展示同一透镜（焦距 f=50mm）在 F/2.8、F/5.6、F/11 三种光圈下的
入瞳光锥角度对比。

物理要点：
- F# = f / D，其中 D 为入瞳直径（有效孔径）
- 光锥半角 α = arctan(1 / (2 × F#))
- F# 越大 → 入瞳越小 → 光锥越窄 → 景深越大 → 通光量越小
- 光锥的宽窄直接决定了到达像面的光线角度范围
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from oks_mpl import setup_fonts


def main():
    setup_fonts()
    parser = argparse.ArgumentParser(description='F值入瞳光锥角度对比可视化')
    parser.add_argument('--no-display', action='store_true',
                        help='不显示图像窗口，仅保存 PNG 文件')
    args = parser.parse_args()

    # 透镜参数
    f = 50.0  # 焦距 (mm)，三种光锥共用同一焦距

    # 定义三种 F# 值及其绘图属性
    f_numbers = [
        {'F': 2.8,  'color': '#e41a1c', 'y_offset': 0},    # 红色：大光圈，宽光锥
        {'F': 5.6,  'color': '#377eb8', 'y_offset': -22},   # 蓝色：中等光圈
        {'F': 11.0, 'color': '#4daf4a', 'y_offset': -44},  # 绿色：小光圈，窄光锥
    ]

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    for info in f_numbers:
        F = info['F']
        color = info['color']
        y_offset = info['y_offset']

        # 入瞳直径 = 焦距 / F#，这是 F# 的定义
        D = f / F
        half_D = D / 2.0

        # 光锥半角 α：tan(α) = (D/2) / f = 1 / (2×F#)
        alpha_rad = np.arctan(1.0 / (2.0 * F))
        alpha_deg = np.degrees(alpha_rad)
        full_cone_deg = 2.0 * alpha_deg

        # 绘制光锥：从入瞳（左侧 x=0）到焦点（右侧 x=f）
        # 上边缘光线：从入瞳上边缘到焦点
        ax.plot([0, f], [y_offset + half_D, y_offset],
                '-', color=color, linewidth=2.0)
        # 下边缘光线：从入瞳下边缘到焦点
        ax.plot([0, f], [y_offset - half_D, y_offset],
                '-', color=color, linewidth=2.0)

        # 填充光锥内部区域，增强视觉效果
        cone_x = np.array([0, f, f, 0])
        cone_y = np.array([y_offset + half_D, y_offset,
                           y_offset, y_offset - half_D])
        ax.fill(cone_x, cone_y, color=color, alpha=0.12)

        # 绘制入瞳孔径（左侧粗线表示孔径光阑）
        ax.plot([0, 0], [y_offset - half_D, y_offset + half_D],
                '-', color=color, linewidth=3.5, solid_capstyle='round')

        # 在焦点处绘制标记点
        ax.plot(f, y_offset, 'o', color=color, markersize=7)

        # 标注 F# 值、入瞳直径和锥角信息
        ax.text(
            f + 5, y_offset,
            f'F/{F:.1f}\n'
            f'入瞳 D = {D:.2f} mm\n'
            f'半角 α = {alpha_deg:.2f}°\n'
            f'全锥角 = {full_cone_deg:.2f}°',
            fontsize=10, color=color, va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                     alpha=0.9, edgecolor=color, linewidth=1.5)
        )

        # 在入瞳左侧标注入瞳直径数值
        ax.text(
            -2, y_offset + half_D + 1.2,
            f'D = {D:.2f} mm',
            fontsize=8, color=color, ha='right', va='bottom'
        )

    # 绘制三条光锥各自的光轴参考线
    for info in f_numbers:
        ax.axhline(y=info['y_offset'], color='gray', linestyle='--',
                   linewidth=0.7, alpha=0.4)
        # 标注光轴
        ax.text(-12, info['y_offset'] + 0.5, '光轴',
                fontsize=8, color='gray', va='bottom')

    # 添加透镜焦距标注（在 x=0 处）
    ax.text(-12, 6, f'透镜焦距\nf = {f:.0f} mm',
            fontsize=10, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.8))

    # 绘制一个示意透镜轮廓（简化表示）
    lens_y = np.linspace(-10, 10, 100)
    lens_R = 30.0
    lens_x = -lens_R + np.sqrt(lens_R**2 - lens_y**2)
    ax.plot(lens_x, lens_y, 'k-', linewidth=1.5, alpha=0.6)
    ax.plot(lens_x, -lens_y, 'k-', linewidth=1.5, alpha=0.6)
    ax.fill_betweenx(lens_y, lens_x, -2, color='lightgray', alpha=0.3)

    # 物理关系说明文本框
    ax.text(
        0.5, 0.02,
        '核心关系:  F# = f / D    |    半角 α = arctan( 1 / (2×F#) )\n'
        'F# 越大  →  入瞳 D 越小  →  光锥越窄  →  景深越大  →  通光量越小',
        transform=ax.transAxes, fontsize=10, ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.4)
    )

    # 坐标轴和标题设置
    ax.set_xlim(-18, 82)
    ax.set_ylim(-55, 12)
    ax.set_xlabel('光轴方向距离 (mm)', fontsize=12)
    ax.set_ylabel('横向偏移 (mm)', fontsize=12)
    ax.set_title(
        f'F值对比: 同一透镜 (f = {f:.0f} mm) 在不同光圈下的入瞳光锥\n'
        f'光锥越窄 → F# 越大 → 景深越大 → 通光量越小',
        fontsize=13
    )
    ax.grid(True, alpha=0.2)
    ax.set_aspect('auto')  # 不强制等比例，让 x/y 轴自由缩放

    plt.tight_layout()

    # 保存图像
    output_path = '../../attachments/visuals/f_number_cone.png'
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', dpi=150)
    print(f"Saved figure to {output_path}")

    # 根据 --no-display 参数决定是否弹窗显示
    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    main()
