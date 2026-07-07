---
id: moc.design-formulas
title: 模块戊公式索引（MOC）
type: moc
parent: module.design
---

# 模块戊公式索引（MOC）

## 像质评价基础

### Strehl 比

$$S = \frac{I_{actual}}{I_{ideal}} = \left| \frac{1}{\pi} \int_0^{2\pi} \int_0^1 e^{i k W(\rho, \theta)} \rho \, d\rho \, d\theta \right|^2$$

- $W(\rho, \theta)$：波前像差函数（以波长为单位）
- $k = 2\pi / \lambda$
- **Strehl 比 ≥ 0.8** 对应衍射极限（Marechal 判据）

### Marechal 判据

$$W_{RMS} \leq \frac{\lambda}{14} \approx 0.071\lambda$$

波前 RMS 误差小于 $\lambda/14$ 时，系统接近衍射极限。

### RMS 波前误差

$$W_{RMS} = \sqrt{\frac{1}{A} \iint_A [W(x,y) - \bar{W}]^2 \, dx\, dy}$$

- $\bar{W}$：波前平均值
- $A$：光瞳面积

## Seidel 像差（第三级像差）

### 五项 Seidel 和

$$\sum S_I = \sum A^2 \Delta\left(\frac{u}{n}\right) \quad \text{（球差）}$$

$$\sum S_{II} = \sum A \bar{A} \Delta\left(\frac{u}{n}\right) \quad \text{（彗差）}$$

$$\sum S_{III} = \sum \bar{A}^2 \Delta\left(\frac{u}{n}\right) \quad \text{（像散）}$$

$$\sum S_{IV} = \sum H^2 \Delta\left(\frac{1}{n}\right) \quad \text{（场曲/Petzval）}$$

$$\sum S_V = \sum \frac{\bar{A}}{A} \left(\bar{A}^2 \Delta\frac{u}{n} + H^2 \Delta\frac{1}{n}\right) \quad \text{（畸变）}$$

- $A = n i$：折射不变量（近轴）
- $\bar{A} = n \bar{i}$：视场相关折射不变量
- $H = n \bar{u} y - n u \bar{y}$：Lagrange 不变量

## 波前像差与 Zernike 多项式

### Zernike 展开

$$W(\rho, \theta) = \sum_{n=0}^{\infty} \sum_{m=-n}^{n} C_n^m Z_n^m(\rho, \theta)$$

其中 $n - |m|$ 为偶数。

### 常用 Zernike 项（Fringe 编号）

| 编号 | 名称 | 数学表达式 | 物理意义 |
|------|------|-----------|----------|
| Z₁ | 平移 | $1$ | 无物理意义（可去除） |
| Z₂ | x 倾斜 | $2\rho\cos\theta$ | 波前倾斜（x 方向） |
| Z₃ | y 倾斜 | $2\rho\sin\theta$ | 波前倾斜（y 方向） |
| Z₄ | 离焦 | $\sqrt{3}(2\rho^2 - 1)$ | 焦点位置误差 |
| Z₅ | 像散 0° | $\sqrt{6}\rho^2\cos 2\theta$ | 子午/弧矢像散 |
| Z₆ | 像散 45° | $\sqrt{6}\rho^2\sin 2\theta$ | 45° 像散 |
| Z₇ | 彗差 x | $\sqrt{8}(3\rho^3 - 2\rho)\cos\theta$ | x 方向彗差 |
| Z₈ | 彗差 y | $\sqrt{8}(3\rho^3 - 2\rho)\sin\theta$ | y 方向彗差 |
| Z₉ | 球差 | $\sqrt{5}(6\rho^4 - 6\rho^2 + 1)$ | 三级球差 |

### 波前 RMS 与 Zernike 系数

$$W_{RMS}^2 = \sum_{n,m} |C_n^m|^2 \quad \text{（归一化 Zernike）}$$

## MTF 相关

### 衍射极限 MTF（圆形光瞳，非相干）

