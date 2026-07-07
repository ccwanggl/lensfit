---
id: concept.spectral-bandwidth
title: 光谱带宽与 FWHM
type: concept
domains:
  - spectroscopy
status: draft
aliases:
  - Spectral Bandwidth
  - FWHM
  - 半高全宽
  - 谱线宽度
---

# 光谱带宽与 FWHM

## 定义

**光谱带宽（Spectral Bandwidth）** 指光谱仪或光学系统能够分辨或传输的波长范围宽度。在光谱测量中，它通常由仪器函数（Instrument Function）决定，反映仪器对单色光的响应展宽。

**FWHM（Full Width at Half Maximum，半高全宽）** 是描述谱线或光谱峰宽度的标准参数，定义为峰强度最大值一半处的宽度。FWHM 是衡量光谱分辨率、光源线宽和滤波器带宽的通用指标。

两者关系：
- 光谱带宽通常指仪器或系统的通带宽度。
- FWHM 是描述任何峰形分布的通用参数，可用于谱线、滤波器、脉冲等。

## 直观理解

想象一个理想单色光源（如单一波长激光）经过光谱仪测量。理论上应得到一条无限细的谱线。实际上，由于狭缝宽度、衍射、像差等因素，测得的谱线会展宽成一个峰形。FWHM 就是这个峰的"胖瘦"程度。

- FWHM 小 = 峰窄 = 分辨率高，能区分靠得更近的谱线。
- FWHM 大 = 峰宽 = 分辨率低，相邻谱线可能重叠。

类比：FWHM 就像人的体型——瘦子（小 FWHM）可以轻松挤过窄缝（分辨紧邻谱线），胖子（大 FWHM）则不行。

## 关键参数/公式

| 参数 | 符号 | 单位 | 说明 |
|------|------|------|------|
| FWHM | $\Delta\lambda_{FWHM}$ | nm | 峰半高处的全宽 |
| 光谱分辨率 | $R$ | 无量纲 | $R = \lambda / \Delta\lambda$ |
| 仪器带宽 | $\Delta\lambda_{inst}$ | nm | 仪器决定的等效带宽 |
| 自然线宽 | $\Delta\lambda_{nat}$ | nm | 光源本身决定的线宽（受激寿命等） |

关键关系：
- 总测量线宽（卷积结果）：$\Delta\lambda_{meas} \approx \sqrt{\Delta\lambda_{inst}^2 + \Delta\lambda_{source}^2}$
- 分辨率与 FWHM：$R = \lambda / \Delta\lambda_{FWHM}$
- 狭缝宽度与带宽：$\Delta\lambda = w \cdot D_L$（$w$ 为狭缝宽度，$D_L$ 为倒线色散）

## 适用场景

- **光谱仪性能评估**：用 FWHM 表征仪器对不同线宽光源的分辨能力。
- **光源线宽测量**：用已知高分辨率仪器测量光源的 FWHM。
- **滤波器设计**：带通滤波器的带宽通常用 FWHM 定义。
- **荧光/拉曼光谱**：测量峰位和 FWHM 以分析分子结构和环境。
- **激光特性**：激光的线宽（如 0.1 nm、1 pm）通常用 FWHM 表示。
- **OCT/相干成像**：光源的 FWHM 决定轴向分辨率。

## 关键关系
- 相关概念：[[10-concepts/slit|入射狭缝]]、[[10-concepts/czerny-turner|Czerny-Turner 光谱仪]]、[[10-concepts/spectral-resolution|光谱分辨率]]
- 相关公式：[[20-formulas/czerny-turner-resolution|Czerny-Turner 分辨率]]
- 相关概念：[[10-concepts/dispersion|色散]]、[[10-concepts/diffraction-grating|衍射光栅]]
- 相关教程：[[50-learning/016-spectroscopy|光谱学与色彩科学]]

## 常见误区

- **混淆 FWHM 与半高半宽（HWHM）**：FWHM 是全宽，HWHM 是半宽，FWHM = 2 × HWHM。
- **认为仪器带宽等于 FWHM**：仪器带宽通常近似等于 FWHM，但严格来说是仪器函数的宽度指标。
- **忽略卷积效应**：实际测量线宽是光源线宽与仪器函数的卷积，不是简单相加。
- **将分辨率与 FWHM 混用**：分辨率 $R = \lambda / \Delta\lambda$ 是无量纲比值，FWHM 是波长宽度。
- **不同峰形用同一 FWHM 比较**：高斯峰和洛伦兹峰的 FWHM 定义相同但形状不同，直接比较可能误导。

## 来源

- Hecht, *Optics*, 5th ed., Chapter 10
- Davis, *Building Scientific Apparatus*, Chapter 10
- 光学工程教材，光谱仪器章节
