#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
折射率-波长曲线可视化 (refractive-index-curve)
概念: 折射率 (refractive-index)

使用 rayoptics 的 opticalglass 库获取常见光学玻璃的色散数据，
绘制折射率 n 随波长 λ 变化的曲线，展示正常色散特性：
短波长（蓝光）折射率大于长波长（红光），这是棱镜分光和透镜色差的物理根源。
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from opticalglass.glassfactory import create_glass


def main():
    # 命令行参数解析，支持 --no-display 用于无头环境（如 CI/自动化）
    parser = argparse.ArgumentParser(description='折射率-波长曲线可视化')
    parser.add_argument('--no-display', action='store_true',
                        help='不显示图像窗口，仅保存 PNG 文件')
    args = parser.parse_args()

    # 可见光波长范围: 400nm (紫光) 到 700nm (红光)
    # 取 300 个采样点以获得平滑的色散曲线
    wavelengths = np.linspace(400, 700, 300)

    # 定义要对比的三种典型光学玻璃
    # N-BK7: 最常用的冕牌玻璃，低色散
    # SF10: 重火石玻璃，高色散，高折射率
    # F2: 火石玻璃，中等色散
    glasses = {
        'N-BK7': {'factory': 'Schott', 'color': '#1f77b4', 'linestyle': '-'},
        'SF10':  {'factory': 'Schott', 'color': '#d62728', 'linestyle': '-'},
        'F2':    {'factory': 'Schott', 'color': '#2ca02c', 'linestyle': '-'},
    }

    # 创建 matplotlib 图形，高 DPI 确保输出清晰
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    # 遍历每种玻璃，从 opticalglass 数据库获取折射率并绘制曲线
    for glass_name, info in glasses.items():
        try:
            # 通过 glassfactory 创建玻璃实例
            glass = create_glass(glass_name, info['factory'])
            # 对每一个波长计算折射率（色散函数的内插）
            n_values = np.array([glass.rindex(wl) for wl in wavelengths])
            ax.plot(wavelengths, n_values, color=info['color'],
                    linestyle=info['linestyle'], linewidth=2.2,
                    label=f'{glass_name} ({info["factory"]})')
        except Exception as e:
            print(f"警告: 无法获取 {glass_name} 数据: {e}")
            continue

    # 标注关键光谱线位置——夫琅禾费谱线，用于定义阿贝数
    # C线: 656.3nm (氢的红线)，d线: 587.6nm (氦的黄线)，F线: 486.1nm (氢的蓝线)
    spectral_lines = [
        {'wl': 656.3, 'label': 'C线 656.3nm', 'color': '#e41a1c'},  # 红色
        {'wl': 587.6, 'label': 'd线 587.6nm', 'color': '#ff7f00'},  # 黄色/橙色
        {'wl': 486.1, 'label': 'F线 486.1nm', 'color': '#377eb8'},  # 蓝色
    ]

    # 在图上绘制垂直虚线并标注三条谱线
    for line in spectral_lines:
        ax.axvline(x=line['wl'], color=line['color'], linestyle='--',
                   alpha=0.6, linewidth=1.2)
        ax.text(line['wl'], ax.get_ylim()[1], line['label'],
                color=line['color'], fontsize=9, ha='center', va='bottom',
                rotation=90)

    # 坐标轴与标题设置
    ax.set_xlabel('波长 λ (nm)', fontsize=12)
    ax.set_ylabel('折射率 n', fontsize=12)
    ax.set_title(
        '光学玻璃折射率色散曲线 (n–λ 曲线)\n'
        '正常色散: 短波长(蓝光)折射率大于长波长(红光)',
        fontsize=13
    )
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(400, 700)
    ax.set_ylim(1.45, 1.75)

    # 添加物理意义说明文本框
    ax.text(
        0.02, 0.15,
        '物理意义:\n'
        '• 正常色散: n 随 λ 增大而单调减小\n'
        '• 蓝光(短波)在玻璃中偏折更强烈\n'
        '• 这是棱镜分光和透镜轴向色差的根源',
        transform=ax.transAxes, fontsize=9,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.3)
    )

    plt.tight_layout()

    # 保存图像到指定输出路径
    output_path = '../../attachments/visuals/refractive_index_curve.png'
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', dpi=150)
    print(f"Saved figure to {output_path}")

    # 根据 --no-display 参数决定是否弹窗显示
    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    main()