$$MTF(f) = \frac{2}{\pi} \left[ \arccos\left(\frac{f}{f_c}\right) - \frac{f}{f_c}\sqrt{1 - \left(\frac{f}{f_c}\right)^2} \right]$$

- $f$：空间频率（lp/mm）
- $f_c = \frac{1}{\lambda \cdot F\#}$：截止频率

### 截止频率（非相干）

$$f_{cutoff} = \frac{2NA}{\lambda} = \frac{1}{\lambda \cdot F\#}$$

- 与相干照明截止频率的关系：$f_{cutoff,\text{非相干}} = 2 f_{cutoff,\text{相干}}$

### 离焦 MTF 近似

$$MTF_{defocus}(f) \approx MTF_{diffraction}(f) \cdot \cos\left(2\pi W_{020} \frac{f}{f_c}\right)$$

- $W_{020}$：离焦的 Zernike 系数（以波长为单位）

## 几何光学近似

### 畸变

$$\text{Distortion} = \frac{Y_{actual} - Y_{ideal}}{Y_{ideal}} \times 100\%$$

- 枕形畸变：$>0$（正畸变）
- 桶形畸变：$<0$（负畸变）

### 照度衰减（cos⁴ 定律）

$$E(\theta) = E_0 \cos^4\theta$$

- $\theta$：视场角
- $E_0$：轴上照度

近似公式：

$$E(\theta) \approx E_0 \left(1 - 2\theta^2\right) \quad \text{（小角度，弧度）}$$

### 渐晕因子

$$V = \frac{A_{effective}(\theta)}{A_{entrance}}$$

照度综合：$E(\theta) = E_0 \cdot V \cdot \cos^4\theta$

## 光学设计约束

### 边缘厚度约束

$$t_{edge} = t_{center} - \frac{D^2}{8R}$$

- $t_{edge}$：透镜边缘厚度
- $t_{center}$：中心厚度
- $D$：通光口径
- $R$：曲率半径（凸面为正）

### 像方 NA 与 F 数

$$NA = n' \sin\theta' \approx \frac{1}{2F\#}$$

$$F\# = \frac{f}{D_{EP}}$$

- $n'$：像方折射率
- $\theta'$：像方锥角半角
- $D_{EP}$：入瞳直径

### 放大率与像面尺寸

$$m = \frac{y'}{y} = \frac{n u}{n' u'}$$

像面直径：$D_{image} = 2y'_{max} = 2m \cdot y_{max}$

## 公差分析

### 蒙特卡洛统计

$$\sigma_{total}^2 = \sum_i \sigma_i^2 = \sum_i \left(\frac{\partial P}{\partial x_i}\right)^2 \sigma_{x_i}^2$$

- $P$：性能参数（如 RMS wavefront）
- $x_i$：第 $i$ 个公差参数
- $\sigma_{x_i}$：第 $i$ 个参数的统计分布标准差

### 灵敏度

$$S_i = \frac{\Delta P}{\Delta x_i}$$

单位参数变化引起的性能变化量。

### 良率估算

$$Y = \frac{N_{pass}}{N_{total}} \times 100\%$$

- $N_{pass}$：满足规格的蒙特卡洛样本数
- $N_{total}$：总样本数（通常 500~5000）

## 光学不变量

### Lagrange 不变量

$$H = n \bar{u} y - n u \bar{y} = n' \bar{u}' y' - n' u' \bar{y}'$$

- 全系统守恒量
- 决定光瞳-视场关系

### 光通量守恒

$$\Phi = L \cdot A \cdot \Omega \cdot \tau$$

- $L$：光源亮度
- $A$：光瞳面积
- $\Omega$：接收立体角
- $\tau$：系统透射率

---

> **速查提示**：
> - Strehl 比 ≥ 0.8 $ightarrow$ 衍射极限（Marechal 判据）
> - Zernike 系数 $ightarrow$ 波前像差分解诊断
> - MTF 曲线 $ightarrow$ 对比度 vs 空间频率的完整像质描述
> - Seidel 和 $ightarrow$ 系统级像差预算分配
> - 蒙特卡洛 $ightarrow$ 制造良率量化评估
