---
id: concept.strehl-ratio
title: Strehl 比
type: concept
domains: [optical-design]
status: draft
aliases:
  - strehl-ratio
  - Strehl比
  - 斯特列尔比
  - strehl-definition
---

# Strehl 比

## 定义

Strehl 比（Strehl Ratio）是评价光学系统成像质量的核心指标之一，定义为实际光学系统的点扩散函数（PSF）峰值强度与理想衍射受限系统 PSF 峰值强度之比：
$$
S = \frac{I_{actual}}{I_{ideal}}
$$

对于小像差系统（RMS 波前误差 $\sigma_{WFE} \ll \lambda$），Strehl 比与波前误差之间存在近似解析关系：
$$
S \approx e^{-(2\pi \sigma_{WFE})^2}
$$

其中 $\sigma_{WFE}$ 为以波长为单位的 RMS 波前误差。

**Marechal 判据**：当 $S \geq 0.8$ 时，系统被认为是“衍射受限”的，对应 RMS 波前误差约为 $\lambda/14$（约 0.071 $\lambda$）。

## 直观理解

Strehl 比就像“成像锐度的衰减系数”：
- $S = 1.0$ → 完美系统，像点最锐利（实际中不存在，但可作为基准）
- $S = 0.8$ → 衍射受限，像质优良，人眼和大多数应用难以察觉缺陷
- $S = 0.5$ → 像质明显下降，波前误差已较大，接近传统"可接受"边缘
- $S = 0.1$ → 严重像差，像点已显著模糊，成像质量差

**物理直觉**：波前误差导致各光线在像点处不再是同相位叠加，产生相消干涉，使峰值强度降低。波前误差越大，相位错乱越严重，峰值强度下降越显著。

## 关键参数/公式

| 参数 | 符号 | 说明 |
|------|------|------|
| Strehl 比 | $S$ | 无量纲，$0 < S \leq 1$ |
| 理想 PSF 峰值 | $I_{ideal}$ | 衍射受限系统艾里斑中心强度 |
| 实际 PSF 峰值 | $I_{actual}$ | 实际系统 PSF 中心强度 |
| RMS 波前误差 | $\sigma_{WFE}$ | 以波长为单位，$\sigma_{WFE} \ll 1$ 时近似成立 |
| Marechal 极限 | $S = 0.8$ | 衍射受限的判定阈值 |

近似公式的精确形式（Born & Wolf）：
$$
S = \left| \frac{1}{A} \iint_{pupil} e^{i k W(x,y)} dx dy \right|^2
$$
其中 $W(x,y)$ 为波前误差函数，$k = 2\pi/\lambda$，$A$ 为瞳孔面积。

小像差展开：
$$
S \approx 1 - (2\pi \sigma_{WFE})^2 + \frac{(2\pi \sigma_{WFE})^4}{2} - \cdots
$$

## 适用场景

- **光学设计验收**：作为系统是否达到“衍射受限”的标准判据（$S \geq 0.8$）。
- **自适应光学性能评估**：实时测量和报告校正后的 Strehl 比，评估自适应光学系统的校正效果。
- **天文成像**：大口径望远镜的像质通常用 Strehl 比在特定波长（如近红外 $K$ 波段）下评价。
- **显微镜物镜评估**：高 NA 物镜的 Strehl 比直接决定能否实现理论分辨率。
- **激光光束质量**：与 $M^2$ 因子联合使用，评价聚焦光束的接近理想高斯模的程度。
- **光学制造公差制定**：通过 Strehl 比对制造误差的敏感度分析，制定合理的公差范围。

## 关键关系
- 相关概念：[[./wavefront-error|波前误差]]（Strehl 比直接由波前误差决定）
- 相关概念：[[./zernike-polynomials|Zernike 多项式]]（Zernike 系数用于计算和优化波前误差）
- 相关概念：[[./psf|点扩散函数]]（Strehl 比定义为 PSF 峰值强度之比）
- 相关概念：[[./diffraction-limit|衍射极限]]（$S = 1$ 对应理想衍射受限系统）
- 相关公式：[[../20-formulas/strehl-ratio|Strehl 比公式]]
- 相关公式：[[../20-formulas/rms-wavefront-error|RMS 波前误差]]
- 相关教程：[[../modules/50-optical-design/learning/12b-image-quality-evaluation|图像质量综合评价]]

## 常见误区

1. **Strehl 比 = MTF？** 不是。Strehl 比是空域 PSF 峰值指标，MTF 是频域对比度传递指标。两者相关但不等同。高 Strehl 比通常意味着高 MTF，但 MTF 还包含更多频率域信息。
2. **S > 0.8 就绝对合格？** 不一定。某些应用（如光刻、干涉测量）要求更高的像质（$S > 0.9$ 甚至 $S > 0.95$）。
3. **近似公式在任何情况下都适用？** $S \approx e^{-(2\pi\sigma)^2}$ 只在 $\sigma_{WFE} < \lambda/14$ 时准确。大像差时误差很大，需直接计算积分。
4. **忽略波长依赖性**：Strehl 比强烈依赖于评价波长，通常在长波长（如红外）更容易达到高 Strehl 比。比较不同系统的 Strehl 比时必须说明波长。

## 来源

- Born & Wolf, *Principles of Optics*, Chapter 9
- Mahajan, "Strehl Ratio for Primary Aberrations," *JOSA*, 1983
- Smith, *Modern Optical Engineering*, 4th ed., Chapter 11
