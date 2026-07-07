---
id: formula.rms-wavefront-error
title: RMS 波前误差
type: formula
domains: [optical-design]
status: draft
aliases:
  - rms-wavefront-error
  - RMS波前误差
  - WFE-RMS
---

# RMS 波前误差

## 公式

RMS（Root Mean Square）波前误差是描述光学系统波前偏离理想球面程度的统计量，定义为瞳孔区域内波前误差函数平方的平均值的平方根。

**基本定义**：
$$
\sigma_{WFE} = \sqrt{\frac{\iint_{pupil} W^2(x,y) dx dy}{A}}
$$

其中 $W(x,y)$ 为瞳孔坐标处的波前误差（OPD），$A$ 为瞳孔面积。

**去除平移（Piston）后的 RMS**（通常定义）：
$$
\sigma_{WFE} = \sqrt{\frac{\iint_{pupil} [W(x,y) - \bar{W}]^2 dx dy}{A}}
$$

其中 $\bar{W}$ 为波前误差在瞳孔上的平均值：
$$
\bar{W} = \frac{1}{A} \iint_{pupil} W(x,y) dx dy
$$

**Zernike 拟合后的 RMS**：
$$
\sigma_{WFE}^2 = \sum_{i} c_i^2 + \sigma_{residual}^2
$$

其中 $c_i$ 为各 Zernike 项的系数（以波长为单位），$\sigma_{residual}$ 为 Zernike 拟合后残余的高阶波前误差。

**仅含倾斜和离焦时的 RMS**：
$$
\sigma_{WFE} = \sqrt{c_1^2 + c_2^2 + c_3^2 + c_4^2 + \cdots}
$$

注意：去除 piston 后 $c_0 = 0$；去除 tilt 后 $c_1 = c_2 = 0$；去除 defocus 后 $c_3 = 0$。

**RMS 与 PV 的关系**（近似，对于特定像差类型）：

| 像差类型 | PV / RMS 比值 |
|----------|---------------|
| 球差（初级） | $3.46$（$PV = 3.46 \cdot \sigma$） |
| 像散 | $2.83$ |
| 彗差 | $3.35$ |
| 离焦 | $3.46$ |
| 随机面形 | $3$–$5$（经验值） |

## 变量与单位

| 变量 | 符号 | 单位 | 说明 |
|------|------|------|------|
| RMS 波前误差 | $\sigma_{WFE}$ | 波长 ($\lambda$) 或 nm | 波前误差的统计均方根值 |
| 波前误差函数 | $W(x,y)$ | nm 或 μm | 瞳孔坐标处的光程差 |
| 瞳孔面积 | $A$ | mm² | 光学系统的通光孔径面积 |
| 平均波前误差 | $\bar{W}$ | nm 或 μm | 瞳孔上的平均 OPD |
| Zernike 系数 | $c_i$ | 波长 ($\lambda$) | 第 $i$ 项 Zernike 的系数 |
| 残余误差 | $\sigma_{residual}$ | 波长 ($\lambda$) | Zernike 拟合后未解释的误差 |

## 适用条件

- **圆对称瞳孔**：标准 RMS 定义适用于圆形瞳孔。对于非圆瞳孔，需相应调整积分区域。
- **均匀加权**：上述公式对瞳孔上所有点等权重平均。实际中有时采用光强加权 RMS（考虑照明不均匀性）。
- **Zernike 正交基**：Zernike 系数的平方和等于 RMS 的前提是各 Zernike 项采用标准正交归一化（如 Noll 归一化）。不同归一化方式的系数不能直接平方和。
- **去除低阶项**：在光学设计优化中，通常去除 piston（不影响像质）和 tilt（可通过调整像面位置补偿），只计算剩余像差对应的 RMS。
- **多波长加权**：对于宽波段系统，有时计算多个波长下 RMS 的加权平均作为综合评价指标。

## 推导或解释

