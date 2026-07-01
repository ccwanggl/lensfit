#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
焦距可视化：双凸透镜平行光线追迹 (focal-length-trace)
概念: 焦距 (focal-length)

使用 rayoptics 的 opticalglass 库获取 N-BK7 折射率，
构建双凸透镜模型（R=±50mm, d=5mm, D=25mm），
追迹 5 条不同入射高度的子午光线，展示它们汇聚到后焦点的过程。

物理要点：
- 平行于光轴的入射光线经透镜折射后汇聚于后焦点
- 焦距 f 衡量透镜的会聚能力，f 越小会聚能力越强
- 实际光线由于球差不会完美汇聚于一点，近轴近似下焦点唯一
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from opticalglass.glassfactory import create_glass


def trace_paraxial_ray(h, n, R1, R2, d, focal_x):
    """
    近轴光线追迹：计算平行于光轴、入射高度为 h 的光线通过厚透镜后的传播路径。

    参数:
        h: 入射光线高度 (mm)，相对于光轴
        n: 透镜材料折射率（来自 opticalglass）
        R1: 第一面曲率半径 (mm)，凸向物方为正值
        R2: 第二面曲率半径 (mm)，凸向像方为负值
        d: 透镜中心厚度 (mm)
        focal_x: 后焦点 x 坐标 (mm)，用于统一出射光线终点

    返回:
        (x_in, y_in), (x_mid, y_mid), (x_out, y_out): 三段光线的坐标数组
    """
    # 第一段：入射光线，从左侧远处平行入射到第一面顶点 (x=0)
    x_in = np.array([-30, 0])
    y_in = np.array([h, h])

    # 近轴折射公式：n' * u' = n * u - y * (n' - n) / R
    # 第一面：空气(n=1) -> 玻璃(n')
    # 入射角 u = 0（平行光），高度 y = h
    u1_prime = -h * (n - 1.0) / (n * R1)

    # 光线在透镜内传播距离 d 后的高度
    y_mid = h + u1_prime * d
    x_mid = np.array([0, d])
    y_mid_arr = np.array([h, y_mid])

    # 第二面：玻璃(n) -> 空气(n'=1)
    u2_prime = (n * u1_prime - y_mid * (1.0 - n) / R2)

    # 第三段：出射光线，从第二面 (x=d) 到焦点后一段 (x=focal_x+10)
    # 在近轴近似下，光线经过焦点时 y=0
    x_out = np.array([d, focal_x + 10])
    y_out_end = y_mid + u2_prime * (focal_x + 10 - d)
    y_out = np.array([y_mid, y_out_end])

    return (x_in, y_in), (x_mid, y_mid_arr), (x_out, y_out)


