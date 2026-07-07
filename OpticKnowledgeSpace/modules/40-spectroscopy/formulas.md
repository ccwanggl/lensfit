---
id: moc.spectroscopy-formulas
title: 模块丁公式索引（MOC）
type: moc
parent: module.spectroscopy
---

# 模块丁公式索引（MOC）

## 光栅方程

$$d(\sin\theta_i + \sin\theta_m) = m\lambda \quad (m = 0, \pm1, \pm2, \dots)$$

- $d$：光栅常数（相邻刻线间距）
- $\theta_i$：入射角（相对于光栅法线）
- $\theta_m$：第 $m$ 级衍射角
- $m$：衍射级次
- $\lambda$：波长

正入射简化（$\theta_i = 0$）：

$$d \sin\theta_m = m\lambda$$

## 光栅分辨率

$$R = \frac{\lambda}{\Delta\lambda} = mN$$

- $R$：光谱分辨率（分辨本领）
- $\Delta\lambda$：刚好可分辨的最小波长差
- $m$：衍射级次
- $N$：被照明区域的总刻线数

## 自由光谱范围（FSR）

$$\Delta\lambda_{FSR} = \frac{\lambda}{m}$$

相邻级次不重叠的最大波长范围。

## 棱镜色散

### 角色散

$$\frac{d\theta}{d\lambda} = \frac{2\sin(A/2)}{\sqrt{1 - n^2 \sin^2(A/2)}} \cdot \frac{dn}{d\lambda}$$

- $A$：棱镜顶角
- $n$：棱镜材料折射率
- $dn/d\lambda$：材料色散率

最小偏向角条件下：

$$n = \frac{\sin\left(\frac{A + \delta_m}{2}\right)}{\sin(A/2)}$$

### 线色散

$$D_l = f \cdot \frac{d\theta}{d\lambda}$$

- $f$：聚焦镜焦距
- $D_l$：像平面上的波长分离距离（单位：mm/nm）

## 阿贝数（色散系数）

$$V_d = \frac{n_d - 1}{n_F - n_C}$$

- $n_d$：d 线（587.6 nm）折射率
- $n_F$：F 线（486.1 nm）折射率
- $n_C$：C 线（656.3 nm）折射率

**数值越大，色散越小**。低色散玻璃 $V_d > 50$（冕牌玻璃），高色散玻璃 $V_d < 50$（火石玻璃）。

## 普朗克黑体辐射

### 光谱辐射亮度（普朗克公式）

$$B_\lambda(T) = \frac{2hc^2}{\lambda^5} \frac{1}{e^{hc/\lambda k_B T} - 1}$$

- $h$：普朗克常数 $6.626 \times 10^{-34}$ J·s
- $c$：光速
- $k_B$：玻尔兹曼常数 $1.381 \times 10^{-23}$ J/K
- $T$：绝对温度（K）
- $\lambda$：波长

### 维恩位移定律

$$\lambda_{max} \cdot T = 2.898 \times 10^{-3} \, \text{m·K}$$

峰值波长与温度成反比。

### 斯特藩-玻尔兹曼定律

$$M = \sigma T^4$$

- $M$：总辐射出射度（W/m²）
- $\sigma = 5.670 \times 10^{-8}$ W/(m²·K⁴)

## 色度计算

### CIE 三刺激值

$$X = k \int_{\lambda} S(\lambda) \bar{x}(\lambda) R(\lambda) d\lambda$$

$$Y = k \int_{\lambda} S(\lambda) \bar{y}(\lambda) R(\lambda) d\lambda$$

$$Z = k \int_{\lambda} S(\lambda) \bar{z}(\lambda) R(\lambda) d\lambda$$

- $S(\lambda)$：光源相对光谱功率分布
- $\bar{x}, \bar{y}, \bar{z}$：CIE 标准色度匹配函数
- $R(\lambda)$：物体反射/透射光谱
- $k$：归一化常数

### 色度坐标（CIE 1931）

$$x = \frac{X}{X + Y + Z}, \quad y = \frac{Y}{X + Y + Z}, \quad z = \frac{Z}{X + Y + Z}$$

### CIE76 Delta E（色差）

$$\Delta E_{ab}^* = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}$$

- $\Delta L^*$：明度差
- $\Delta a^*$：红绿色度差
- $\Delta b^*$：黄蓝色度差

### CIE94 / CIE2000 色差（改进版）

$$\Delta E_{94}^* = \sqrt{\left(\frac{\Delta L^*}{K_L S_L}\right)^2 + \left(\frac{\Delta C^*}{K_C S_C}\right)^2 + \left(\frac{\Delta H^*}{K_H S_H}\right)^2}$$

（更精确的人眼感知一致性模型）

## 拉曼位移

$$\Delta \tilde{\nu} = \tilde{\nu}_0 - \tilde{\nu}_s = \frac{1}{\lambda_0} - \frac{1}{\lambda_s}$$

- $\tilde{\nu}_0$：入射光波数
- $\tilde{\nu}_s$：散射光波数
- 斯托克斯位移：散射光波长较长（能量较低）
- 反斯托克斯位移：散射光波长较短（能量较高）

## 光谱仪分辨率（实际）

$$\Delta\lambda_{实际} = \sqrt{\Delta\lambda_{光栅}^2 + \Delta\lambda_{狭缝}^2 + \Delta\lambda_{探测器}^2}$$

实际分辨率是各项贡献的卷积/综合效果。

---

> **速查提示**：
> - 光栅方程 $ightarrow$ 计算衍射角/波长位置
> - $R = mN$ $ightarrow$ 光栅理论极限分辨率
> - 阿贝数 $V_d$ $ightarrow$ 材料色散大小（越大越小）
> - 普朗克公式 $ightarrow$ 光源光谱分布预测
> - Delta E $ightarrow$ 颜色差异量化