1. **统计定义**：RMS 是标准统计量，描述数据点偏离平均值的分散程度。对于波前误差，它反映波前“起伏”的平均幅度。
2. **正交展开**：Zernike 多项式在单位圆上正交归一化，因此波前误差的方差可分解为各 Zernike 项方差之和（Parseval 定理类比）。
3. **去除 piston 的原因**：piston 是整体相位平移，不改变光强分布，因此不影响像质。RMS 计算中去除 piston 以反映实际对成像有贡献的误差。
4. **去除 tilt 和 defocus**：tilt 对应像面倾斜（可通过调整探测器角度补偿），defocus 对应轴向离焦（可通过调整像面位置补偿）。在评估“不可补偿”的像差时，常去除这些可补偿项。
5. **与 Strehl 比的关系**：在小像差条件下，RMS WFE 与 Strehl 比存在一一对应关系（Marechal 近似），使 RMS 成为像质的便捷指标。

## 验证样例

**样例 1**：简单抛物面波前

- 波前误差：$W(x,y) = a(x^2 + y^2)$，在半径为 1 的圆瞳孔上
- 平均值：$\bar{W} = a \cdot \frac{1}{\pi} \int_0^{2\pi} \int_0^1 r^2 \cdot r dr d\theta = a \cdot \frac{1}{2}$
- 方差：$\langle (W - \bar{W})^2 \rangle = a^2 \cdot \frac{1}{\pi} \int_0^{2\pi} \int_0^1 (r^2 - 1/2)^2 r dr d\theta = a^2/12$
- RMS：$\sigma_{WFE} = a/\sqrt{12} \approx 0.289a$
- PV：$W_{max} - W_{min} = a(1 - 0) = a$（在边缘处）
- PV/RMS：$a / (0.289a) \approx 3.46$（与初级球差理论比值一致）

**样例 2**：Zernike 系数求 RMS

- 某系统的 Zernike 系数（去除 piston 后）：
  - 离焦 $c_4 = 0.03\lambda$
  - 像散 $c_5 = 0.02\lambda$
  - 彗差 $c_7 = 0.015\lambda$
  - 球差 $c_9 = 0.01\lambda$
- 假设无残余高阶误差：$\sigma_{WFE} = \sqrt{0.03^2 + 0.02^2 + 0.015^2 + 0.01^2} = \sqrt{0.001625} \approx 0.0403\lambda$
- 对应 Strehl 比：$S \approx e^{-(2\pi \times 0.0403)^2} = e^{-0.064} \approx 0.938$
- 结论：系统具有接近衍射极限的优良像质

**样例 3**：Marechal 判据的 RMS 值

- Marechal 判据要求 $S \geq 0.8$
- 由 $S = e^{-(2\pi\sigma)^2} = 0.8$，解得：
  $$
  \sigma = \frac{\sqrt{-\ln(0.8)}}{2\pi} = \frac{0.472}{6.283} \approx 0.075\lambda \approx \lambda/13.3
  $$
- 工程上常取保守值 $\sigma_{WFE} \leq \lambda/14 \approx 0.071\lambda$

## 关键关系
- 相关概念：[[../10-concepts/wavefront-error|波前误差（概念）]]
- 相关概念：[[../10-concepts/zernike-polynomials|Zernike 多项式]]（Zernike 是计算 RMS 的标准基函数）
- 相关概念：[[../10-concepts/strehl-ratio|Strehl 比]]（RMS WFE 与 Strehl 比直接相关）
- 相关公式：[[./strehl-ratio|Strehl 比公式]]
- 相关概念：[[../10-concepts/opd|光程差]]（RMS WFE 是 OPD 的统计度量）
- 相关教程：[[../modules/50-optical-design/learning/06b-wavefront-aberrations|像差（下）｜高阶像差与设计关联]]

## 来源
- Born & Wolf, *Principles of Optics*, Chapter 9
- Noll, "Zernike Polynomials and Atmospheric Turbulence," *JOSA*, 1976
- Wyant & Creath, "Basic Wavefront Aberration Theory for Optical Metrology"
