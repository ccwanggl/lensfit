---
id: formula.czerny-turner-resolution
title: Czerny-Turner 分辨率
type: formula
domains: [spectroscopy]
status: draft
aliases:
  - czerny-turner-resolution
  - C-T分辨率
---

# Czerny-Turner 分辨率

## 公式

Czerny-Turner 光谱仪的实际分辨率由多个因素共同决定，包括光栅理论分辨率、狭缝宽度、光学像差和探测器像元尺寸。

**光栅理论分辨率**（衍射极限）：
$$
R_{grating} = m \cdot N = m \cdot \frac{W}{d}
$$

其中 $m$ 为衍射级次，$N$ 为光栅总刻线数，$W$ 为光栅被照明的宽度，$d$ 为光栅常数。

**狭缝限制的分辨率**（狭缝宽度对应的谱线展宽）：
$$
\Delta\lambda_{slit} = w \cdot \frac{d \cos\beta}{m f_2}
$$

其中 $w$ 为入射狭缝宽度，$f_2$ 为聚焦镜焦距，$\beta$ 为衍射角。

**系统综合光谱带宽（FWHM，近似）**：
$$
\Delta\lambda_{FWHM} \approx \sqrt{\Delta\lambda_{slit}^2 + \Delta\lambda_{aberration}^2 + \Delta\lambda_{detector}^2}
$$

实际光谱分辨率（以 FWHM 定义）：
$$
R_{actual} = \frac{\lambda}{\Delta\lambda_{FWHM}}
$$

**线色散**（频谱面上波长与位置的对应关系）：
$$
D_L = \frac{d\lambda}{dx} = \frac{d \cos\beta}{m f_2}
$$

## 变量与单位

| 变量 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 理论分辨率 | $R_{grating}$ | 无量纲 | 光栅本身的理论分辨极限 |
| 衍射级次 | $m$ | 整数 | 通常为 1 |
| 光栅总刻线数 | $N$ | 无量纲 | 被照明区域内的总刻线数 |
| 光栅宽度 | $W$ | mm | 准直光束在光栅上的照明宽度 |
| 光栅常数 | $d$ | nm | 相邻刻线间距 |
| 狭缝宽度 | $w$ | mm | 通常为 0.01–0.1 mm |
| 聚焦镜焦距 | $f_2$ | mm | 决定线色散和光谱分辨率 |
| 衍射角 | $\beta$ | 度 (°) | 相对于光栅法线 |
| 线色散 | $D_L$ | nm/mm | 频谱面上每毫米对应的波长范围 |
| 光谱带宽 | $\Delta\lambda_{FWHM}$ | nm | 仪器测得的谱线半高全宽 |

## 适用条件

- **平面光栅**：公式适用于 Czerny-Turner 配置的平面光栅系统。
- **近 Littrow 配置**：当入射角与衍射角接近时（Littrow 条件），光栅效率最高，但像散可能较大。
- **小像差近似**：像差项 $\Delta\lambda_{aberration}$ 在优化良好的系统中应接近狭缝衍射极限。
- **探测器像元限制**：要求探测器像元尺寸小于或等于狭缝像宽，否则探测器像元成为分辨率限制因素。
- **单色光或窄线宽光源**：测量仪器线型函数时，光源线宽应远小于预期仪器带宽。

## 推导或解释

1. **光栅理论分辨率**：基于瑞利判据，两条等强度谱线刚好可分辨时，一条谱线的主极大落在另一条的第一个极小处。光栅的角半宽度为 $\Delta\theta = \lambda / (Nd \cos\beta)$，结合光栅方程微分 $d\cos\beta \cdot d\theta = m \cdot d\lambda$，得到 $R = mN$。
2. **狭缝限制**：狭缝宽度 $w$ 在焦面上形成的像宽为 $w \cdot (f_2/f_1)$（若放大率不为 1）。对应的波长宽度由线色散转换得到 $\Delta\lambda_{slit} = w \cdot D_L$。
3. **像差贡献**：球差、彗差和像散会使理想点扩散成斑，导致谱线展宽。像散是 Czerny-Turner 结构的主要像差，可通过优化反射镜曲率和布局来最小化。
4. **探测器像元贡献**：探测器像元尺寸 $p$ 对应的波长宽度为 $\Delta\lambda_{detector} = p \cdot D_L$。当 $p$ 大于狭缝像宽时，探测器成为分辨率瓶颈。
5. **综合卷积**：实际仪器线型是狭缝函数、像差点扩散函数和探测器采样函数的卷积，FWHM 近似为各分量的平方和根。

## 验证样例

**样例 1**：典型 Czerny-Turner 光谱仪分辨率估算

- 光栅：1200 线/mm，$d = 833.3$ nm，$m = 1$
- 照明宽度：$W = 12$ mm，理论分辨率 $R = 1 \times 1200 \times 12 = 14400$
- 在 $\lambda = 500$ nm 处，理论最小可分辨波长差：$\Delta\lambda = 500/14400 \approx 0.035$ nm

**样例 2**：狭缝限制的分辨率

- 狭缝宽度 $w = 25$ μm = 0.025 mm
- 聚焦镜焦距 $f_2 = 150$ mm，$\beta = 15°$
- 线色散：$D_L = d \cos\beta / (m f_2) = 833.3 \times \cos(15°) / 150 \approx 5.37$ nm/mm
- 狭缝限制带宽：$\Delta\lambda_{slit} = 0.025 \times 5.37 \approx 0.134$ nm
- 实际分辨率（狭缝限制）：$R_{actual} = 500 / 0.134 \approx 3730$

**样例 3**：探测器像元限制

- 探测器像元 $p = 14$ μm = 0.014 mm
- 像元限制带宽：$\Delta\lambda_{detector} = 0.014 \times 5.37 \approx 0.075$ nm
- 综合 FWHM（假设像差可忽略）：$\Delta\lambda_{FWHM} = \sqrt{0.134^2 + 0.075^2} \approx 0.154$ nm

## 关键关系
- 相关概念：[[../10-concepts/czerny-turner|Czerny-Turner 光谱仪结构]]
- 相关概念：[[../10-concepts/slit|入射狭缝]]（狭缝宽度是实际分辨率的主要限制）
- 相关概念：[[../10-concepts/spectral-bandwidth|光谱带宽/FWHM]]（实际测量的分辨率指标）
- 相关概念：[[../10-concepts/spectral-resolution|光谱分辨率]]（理论极限与实际的对比）
- 相关公式：[[./012-grating-equation|光栅方程]]
- 相关公式：[[./013-grating-resolving-power|光栅光谱分辨率]]
- 相关设备：[[../40-devices/011-spectrometer|光谱仪]]

## 来源
- Hecht, *Optics*, 5th ed., Chapter 10
- Loewen & Popov, *Diffraction Gratings and Applications*, Chapter 7
- James, *Spectrograph Design Fundamentals*, Chapter 4