def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='双凸透镜焦距光线追迹可视化')
    parser.add_argument('--no-display', action='store_true',
                        help='不显示图像窗口，仅保存 PNG 文件')
    args = parser.parse_args()

    # ========== 透镜几何与材料参数 ==========
    R1 = 50.0         # 第一面曲率半径 (mm)，凸向物方，曲率中心在 +x 方向
    R2 = -50.0        # 第二面曲率半径 (mm)，凸向像方，曲率中心在 -x 方向
    d = 5.0           # 透镜中心厚度 (mm)
    diameter = 25.0   # 透镜通光口径 (mm)
    max_h = diameter / 2.0  # 最大半口径 = 12.5 mm

    # 使用 rayoptics opticalglass 获取 N-BK7 在 d 线 (587.6nm) 的折射率
    glass = create_glass('N-BK7', 'Schott')
    n_d = glass.rindex(587.6)
    print(f"N-BK7 在 d 线 (587.6nm) 的折射率: n_d = {n_d:.4f}")

    # 厚透镜焦距计算（透镜制造者公式）
    # 1/f = (n-1) * [1/R1 - 1/R2 + (n-1)*d / (n*R1*R2)]
    inv_f = (n_d - 1.0) * (1.0 / R1 - 1.0 / R2
                          + (n_d - 1.0) * d / (n_d * R1 * R2))
    f_eff = 1.0 / inv_f
    print(f"透镜有效焦距 EFL ≈ {f_eff:.2f} mm")

    # 计算后焦点位置（从第一面顶点起算的 x 坐标），用于统一出射光线
    # 先用单位高度光线的近轴追迹求得精确后焦距
    u1_ref = -(n_d - 1.0) / (n_d * R1)          # 单位高度的第一面折射角
    y_mid_ref = 1.0 + u1_ref * d                # 第二面处高度
    u2_ref = (n_d * u1_ref - y_mid_ref * (1.0 - n_d) / R2)  # 出射角
    bfl = -y_mid_ref / u2_ref                   # 后焦距（从第二面到焦点）
    focal_x = d + bfl                           # 焦点从第一面顶点起的 x 坐标
    print(f"后焦点位置 (从第一面起): {focal_x:.2f} mm")

    # ========== 创建图形 ==========
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

    # 绘制透镜轮廓：使用球面方程精确计算截面
    y_lens = np.linspace(-max_h, max_h, 200)

    # 第一面：球心在 (-R1, 0) = (-50, 0)，半径 R1=50
    # 球面方程: (x + R1)^2 + y^2 = R1^2  =>  x = -R1 + sqrt(R1^2 - y^2)
    x1_surf = -R1 + np.sqrt(R1**2 - y_lens**2)

    # 第二面：顶点在 x=d=5，R2=-50，曲率中心在 x = d + R2 = -45
    # 球面方程: (x - (d+R2))^2 + y^2 = R2^2  =>  x = (d+R2) + sqrt(R2^2 - y^2)
    x2_surf = (d + R2) + np.sqrt(R2**2 - y_lens**2)

    # 填充透镜区域并绘制边界
    ax.fill_betweenx(y_lens, x1_surf, x2_surf, color='#a6cee3', alpha=0.35, edgecolor='none')
    ax.plot(x1_surf, y_lens, 'b-', linewidth=1.5, label='透镜表面')
    ax.plot(x2_surf, y_lens, 'b-', linewidth=1.5)

    # 绘制光轴（贯穿整个系统的中心线）
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)

    # 追迹 5 条不同入射高度的子午光线
    num_rays = 5
    heights = np.linspace(0, max_h, num_rays)
    colors = ['#e41a1c', '#ff7f00', '#4daf4a', '#377eb8', '#984ea3']

    for i, h in enumerate(heights):
        seg_in, seg_mid, seg_out = trace_paraxial_ray(h, n_d, R1, R2, d, focal_x)

        # 入射段：用虚线表示尚未到达透镜的平行光
        ax.plot(seg_in[0], seg_in[1], '--', color=colors[i], linewidth=1.2, alpha=0.7)
        # 透镜内段：实线表示在玻璃中的传播
        ax.plot(seg_mid[0], seg_mid[1], '-', color=colors[i], linewidth=1.8)
        # 出射段：实线表示折射后向焦点汇聚
        ax.plot(seg_out[0], seg_out[1], '-', color=colors[i], linewidth=1.5,
                label=f'h = {h:.1f} mm')

    # 标注焦点位置（所有近轴光线理论上的汇聚点）
    ax.axvline(x=focal_x, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.plot(focal_x, 0, 'ro', markersize=8, zorder=5)
    ax.annotate(
        f'后焦点 F\n(EFL ≈ {f_eff:.1f} mm)',
        xy=(focal_x, 0), xytext=(focal_x + 8, 4),
        fontsize=10, color='red',
        arrowprops=dict(arrowstyle='->', color='red', lw=1.2),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='red')
    )

    # 标注光轴
    ax.annotate('光轴', xy=(-25, 0.8), fontsize=10, color='gray', va='bottom')

    # 标注透镜后表面（第二面）的位置
    ax.axvline(x=d, color='blue', linestyle='-.', linewidth=0.8, alpha=0.4)
    ax.text(d + 0.5, -15, f'第二面\nx={d:.0f}mm', fontsize=8, color='blue', va='top')

    # 设置坐标范围和比例
    ax.set_xlim(-35, 85)
    ax.set_ylim(-18, 18)
    ax.set_aspect('equal')
    ax.set_xlabel('光轴方向距离 (mm)', fontsize=12)
    ax.set_ylabel('子午方向高度 (mm)', fontsize=12)
    ax.set_title(
        '双凸透镜平行光线追迹 (N-BK7, R₁=+50mm, R₂=−50mm, d=5mm, D=25mm)\n'
        '展示不同入射高度的子午光线汇聚到后焦点——近轴光线追迹',
        fontsize=13
    )
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)

    # 添加透镜参数说明框
    ax.text(
        0.02, 0.98,
        f'透镜参数:\n'
        f'  材料: N-BK7, n_d = {n_d:.4f}\n'
        f'  R₁ = +{R1:.0f} mm  (凸向物方)\n'
        f'  R₂ = {R2:.0f} mm  (凸向像方)\n'
        f'  厚度 d = {d:.0f} mm, 口径 D = {diameter:.0f} mm\n'
        f'  有效焦距 EFL ≈ {f_eff:.1f} mm\n'
        f'  后焦点 (从第一面) ≈ {focal_x:.1f} mm',
        transform=ax.transAxes, fontsize=9,
        verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8)
    )

    plt.tight_layout()

    # 保存图像
    output_path = '../../attachments/visuals/focal_length_trace.png'
    plt.savefig(output_path, bbox_inches='tight', facecolor='white', dpi=150)
    print(f"Saved figure to {output_path}")

    # 根据参数决定是否弹窗显示
    if not args.no_display:
        plt.show()
    else:
        plt.close(fig)


if __name__ == '__main__':
    main()
