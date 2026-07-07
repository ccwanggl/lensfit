# CMOS Sensor Interactive Lab
# 主应用入口 — Streamlit 交互式教学工具
#
# 运行方式：
#   cd /path/to/.compute
#   streamlit run cmos_sensor_lab/app.py
#
# 对应知识库：OpticKnowledgeSpace/50-learning/Understanding CMOS Image Sensor.md

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# 导入核心模型
import sys
sys.path.insert(0, 'E:/DevSpace/lensfit/OpticKnowledgeSpace/.compute/cmos_sensor_lab')
from core import sensor, noise
from utils import plots

# ────────────────────────────────────────────
# 页面配置
# ────────────────────────────────────────────
st.set_page_config(
    page_title="CMOS Sensor Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────
# 自定义 CSS：让侧边栏更紧凑，图表区域更大
# ────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding: 2rem 3rem; }
    .sidebar .sidebar-content { padding: 1rem; }
    h1 { font-size: 2rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.5rem !important; margin-top: 1rem !important; }
    .stSlider { padding-bottom: 0.5rem; }
    .stMarkdown p { font-size: 0.95rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# 侧边栏：模块选择 + 全局参数
# ────────────────────────────────────────────
st.sidebar.title("🔬 CMOS Sensor Lab")
st.sidebar.markdown("---")

module = st.sidebar.radio(
    "选择模块",
    [
        "1. 光电转换链路",
        "2. 噪声模型与 SNR",
        "3. 动态范围与 WDR",
        "4. 曝光控制",
        "5. 图像伪影"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**使用说明**：
1. 在左侧选择模块
2. 调节参数滑块
3. 观察右侧图表实时变化
4. 点击「保存图表」可将结果导出

对应知识库：
`50-learning/Understanding CMOS Image Sensor.md`
""")

# ────────────────────────────────────────────
# 模块 1: 光电转换链路 (Photon → Electron → DN)
# ────────────────────────────────────────────
if module == "1. 光电转换链路":
    st.title("1. 光电转换链路")
    st.markdown(
        """
        **对应笔记**：1.2 光电转换、1.3 像点微观结构、3.6 灵敏度

        本模块展示 CMOS 传感器的完整光电转换过程：
        **光子 → 电子 → 增益放大 → ADC 量化 → DN**

        通过调节参数，理解：
        - 为什么增大增益不改变信噪比？
        - 为什么 ADC 位数不够会导致量化噪声？
        - 势阱满了会怎样？
        """
    )

    col_params, col_chart = st.columns([1, 2])

    with col_params:
        st.subheader("⚙️ 参数调节")

        qe = st.slider(
            "量子效率 QE",
            min_value=0.1, max_value=1.0, value=0.5, step=0.05,
            help="每个光子产生电子的概率。典型值：可见光 0.4-0.8，红外较低。"
        )

        gain = st.slider(
            "增益系数 g",
            min_value=0.5, max_value=10.0, value=1.0, step=0.5,
            help="1/g = 1 DN 对应的电子数。增益越大，1 DN 代表电子越少。"
        )

        adc_bits = st.slider(
            "ADC 位数",
            min_value=8, max_value=16, value=12, step=1,
            help="ADC 位数决定输出范围：8-bit=0-255，12-bit=0-4095，16-bit=0-65535。"
        )

        fwc = st.slider(
            "势阱容量 FWC (e⁻)",
            min_value=1000, max_value=100000, value=10000, step=1000,
            help="单个像素能容纳的最大电子数。FWC 越大，动态范围越高。"
        )

        exposure_time = st.slider(
            "曝光时间 (ms)",
            min_value=0.01, max_value=100.0, value=1.0, step=0.1,
            help="曝光时间越长，收集的光子越多，但运动模糊风险增加。"
        )

        st.markdown("---")
        st.markdown(
            f"""
            **当前参数解读**：
            - 饱和光子数：{sensor.get_saturation_photons(qe, fwc):.0f} photons
            - 1 DN 对应电子数：{sensor.get_quantization_step(gain):.2f} e⁻
            - 最大输出：{2**adc_bits - 1} DN
            """
        )

    with col_chart:
        # 生成响应曲线
        photons_range = np.linspace(0, sensor.get_saturation_photons(qe, fwc) * 1.5, 500)
        dn_values = sensor.generate_response_curve(
            photons_range, qe, gain, adc_bits, fwc
        )

        fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor=plots.COLORS['bg'])

        # 左图：响应曲线
        plots.plot_response_curve(
            axes[0], photons_range, dn_values,
            saturation_photons=sensor.get_saturation_photons(qe, fwc),
            title="输入-输出响应曲线"
        )

        # 右图：不同增益下的量化阶梯对比
        gains_compare = [0.5, 1.0, 2.0, 4.0]
        colors = [plots.COLORS['primary'], plots.COLORS['secondary'],
                  plots.COLORS['tertiary'], plots.COLORS['highlight']]
        for g, color in zip(gains_compare, colors):
            dn = sensor.generate_response_curve(photons_range, qe, g, adc_bits, fwc)
            axes[1].plot(photons_range, dn, linewidth=2, label=f'g={g}', color=color)
        axes[1].set_xlabel('入射光子数', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('DN 值', fontsize=12, fontweight='bold')
        axes[1].set_title(f"不同增益对比（{adc_bits}-bit ADC）", fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3, linestyle='--')
        axes[1].legend(loc='lower right', fontsize=10)
        axes[1].set_facecolor(plots.COLORS['bg'])

        plt.tight_layout()
        st.pyplot(fig)

        # 保存按钮
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        st.download_button(
            label="📥 保存图表",
            data=buf.getvalue(),
            file_name="response_curve.png",
            mime="image/png"
        )

    # 物理直觉区
    st.markdown("---")
    st.subheader("💡 物理直觉")

    with st.expander("为什么增大增益不改变信噪比？"):
        st.markdown(
            """
            增益同时放大信号和噪声。

            - 信号放大：$S_{out} = g \cdot S_{in}$
            - 散粒噪声放大：$\sigma_{out} = g \cdot \sigma_{in}$
            - 信噪比：$SNR = \frac{g \cdot S}{g \cdot \sigma} = \frac{S}{\sigma}$（不变）

            **结论**：增益只能改变信号的"强度"，不能改变信号的"质量"。
            要改善 SNR，必须增加光子数（更大的像素、更长的曝光、更强的光源）。
            """
        )

    with st.expander("为什么 ADC 位数不够会导致量化噪声？"):
        st.markdown(
            """
            ADC 将连续的模拟信号离散化为整数 DN。

            当 ADC 位数不足时（如 8-bit），
            相邻电子数可能被量化为同一个 DN，导致信息损失。

            例如：g=1，12-bit ADC 能区分 1 e⁻ 差异；
            但 8-bit ADC 只能区分约 40 e⁻ 差异（10000/255）。

            右图对比展示了不同增益下，低 ADC 位数时的"阶梯效应"。
            """
        )

    with st.expander("势阱满了会怎样？"):
        st.markdown(
            """
            当电子数超过 FWC（势阱容量）时，多余的电子会溢出：
            - **溢出到相邻像素**： blooming（光晕）
            - **沿列读出方向拖尾**： smear
            - **完全饱和**：DN 不再增加，变成"平头"（plateau）

            左图中的饱和点就是 FWC 的物理极限。
            """
        )


# ────────────────────────────────────────────
# 模块 2: 噪声模型与 SNR
# ────────────────────────────────────────────
elif module == "2. 噪声模型与 SNR":
    st.title("2. 噪声模型与 SNR")
    st.markdown(
        """
        **对应笔记**：3.3 噪声、3.4 信噪比

        本模块展示 CMOS 传感器的各种噪声源及其对 SNR 的影响。

        总噪声公式：$\\sigma_{eff} = \\sqrt{\\sigma_S^2 + \\sigma_D^2 + \\sigma_R^2}$
        """
    )

    col_params, col_chart = st.columns([1, 2])

    with col_params:
        st.subheader("⚙️ 参数调节")

        qe = st.slider(
            "量子效率 QE", 0.1, 1.0, 0.5, 0.05,
            help="影响信号电子数，从而影响散粒噪声。"
        )

        sigma_r = st.slider(
            "读出噪声 σ_R (e⁻)", 0.5, 20.0, 2.0, 0.5,
            help="读出电路引入的噪声。高端传感器可低至 0.5 e⁻，普通传感器 2-5 e⁻。"
        )

        dark_current = st.slider(
            "暗电流 D (e⁻)", 0.0, 50.0, 0.0, 1.0,
            help="无光时产生的电子数。温度每升高 6°C，暗电流约翻倍。"
        )

        temperature = st.slider(
            "温度 (°C)", -40, 60, 25, 5,
            help="仅用于展示温度对暗电流的影响趋势。"
        )

        fwc = st.slider(
            "势阱容量 FWC (e⁻)", 1000, 100000, 10000, 1000
        )

        st.markdown("---")

        # 计算当前设置下的噪声分解
        signal_e = fwc  # 用饱和电子数作为参考信号
        decomp = noise.generate_noise_decomposition(signal_e, dark_current, sigma_r)
        total = sum(decomp.values())

        st.markdown(
            f"""
            **饱和时噪声分解**（FWC={fwc} e⁻）：
            | 噪声类型 | σ² (e⁻²) | 占比 |
            |----------|----------|------|
            | 散粒噪声 | {decomp['散粒噪声']:.1f} | {decomp['散粒噪声']/total*100:.1f}% |
            | 暗电流噪声 | {decomp['暗电流噪声']:.1f} | {decomp['暗电流噪声']/total*100:.1f}% |
            | 读出噪声 | {decomp['读出噪声']:.1f} | {decomp['读出噪声']/total*100:.1f}% |

            **总噪声**：$\\sigma_{{eff}} = \\sqrt{{{total:.1f}}} \\approx \\sqrt{{{total:.0f}}} \\approx {np.sqrt(total):.1f}$ e⁻
            """
        )

    with col_chart:
        # 左图：SNR 曲线
        photon_range = np.logspace(1, 6, 500)  # 10 ~ 1,000,000 photons

        snr_25 = noise.generate_snr_curve(photon_range, qe, dark_current, sigma_r)
        # 模拟温度降低：暗电流减半（简化模型）
        snr_0 = noise.generate_snr_curve(photon_range, qe, dark_current * 0.5, sigma_r)
        snr_n25 = noise.generate_snr_curve(photon_range, qe, dark_current * 0.1, sigma_r)

        fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor=plots.COLORS['bg'])

        plots.plot_comparison(
            axes[0], photon_range,
            [snr_25, snr_0, snr_n25],
            ['25°C', '0°C', '-25°C'],
            title="SNR 随光子数变化（不同温度）",
            xlabel="入射光子数",
            ylabel="SNR (dB)"
        )
        axes[0].axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Acceptable (10 dB)')
        axes[0].axhline(y=30, color='orange', linestyle='--', alpha=0.5, label='Good (30 dB)')
        axes[0].axhline(y=40, color='green', linestyle='--', alpha=0.5, label='Excellent (40 dB)')
        axes[0].legend(loc='lower right', fontsize=9)

        # 右图：噪声分解饼图
        plots.plot_noise_decomposition(axes[1], decomp, title="噪声成分占比（饱和时）")

        plt.tight_layout()
        st.pyplot(fig)

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        st.download_button(
            label="📥 保存图表",
            data=buf.getvalue(),
            file_name="noise_snr.png",
            mime="image/png"
        )

    # 模拟拍摄
    st.markdown("---")
    st.subheader("📷 模拟拍摄")

    st.markdown(
        """
        下方模拟一个均匀光照场景的 1000 帧拍摄，
        展示噪声的实际分布。
        """
    )

    col_img, col_hist = st.columns(2)

    with col_img:
        # 生成均匀光子图像
        photon_image = np.full((128, 128), 1000.0)  # 1000 photons/pixel
        noisy_image = noise.add_noise_to_image(
            photon_image, qe, dark_current, sigma_r, fwc
        )
        dn_image = sensor.electron_to_dn(noisy_image, gain=1.0, adc_bits=12, fwc=fwc)

        fig, ax = plt.subplots(figsize=(6, 5), facecolor=plots.COLORS['bg'])
        plots.plot_2d_image(ax, dn_image, title="含噪声图像（模拟）", cmap='gray')
        plt.tight_layout()
        st.pyplot(fig)

    with col_hist:
        fig, ax = plt.subplots(figsize=(6, 5), facecolor=plots.COLORS['bg'])
        plots.plot_histogram(ax, dn_image, title="DN 分布直方图", xlabel="DN 值")
        plt.tight_layout()
        st.pyplot(fig)

    # 物理直觉
    st.markdown("---")
    st.subheader("💡 物理直觉")

    with st.expander("暗光时读出噪声主导，强光时散粒噪声主导"):
        st.markdown(
            """
            - **暗光**：光子数少，散粒噪声 $\\sigma_S = \\sqrt{S}$ 很小。
              此时读出噪声 $\\sigma_R$（固定值，如 2 e⁻）占主导。

            - **强光**：光子数多，$\\sigma_S = \\sqrt{10000} = 100$ e⁻，
              远大于读出噪声。此时散粒噪声占主导。

            左图展示了 SNR 曲线：
            - 低光子数区域，SNR 受读出噪声限制（曲线较平缓）
            - 高光子数区域，SNR 受散粒噪声限制（$SNR \\propto \\sqrt{N}$）
            """
        )

    with st.expander("温度降低为什么能改善噪声？"):
        st.markdown(
            """
            暗电流与温度的关系近似为：
            $D(T) \\propto T^{1.5} \\cdot e^{-E_g / 2kT}$

            温度每降低约 6°C，暗电流减半。

            对于低温应用（如天文摄影），
            使用制冷传感器可将暗电流降至几乎为零。
            """
        )


# ────────────────────────────────────────────
# 模块 3-5: 占位（后续开发）
# ────────────────────────────────────────────
else:
    st.title(f"{module}")
    st.info(
        """
        🚧 该模块正在开发中...

        当前可用模块：
        - **1. 光电转换链路**
        - **2. 噪声模型与 SNR**

        请从左侧选择已完成的模块。
        """
    )

# ────────────────────────────────────────────
# 页脚
# ────────────────────────────────────────────
st.markdown("---")
st.caption(
    "CMOS Sensor Interactive Lab | 基于 LensFit 知识库 | "
    "[对应笔记](https://github.com/your-repo/blob/main/50-learning/Understanding%20CMOS%20Image%20Sensor.md)"
)
