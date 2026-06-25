---

id: concept.spectral-power-distribution
title: 光谱分布函数
type: concept
domains: [spectroscopy]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: [spectral-power-distribution, SPD, 光谱功率分布, 光谱分布]---
# 光谱分布函数

## 定义

光谱分布函数（Spectral Power Distribution, SPD）描述**光源在各波长上的辐射功率（或相对功率）分布**，是光源最完整的光谱特征表示。

SPD 是色度学、光度学和辐射度学的基础：任何与光相关的颜色、亮度、显色性等物理量，都可以从 SPD 计算得到。

## 直观理解

- SPD 就像光源的“光谱指纹”：告诉你在每个波长上有多少光。
- 理想的 SPD 可以是一条平滑曲线（白炽灯近似黑体），也可以是离散的尖峰（LED 是几个窄带峰）。
- 知道了 SPD，就可以计算出色度坐标、色温、显色指数（CRI）、光照度等所有光学参数。

## 关键参数/公式

| 参数 | 符号 | 说明 |
|------|------|------|
| 光谱功率分布 | P(λ) | 单位波长间隔内的辐射功率（W/nm）或相对值 |
| 波长范围 | λ | 通常 380 ~ 780 nm（可见光）或更宽（UV-NIR） |
| 光谱采样间隔 | Δλ | 测量 SPD 时的波长步进，通常 1 ~ 5 nm |

由 SPD 计算色度三刺激值（CIE 1931）：
```
X = k ∫ P(λ) x̄(λ) dλ
Y = k ∫ P(λ) ȳ(λ) dλ
Z = k ∫ P(λ) z̄(λ) dλ
```
其中 x̄(λ), ȳ(λ), z̄(λ) 是 CIE 标准观察者配色函数。

## 适用场景

- **光源表征**：LED、荧光灯、白炽灯SPD 差异巨大，决定其视觉特性。
- **显色指数计算**：CRI 需要光源和标准参照光源的 SPD。
- **色彩管理**：显示屏、印刷的标准光源由 SPD 定义（如 D65）。
- **照明设计**：通过 SPD 预测颜色呈现效果。
- **植物照明**：需要特定波长（如红、蓝）的 SPD 来优化光合作用。
- **光谱仪校准**：标准灯的 SPD 作为参考。

## 关键关系

- 相关概念：[[./color-temperature|色温]]（由 SPD 匹配黑体辐射得到）
- 相关概念：[[./chromaticity-diagram|色度图]]（色度坐标由 SPD 计算）
- 相关设备：[[../40-devices/spectrometer|光谱仪]]（SPD 测量工具）
- 相关设备：[[../40-devices/integrating-sphere|积分球]]（均匀收集 SPD 的光）
- 相关教程：[[50-learning/16-spectroscopy|光谱学]]

## 常见误区

1. **SPD 与光谱图混淆**：SPD 是功率随波长的分布，不是吸收光谱或透射光谱。
2. **相对 SPD 与绝对 SPD**：相对 SPD 用于颜色计算，绝对 SPD 用于光度/辐射度计算。
3. **峰值波长 ≠ 主波长**：LED 的峰值波长是 SPD 最大值位置，但视觉颜色可能由多个峰共同决定。
4. **SPD 平滑 ≠ 显色好**：白炽灯 SPD 平滑但缺失部分短波，显色指数中等；多芯片 LED SPD 有峰但显色指数可很高。

## 可视化辅助

![[attachments/visuals/spectral-power-distribution.svg]]
*图：Spectral Power Distribution*

## 来源

- CIE 15:2004, Colorimetry
- 光学工程教材，第 16 章 光谱学

## 关联实验

- [[90-maps/Optics Lab#color-mixing|光谱混色实验]] — 混合两种单色光，观察合成光谱和感知颜色。
