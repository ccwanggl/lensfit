---
id: formula.fourier-transform-optics
title: 光学傅里叶变换对
type: formula
domains: [wave-optics]
status: draft
aliases:
  - fourier-transform-optics
  - 光学傅里叶变换
---

# 光学傅里叶变换对

## 公式

空间域复振幅分布 $U(x,y)$ 与空间频率域频谱 $\tilde{U}(f_x, f_y)$ 之间的傅里叶变换对：

**正变换（空间域 → 频率域）**：
$$
\tilde{U}(f_x, f_y) = \iint_{-\infty}^{+\infty} U(x,y) e^{-i2\pi(f_x x + f_y y)} dx dy
$$

**逆变换（频率域 → 空间域）**：
$$
U(x,y) = \iint_{-\infty}^{+\infty} \tilde{U}(f_x, f_y) e^{i2\pi(f_x x + f_y y)} df_x df_y
$$

透镜后焦面上的光学傅里叶变换（考虑透镜相位因子）：
$$
U_f(x', y') = \frac{e^{i\frac{k}{2f}(x'^2 + y'^2)}}{i\lambda f} \iint U_{in}(x,y) e^{-i\frac{2\pi}{\lambda f}(x' x + y' y)} dx dy
$$

其中 $k = 2\pi/\lambda$ 为波数，$f$ 为透镜焦距。

## 变量与单位

| 变量 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 空间域复振幅 | $U(x,y)$ | 无量纲（或 V/m） | 光场在物平面上的复振幅分布 |
| 空间频率谱 | $\tilde{U}(f_x, f_y)$ | 同上（频域） | 光场的空间频率成分 |
| 空间频率 | $f_x, f_y$ | $lp/mm$（或 $m^{-1}$） | 单位长度内的周期数 |
| 波长 | $\lambda$ | μm 或 nm | 照明光在真空中的波长 |
| 波数 | $k$ | $rad/μm$ | $k = 2\pi/\lambda$ |
| 透镜焦距 | $f$ | mm | 傅里叶变换透镜的焦距 |
| 频谱面坐标 | $x', y'$ | mm | 透镜后焦面上的物理坐标 |

频谱面坐标与空间频率的对应关系：
$$
f_x = \frac{x'}{\lambda f}, \quad f_y = \frac{y'}{\lambda f}
$$

## 适用条件

- **标量近似**：光场用标量复振幅描述，忽略矢量偏振效应（适用于 NA < 0.5 的大多数系统）。
- **傍轴近似**：光场与光轴夹角较小，$\sin\theta \approx \theta$，$\tan\theta \approx \theta$。
- **单色照明**：公式适用于单色光或窄带光，宽带光需对每个波长分别计算。
- **平面波照明**：上述透镜变换公式假设输入平面位于透镜前焦面且用平面波照明。非平面波照明需引入额外相位因子。
- **理想薄透镜**：忽略透镜厚度、像差和有限孔径效应。实际系统中需考虑有限孔径导致的渐晕和频率截断。

## 推导或解释

1. **亥姆霍兹方程**：单色光场满足 $\nabla^2 U + k^2 U = 0$。
2. **平面波展开**：任意光场可分解为不同方向传播平面波的叠加：
   $$
   U(x,y,z) = \iint A(f_x, f_y) e^{i2\pi(f_x x + f_y y)} e^{i k_z z} df_x df_y
   $$
3. **透镜的相位调制**：薄透镜引入二次相位因子 $e^{-i\frac{k}{2f}(x^2 + y^2)}$，相当于对入射光场进行相位调制。
4. **菲涅尔衍射积分**：结合菲涅尔近似和透镜相位因子，在透镜后焦面上得到输入光场的傅里叶变换（附加一个二次相位因子）。
5. **4f 系统消除附加相位**：使用双透镜 4f 结构，在第二透镜后焦面获得无附加相位因子的精确傅里叶变换。

## 验证样例

**样例 1**：矩形函数的傅里叶变换

- 输入：$U(x) = \text{rect}(x/a)$（宽度为 $a$ 的矩形孔）
- 频谱：$\tilde{U}(f_x) = a \cdot \text{sinc}(a f_x) = a \cdot \frac{\sin(\pi a f_x)}{\pi a f_x}$
- 物理意义：矩形孔径的衍射图样是 sinc 函数，第一个零点位于 $f_x = 1/a$

**样例 2**：高斯函数的傅里叶变换

- 输入：$U(x) = e^{-\pi x^2 / w^2}$
- 频谱：$\tilde{U}(f_x) = w \cdot e^{-\pi w^2 f_x^2}$
- 物理意义：高斯光束的远场仍然是高斯分布，束腰与发散角成反比

**样例 3**：透镜频谱面计算

- 透镜焦距 $f = 100$ mm，波长 $\lambda = 632.8$ nm
- 频谱面上 $x' = 10$ mm 处对应的空间频率：
  $$
  f_x = \frac{x'}{\lambda f} = \frac{10}{0.6328 \times 100} \approx 157.9 \text{ lp/mm}
  $$

## 关键关系
- 相关概念：[[../10-concepts/fourier-transform-pair|傅里叶变换对（概念）]]
- 相关概念：[[../10-concepts/4f-system|4f 系统]]（物理实现傅里叶变换的标准架构）
- 相关概念：[[../10-concepts/spatial-filtering|空间滤波]]（基于傅里叶变换的频域操作）
- 相关公式：[[./angular-spectrum|角谱传播公式]]（基于平面波展开的另一种衍射计算方法）
- 相关概念：[[../10-concepts/cutoff-frequency|截止频率]]（系统频域传递的极限）
- 相关教程：[[../modules/30-wave-optics/learning/12a-psf-otf-mtf|PSF、OTF 与 MTF 基础]]

## 来源
- Goodman, *Introduction to Fourier Optics*, 4th ed., Chapters 2, 5, 6
- Hecht, *Optics*, 5th ed., Chapter 11
