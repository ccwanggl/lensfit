---
id: moc.wave-formulas
title: 模块丙公式索引（MOC）
type: moc
parent: module.wave
---

# 模块丙公式索引（MOC）

## 干涉

### 双缝干涉

$$d \sin\theta = m\lambda \quad (m = 0, \pm1, \pm2, \dots)$$

- $d$：双缝间距
- $\theta$：衍射角
- $m$：干涉级次
- $\lambda$：波长

条纹间距：

$$\Delta y = \frac{\lambda L}{d}$$

- $L$：屏到双缝距离

### 薄膜干涉（等厚干涉）

$$2nd \cos\theta_r = m\lambda \quad \text{（相长干涉）}$$

- $n$：薄膜折射率
- $d$：膜厚
- $\theta_r$：折射角

## 衍射

### 单缝夫琅禾费衍射

$$a \sin\theta = m\lambda \quad (m = \pm1, \pm2, \dots)$$

- $a$：缝宽
- 中央亮纹半角宽：$\theta_1 \approx \lambda / a$

### 光栅方程

$$d(\sin\theta_i + \sin\theta_m) = m\lambda \quad (m = 0, \pm1, \pm2, \dots)$$

- $d$：光栅常数（周期）
- $\theta_i$：入射角
- $\theta_m$：第 $m$ 级衍射角

### 光栅分辨率

$$R = \frac{\lambda}{\Delta\lambda} = mN$$

- $N$：被照明的光栅总刻线数
- $m$：衍射级次

### 艾里斑（圆孔衍射）

第一暗环半径：

$$r_{Airy} = 1.22 \frac{\lambda f}{D} = 1.22 \lambda \cdot F\#$$

- $f$：焦距
- $D$：孔径直径
- $F\# = f/D$：F 数

## 瑞利判据

最小可分辨角：

$$\theta_{min} = 1.22 \frac{\lambda}{D}$$

最小可分辨距离：

$$\delta = 1.22 \frac{\lambda}{NA}$$

- $NA$：数值孔径

## 傅里叶变换对

### 定义

$$\mathcal{F}\{g(x,y)\} = G(f_x, f_y) = \iint_{-\infty}^{+\infty} g(x,y) e^{-j2\pi(f_x x + f_y y)} dx\, dy$$

$$\mathcal{F}^{-1}\{G(f_x, f_y)\} = g(x,y) = \iint_{-\infty}^{+\infty} G(f_x, f_y) e^{j2\pi(f_x x + f_y y)} df_x\, df_y$$

### 常用变换对

| 空域 $g(x)$ | 频域 $G(f_x)$ |
|-------------|---------------|
| 矩形函数 $\text{rect}(x/a)$ | $a \cdot \text{sinc}(a f_x)$ |
| 高斯函数 $e^{-\pi x^2}$ | $e^{-\pi f_x^2}$ |
| 三角函数 $\Lambda(x/a)$ | $a \cdot \text{sinc}^2(a f_x)$ |
| 冲激函数 $\delta(x)$ | $1$ |
| 常数 $1$ | $\delta(f_x)$ |
| 余弦 $\cos(2\pi f_0 x)$ | $\frac{1}{2}[\delta(f_x - f_0) + \delta(f_x + f_0)]$ |

### 角谱传播

$$U(x,y,z) = \mathcal{F}^{-1}\left\{ A(f_x, f_y, 0) \cdot e^{j k_z z} \right\}$$

其中传播核：

$$k_z = \sqrt{k^2 - (2\pi f_x)^2 - (2\pi f_y)^2} = \sqrt{k^2 - k_x^2 - k_y^2}$$

- $k = 2\pi / \lambda$：波数

## OTF / MTF

### 相干照明下的 OTF

$$OTF(f_x, f_y) = \mathcal{F}\{ |h(x,y)|^2 \}$$

- $h(x,y)$：相干点扩散函数（PSF）

### 非相干照明下的 OTF

$$OTF(f_x, f_y) = \frac{\mathcal{F}\{ |h(x,y)|^2 \}}{\mathcal{F}\{ |h(x,y)|^2 \}|_{(0,0)}}$$

### 截止频率

圆形出瞳（直径 $D$，像方焦距 $f_i$）：

$$f_{cutoff} = \frac{D}{\lambda f_i} = \frac{1}{\lambda \cdot F\#}$$

## 空间滤波

### 4f 系统输出

$$g_{out}(x,y) = \mathcal{F}^{-1}\{ H(f_x, f_y) \cdot G_{in}(f_x, f_y) \}$$

- $H(f_x, f_y)$：滤波函数（孔径函数）
- $G_{in}(f_x, f_y)$：输入频谱

---

> **速查提示**：
> - 艾里斑半径 $ightarrow$ 分辨率极限
> - 光栅方程 $ightarrow$ 色散/分光
> - 傅里叶变换对 $ightarrow$ 空域与频域的桥梁
> - MTF 曲线 $ightarrow$ 对比度保留率 vs 空间频率
