---
id: formula.strehl-ratio
title: Strehl 比公式
type: formula
domains: [optical-design]
status: draft
aliases:
  - strehl-ratio-formula
  - Strehl比公式
---

# Strehl 比公式

## 公式

Strehl 比定义为实际光学系统 PSF 峰值强度与理想衍射受限系统 PSF 峰值强度之比：

**基本定义**：
$$
S = \frac{I_{actual}}{I_{ideal}}
$$

**小像差近似（Marechal 近似）**：
$$
S \approx e^{-(2\pi \sigma_{WFE})^2}
$$

其中 $\sigma_{WFE}$ 为以波长为单位的 RMS 波前误差。

**精确表达式（Born & Wolf）**：
$$
S = \left| \frac{1}{A} \iint_{pupil} e^{i k W(x,y)} dx dy \right|^2
$$

其中 $W(x,y)$ 为瞳孔上的波前误差函数（单位为长度），$k = 2\pi/\lambda$ 为波数，$A$ 为瞳孔面积。

**Zernike 系数形式的展开**：
$$
S \approx 1 - (2\pi)^2 \sum_{i} c_i^2 + \frac{(2\pi)^4}{2} \left(\sum_{i} c_i^2\right)^2 - \cdots
$$

其中 $c_i$ 为以波长为单位的 Zernike 系数。

**Marechal 判据**：
$$
S \geq 0.8 \quad \Leftrightarrow \quad \sigma_{WFE} \leq \frac{\lambda}{14} \approx 0.071\lambda
$$

## 变量与单位

| 变量 | 符号 | 单位 | 说明 |
|------|------|------|------|
| Strehl 比 | $S$ | 无量纲 | $0 < S \leq 1$ |
| 实际 PSF 峰值 | $I_{actual}$ | W/m² | 实际系统艾里斑中心强度 |
| 理想 PSF 峰值 | $I_{ideal}$ | W/m² | 衍射受限系统艾里斑中心强度 |
| RMS 波前误差 | $\sigma_{WFE}$ | 波长 ($\lambda$) | 波前误差的均方根值 |
| 波前误差函数 | $W(x,y)$ | μm 或 nm | 瞳孔坐标处的光程差 |
| 波数 | $k$ | rad/μm | $k = 2\pi/\lambda$ |
| 瞳孔面积 | $A$ | mm² | 光学系统的通光孔径面积 |
| Zernike 系数 | $c_i$ | 波长 ($\lambda$) | 第 $i$ 项 Zernike 的系数 |

## 适用条件

- **小像差近似**：指数近似 $S \approx e^{-(2\pi\sigma)^2}$ 仅在 $\sigma_{WFE} < \lambda/14$（即 $S > 0.8$）时较为准确。大像差时需使用精确积分公式。
- **圆对称瞳孔**：精确积分公式假设瞳孔为圆形。对于非圆瞳孔（如矩形、环形），需调整积分区域。
- **单色光**：Strehl 比通常在特定波长下评价。对于宽波段系统，需分别计算各波长下的 Strehl 比。
- **均匀照明**：公式假设瞳孔上照明均匀。对于部分相干或非均匀照明（如高斯光束），需做修正。
- **无杂散光**：Strehl 比只考虑波前像差，不包括杂散光、散射等效应。

## 推导或解释

1. **PSF 的傅里叶关系**：衍射受限系统的 PSF 是瞳孔函数的傅里叶变换模平方：$PSF \propto |\mathcal{F}\{P(x,y)\}|^2$。峰值强度正比于瞳孔面积平方。
2. **像差瞳孔函数**：存在波前误差时，瞳孔函数变为 $P'(x,y) = P(x,y) \cdot e^{i k W(x,y)}$。
3. **PSF 峰值计算**：PSF 中心强度正比于瞳孔上复振幅的积分模平方：
   $$
   I_{actual} \propto \left| \iint P'(x,y) dx dy \right|^2 = \left| \iint e^{i k W(x,y)} dx dy \right|^2
   $$
4. **归一化**：与理想系统（$W=0$）的峰值强度归一化，得到精确 Strehl 比公式。
5. **小像差展开**：当 $kW \ll 1$ 时，$e^{i k W} \approx 1 + i k W - (kW)^2/2$，取平均后得到：
   $$
   \langle e^{i k W} \rangle \approx 1 - \frac{k^2}{2} \langle W^2 \rangle = 1 - 2\pi^2 \sigma_{WFE}^2
   $$
   因此 $S \approx |1 - 2\pi^2 \sigma^2|^2 \approx 1 - 4\pi^2 \sigma^2 \approx e^{-(2\pi\sigma)^2}$。

## 验证样例

**样例 1**：Marechal 判据验证

- 给定 $\sigma_{WFE} = \lambda/14 \approx 0.071\lambda$
- $S = e^{-(2\pi \times 0.071)^2} = e^{-0.199} \approx 0.820$
- 结论：当 RMS WFE 为 $\lambda/14$ 时，Strehl 比约为 0.82，满足 $S \geq 0.8$ 的衍射受限判据

**样例 2**：不同像差水平的 Strehl 比

| $\sigma_{WFE}$ | $S$（近似） | 像质评价 |
|----------------|-------------|----------|
| $\lambda/28$ | 0.951 | 衍射极限，优秀 |
| $\lambda/14$ | 0.820 | Marechal 判据，良好 |
| $\lambda/10$ | 0.673 | 中等，可接受边缘 |
| $\lambda/4$ | 0.007 | 严重像差，不可用 |

**样例 3**：Zernike 系数计算

- 系统仅有离焦像差：$c_2 = 0.05\lambda$（即 $\lambda/20$）
- 假设无其他像差，$\sigma_{WFE} = c_2 = 0.05\lambda$
- $S = e^{-(2\pi \times 0.05)^2} = e^{-0.0987} \approx 0.906$
- 结论：仅有离焦 $\lambda/20$ 时，系统仍具有接近衍射极限的像质

## 关键关系
- 相关概念：[[../10-concepts/strehl-ratio|Strehl 比（概念）]]
- 相关概念：[[../10-concepts/wavefront-error|波前误差]]（Strehl 比直接由 WFE 决定）
- 相关概念：[[../10-concepts/zernike-polynomials|Zernike 多项式]]（Zernike 系数用于计算 WFE）
- 相关概念：[[../10-concepts/psf|点扩散函数]]（Strehl 比定义为 PSF 峰值之比）
- 相关公式：[[./rms-wavefront-error|RMS 波前误差]]
- 相关教程：[[../modules/50-optical-design/learning/12b-image-quality-evaluation|图像质量综合评价]]

## 来源
- Born & Wolf, *Principles of Optics*, Chapter 9
- Mahajan, "Strehl Ratio for Primary Aberrations," *JOSA*, 1983
- Smith, *Modern Optical Engineering*, 4th ed., Chapter 11
