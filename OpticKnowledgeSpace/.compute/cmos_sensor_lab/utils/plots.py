# 统一绘图工具
# 提供统一的 matplotlib 风格，确保所有模块的图表一致

import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体（Windows 优先 SimHei，Linux 优先 DejaVu）
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 统一配色方案：低饱和度、暖色调
COLORS = {
    'primary': '#2E7D32',      # 深绿（主色）
    'secondary': '#D84315',    # 深橙（对比色）
    'tertiary': '#1565C0',     # 深蓝
    'highlight': '#F9A825',    # 高亮黄
    'neutral': '#757575',      # 中性灰
    'light': '#E8E8E8',        # 浅灰
    'bg': '#FAFAFA'            # 背景色
}


def setup_figure(figsize=(10, 6), dpi=100):
    """创建标准尺寸的图形，返回 Figure 对象"""
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=COLORS['bg'])
    return fig


def plot_response_curve(ax, photons, dn, saturation_photons=None, title="响应曲线"):
    """
    绘制传感器输入-输出响应曲线。

    展示三个区域：
    - 线性区：DN 与光子数成正比
    - 饱和区：DN 不再增加（ plateau ）
    - 截止区：低光子数时的读出噪声淹没
    """
    ax.plot(photons, dn, color=COLORS['primary'], linewidth=2.5, label='响应曲线')

    # 标注饱和点
    if saturation_photons is not None and saturation_photons < max(photons):
        ax.axvline(x=saturation_photons, color=COLORS['secondary'],
                   linestyle='--', linewidth=1.5, alpha=0.7, label='饱和点')
        ax.axhline(y=max(dn), color=COLORS['secondary'],
                   linestyle='--', linewidth=1.5, alpha=0.7)

    ax.set_xlabel('入射光子数', fontsize=12, fontweight='bold')
    ax.set_ylabel('DN 值', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0, max(photons))
    ax.set_ylim(0, max(dn) * 1.1)
    ax.legend(loc='lower right', fontsize=10)
    ax.set_facecolor(COLORS['bg'])


def plot_snr_curve(ax, photons, snr_db, title="SNR 曲线", thresholds=None):
    """
    绘制 SNR 随光子数变化的曲线。

    可选标注关键阈值：
    - SNR = 10 dB（可接受）
    - SNR = 30 dB（良好）
    - SNR = 40 dB（优秀）
    """
    ax.semilogx(photons, snr_db, color=COLORS['primary'], linewidth=2.5, label='SNR')

    if thresholds:
        for val, label, color in thresholds:
            ax.axhline(y=val, color=color, linestyle='--',
                       linewidth=1.5, alpha=0.6, label=label)

    ax.set_xlabel('入射光子数', fontsize=12, fontweight='bold')
    ax.set_ylabel('SNR (dB)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', which='both')
    ax.set_xlim(min(photons), max(photons))
    ax.set_ylim(0, max(snr_db) * 1.1)
    ax.legend(loc='lower right', fontsize=10)
    ax.set_facecolor(COLORS['bg'])


def plot_noise_decomposition(ax, components, title="噪声分解"):
    """
    绘制噪声分解饼图。

    components: dict，如 {'散粒噪声': 100, '读出噪声': 25, '暗电流噪声': 4}
    """
    labels = list(components.keys())
    values = list(components.values())
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['tertiary']]

    # 只显示非零项
    nonzero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not nonzero:
        ax.text(0.5, 0.5, '无噪声数据', ha='center', va='center', fontsize=14)
        return

    labels, values, colors = zip(*nonzero)

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors[:len(values)],
        autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 11}
    )
    ax.set_title(title, fontsize=14, fontweight='bold')


def plot_2d_image(ax, image, title="图像", cmap='gray', vmin=None, vmax=None):
    """绘制二维图像"""
    im = ax.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def plot_histogram(ax, data, bins=50, title="直方图", xlabel="DN 值"):
    """绘制 DN 值分布直方图"""
    ax.hist(data.flatten(), bins=bins, color=COLORS['primary'],
            alpha=0.7, edgecolor='white')
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel('频数', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor(COLORS['bg'])


def plot_comparison(ax, x, y_list, labels, title="对比曲线", xlabel="X", ylabel="Y"):
    """绘制多条曲线对比"""
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['tertiary']]
    for y, label, color in zip(y_list, labels, colors):
        ax.plot(x, y, linewidth=2.5, label=label, color=color)
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=10)
    ax.set_facecolor(COLORS['bg'])


def save_and_show(fig, save_path=None, show=True):
    """
    保存和/或显示图形。

    如果 save_path 不为 None，保存到指定路径。
    如果 show=True，调用 plt.show()。
    """
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', facecolor=fig.get_facecolor())
        print(f"Saved: {save_path}")
    if show:
        plt.show()
