---
id: formula.angular-spectrum
title: 角谱传播公式
type: formula
domains: [wave-optics]
status: draft
aliases:
  - angular-spectrum
  - 角谱传播
  - 角谱法
---

# 角谱传播公式

## 公式

角谱传播（Angular Spectrum Propagation）是基于平面波展开的衍射计算方法，将光场在某一平面上的分布分解为不同角度传播的平面波成分，再通过传播相位因子描述各成分在自由空间中的传播，最后在目标平面上重建光场。

**角谱定义**（输入平面 $z=0$ 处的空间频谱）：
$$
A(f_x, f_y; 0) = \iint_{-\infty}^{+\infty} U(x,y; 0) e^{-i2\pi(f_x x + f_y y)} dx dy
$$

**传播后的角谱**（传播距离 $z$）：
$$
A(f_x, f_y; z) = A(f_x, f_y; 0) \cdot e^{i k_z z}
$$

其中纵向波数 $k_z$ 为：
$$
k_z = \sqrt{k^2 - (2\pi f_x)^2 - (2\pi f_y)^2} = k \sqrt{1 - (\lambda f_x)^2 - (\lambda f_y)^2}
$$

**重建光场**（输出平面 $z$）：
$$
U(x,y; z) = \iint_{-\infty}^{+\infty} A(f_x, f_y; z) \cdot e^{i2\pi(f_x x + f_y y)} df_x df_y
$$

或写为统一形式：
$$
U(x,y; z) = \mathcal{F}^{-1}\left\{ \mathcal{F}\{U(x,y; 0)\} \cdot e^{i k \sqrt{1 - (\lambda f_x)^2 - (\lambda f_y)^2} \cdot z} \right\}
$$

## 变量与单位

| 变量 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 光场 | $U(x,y; z)$ | 无量纲（或 V/m） | $z$ 平面处的复振幅分布 |
| 角谱 | $A(f_x, f_y; z)$ | 同上（频域） | 平面波成分的振幅和相位 |
| 空间频率 | $f_x, f_y$ | $lp/mm$ | 横向空间频率 |
| 纵向波数 | $k_z$ | $rad/μm$ | 传播方向的波矢分量 |
| 总波数 | $k$ | $rad/μm$ | $k = 2\pi/\lambda$ |
| 传播距离 | $z$ | mm | 两平面之间的轴向距离 |
| 波长 | $\lambda$ | μm 或 nm | 照明光波长 |

**倏逝波条件**：当 $(\lambda f_x)^2 + (\lambda f_y)^2 > 1$ 时，$k_z$ 为纯虚数，对应倏逝波（Evanescent Wave），其振幅随传播距离指数衰减，不携带远场信息。

## 适用条件

- **标量波动方程**：适用于标量光场，忽略偏振和矢量效应。
- **均匀各向同性介质**：传播介质（通常为空气）的折射率均匀。
- **任意传播距离**：角谱法同时适用于近场（Fresnel 区）和远场（Fraunhofer 区），无需区分衍射区域。
- **平面边界**：输入和输出平面需为平行平面。
- **采样要求**：数值计算时，空间频率采样需满足奈奎斯特采样定理，避免混叠。
- **计算效率**：由于涉及两次 FFT，角谱法在数值计算中非常高效，特别适合计算机模拟。

## 推导或解释

1. **亥姆霍兹方程**：单色光场满足 $\nabla^2 U + k^2 U = 0$。
2. **平面波基函数**：方程的基本解是平面波 $e^{i(k_x x + k_y y + k_z z)}$，其中 $k_x^2 + k_y^2 + k_z^2 = k^2$。
3. **傅里叶分解**：任意平面上的光场可分解为不同平面波的叠加（角谱）。
4. **传播相位因子**：每个平面波成分独立传播，在距离 $z$ 后累积相位 $e^{i k_z z}$。
5. **倏逝波**：当 $k_x^2 + k_y^2 > k^2$ 时，$k_z$ 为虚数，对应倏逝波，振幅按 $e^{-\alpha z}$ 衰减，在近场光学和纳米光子学中有重要应用。
6. **与菲涅尔衍射的关系**：在傍轴近似下（$k_z \approx k - \pi\lambda(f_x^2 + f_y^2)$），角谱法退化为菲涅尔衍射积分。

## 验证样例

**样例 1**：平面波传播

- 输入：$U(x,y;0) = 1$（均匀平面波）
- 角谱：$A(f_x, f_y; 0) = \delta(f_x) \delta(f_y)$
- 传播后：$A(f_x, f_y; z) = \delta(f_x) \delta(f_y) \cdot e^{ikz}$
- 重建：$U(x,y;z) = e^{ikz}$（仅累积整体相位，振幅不变）

**样例 2**：矩形孔径的远场衍射

- 输入：宽度 $a$ 的矩形孔，$U(x,y;0) = \text{rect}(x/a) \cdot \text{rect}(y/a)$
- 角谱：$A(f_x, f_y; 0) = a^2 \cdot \text{sinc}(a f_x) \cdot \text{sinc}(a f_y)$
- 远场（Fraunhofer 近似）：$U(x,y;z) \propto \text{sinc}\left(\frac{a x}{\lambda z}\right) \cdot \text{sinc}\left(\frac{a y}{\lambda z}\right)$
- 与菲涅尔衍射结果一致

**样例 3**：倏逝波截止

- 波长 $\lambda = 500$ nm，空间频率 $f_x = 3000$ lp/mm
- 判断：$\lambda f_x = 0.5 \times 3000 \times 10^{-3} = 1.5 > 1$
- $k_z = k \sqrt{1 - 1.5^2} = i k \sqrt{1.25}$（纯虚数）
- 衰减长度：$\delta = 1/|k_z| = \lambda / (2\pi \sqrt{1.25}) \approx 71$ nm
- 结论：该频率成分在传播约 71 nm 后衰减为原来的 $1/e$

## 关键关系
- 相关概念：[[../10-concepts/fourier-transform-pair|傅里叶变换对]]（角谱法是傅里叶光学的核心应用）
- 相关公式：[[./fourier-transform-optics|光学傅里叶变换对]]
- 相关概念：[[../10-concepts/4f-system|4f 系统]]（透镜实现傅里叶变换，与角谱传播互补）
- 相关概念：[[../10-concepts/diffraction-limit|衍射极限]]（角谱法可精确计算衍射受限系统的光场）
- 相关概念：[[../10-concepts/evanescent-wave|倏逝波]]（角谱法自然包含倏逝波的描述）
- 相关教程：[[../modules/30-wave-optics/learning/12a-psf-otf-mtf|PSF、OTF 与 MTF 基础]]

## 来源
- Goodman, *Introduction to Fourier Optics*, 4th ed., Chapter 3
- Hecht, *Optics*, 5th ed., Chapter 11
- Novotny & Hecht, *Principles of Nano-Optics*, Chapter 2
