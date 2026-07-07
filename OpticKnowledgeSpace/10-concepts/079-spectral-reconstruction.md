---
id: concept.spectral-reconstruction
title: 光谱重建
type: concept
domains: [spectroscopy, on-chip-multispectral, computation]
status: reviewed
aliases:
  - spectral-reconstruction
  - 光谱重建
  - 光谱反演
  - spectral-inversion
---

# 光谱重建

## 定义

光谱重建（Spectral Reconstruction）是从传感器测得的**编码或欠采样信号**中恢复出目标**真实光谱**的过程。它是片上多光谱、高光谱和计算光谱仪的核心算法步骤，本质上是一个**逆问题求解**。

在片上系统中，由于通道数远小于光谱维度，重建通常需要结合系统的前向模型、先验知识和正则化约束。

---

## 直观理解

想象你通过几块有色玻璃看一个场景，每块玻璃只允许某些波长的光通过。你只看到几块“染色”后的图像，而光谱重建就是根据这些有限信息和每块玻璃的颜色特性，反推出每个像素原本完整的光谱曲线。

如果玻璃数量足够多且颜色差异明显，重建相对容易；如果只有几块玻璃，就需要借助先验知识（例如光谱通常平滑、非负、稀疏等）来约束解空间。

---

## 数学模型

片上光谱系统的前向模型通常写作：

$$
y = Hx + n
$$

- **$x \in \mathbb{R}^{N_\lambda}$** —— 真实光谱（每个像素 $N_\lambda$ 个波长采样点）
- **$H \in \mathbb{R}^{M \times N_\lambda}$** —— 系统响应/编码矩阵（$M$ 个通道）
- **$y \in \mathbb{R}^{M}$** —— 传感器测得的 $M$ 个通道信号
- **$n$** —— 噪声（光子噪声、读出噪声、暗电流等）

目标是求：

$$
\hat{x} = \arg\min_x \| y - Hx \|^2 + \lambda R(x)
$$

- **$R(x)$** —— 正则化项，编码先验知识
- **$\lambda$** —— 正则化权重

---

## 常用方法

| 方法 | 核心思想 | 适用场景 |
| --- | --- | --- |
| 最小二乘 / 伪逆 | 直接求 $H^+ y$ | 通道数 ≥ 波长点数、噪声小 |
| Tikhonov 正则化 | 增加平滑性惩罚 | 欠定但光谱平滑 |
| 非负最小二乘 | 光谱强度不能为负 | 大多数物理光谱重建 |
| 稀疏重建 | 光谱在某基底下稀疏 | 压缩感知光谱仪 |
| 全变分（TV） | 保持空间/光谱边缘 | 存在空间-光谱混叠 |
| 深度学习 | 用神经网络学习 $y \to x$ 映射 | 数据充足、需要快速重建 |
| 物理约束网络 | 把前向模型嵌入网络训练 | 数据有限但需要物理一致性 |
| 算法-光学联合优化 | 同时优化 $H$ 和重建网络 | 端到端设计超表面/滤光片系统 |

---

## 评估指标

| 指标 | 含义 | 说明 |
| --- | --- | --- |
| RMSE | 重建光谱与真实光谱的均方根误差 | 越小越好，但对尺度敏感 |
| SAM | 光谱角映射，衡量光谱形状差异 | 对幅度不敏感，常用于高光谱 |
| PSNR | 峰值信噪比 | 常用于图像级重建质量 |
| SSIM | 结构相似性 | 评估空间结构保持 |
| 波长精度 | 重建峰位与真实峰位偏差 | 对气体/材料识别很重要 |

---

## 关键关系

- 相关概念：[[./072-multispectral-imaging|多光谱成像]]
- 相关概念：[[./073-hyperspectral-imaging|高光谱成像]]
- 相关概念：[[./076-multispectral-filter-array|多光谱滤光片阵列]]
- 相关概念：[[./075-snapshot-spectral-imaging|快照式光谱成像]]
- 相关概念：[[./078-metasurface|超表面]]（计算光谱成像的编码结构）
- 相关领域：[[../30-domains/005-on-chip-multispectral|片上多光谱成像]]
- 相关文献：[[../80-sources/009-on-chip-multispectral-literature|片上多光谱/高光谱文献雷达]]

---

## 常见误区

1. **重建 = 插值**：插值只在已有采样点之间估计，而重建是从完全不同的编码测量中恢复高维光谱，属于逆问题。
2. **通道越多重建越好**：关键在于通道响应的**低相关性**和**对目标光谱的覆盖**，而不是单纯数量。
3. **深度学习一定优于传统方法**：在训练数据不足或分布偏移时，传统正则化方法可能更稳健。
4. **忽略噪声模型**：光子噪声、读出噪声、暗电流都会显著影响重建精度，必须在模型中考虑。
5. **标定矩阵 $H$ 一成不变**：温度、老化、入射角变化都会改变 $H$，需要现场标定或在线更新。

---

## 教材参考

- [[../80-sources/002-hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/003-saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]]：适合核对探测器、光与物质相互作用、光子学器件和现代光学系统。
- [[../80-sources/009-on-chip-multispectral-literature|片上多光谱/高光谱文献雷达]]：适合核对超表面、滤波阵列、快照式光谱成像和光谱重建等前沿主题。
- [[../80-sources/001-Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 来源

- Bioucas-Dias et al., "Hyperspectral Remote Sensing Data Analysis and Future Challenges", *IEEE GRSM*, 2013
- Wang et al., "Computational Spectrometers: From Micro to Macro", *eLight*, 2025
- 片上多光谱/高光谱文献清单中的重建/计算光谱论文
