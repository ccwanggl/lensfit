---
id: module.geometric.formulas
title: 模块乙公式 MOC
type: moc
domains: []
status: draft
---

# 模块乙公式 MOC

> 本文件汇总模块乙（几何光学与一阶成像）涉及的所有核心公式。

## 一阶成像公式

### 薄透镜公式（高斯公式）

$$\frac{1}{f} = \frac{1}{u} + \frac{1}{v}$$

- $f$：焦距
- $u$：物距（实物为正）
- $v$：像距（实像为正）

### 牛顿透镜公式

$$x \cdot x' = f^2$$

- $x$：物到前焦点的距离
- $x'$：像到后焦点的距离

### 横向放大率

$$M = \frac{h'}{h} = -\frac{v}{u} = \frac{f}{f - u}$$

### 轴向放大率

$$M_L = \frac{dv}{du} = -M^2 \cdot \frac{n}{n'}$$

## 系统参数公式

### 数值孔径（NA）

$$\text{NA} = n \sin\theta_{\max}$$

### F值（F-number）

$$F = \frac{f}{D}$$

- $D$：入瞳直径

### 相对孔径

$$\frac{D}{f} = \frac{1}{F}$$

### 视角公式

$$\theta = 2 \arctan\frac{H}{2f}$$

- $H$：传感器对角线（或宽度/高度）
- $\theta$：对应视角

### 焦距与视场关系

$$f = \frac{H}{2 \tan(\theta/2)}$$

## 景深公式

### 容许弥散圆直径

$$c = \frac{\text{像素尺寸}}{2} \sim \frac{\text{像素尺寸}}{3}$$（工程经验）

### 近景深与远景深

$$D_n = \frac{u^2 \cdot c \cdot F}{f^2 + u \cdot c \cdot F}, \quad D_f = \frac{u^2 \cdot c \cdot F}{f^2 - u \cdot c \cdot F}$$

### 总景深

$$\text{DoF} = D_f - D_n = \frac{2 u^2 \cdot c \cdot F \cdot f^2}{f^4 - (u \cdot c \cdot F)^2}$$

近似（当 $u \gg f$ 时）：

$$\text{DoF} \approx \frac{2 u^2 \cdot c \cdot F}{f^2}$$

## 分辨率与匹配

### 艾里斑半径（衍射极限）

$$r_{\text{Airy}} = 1.22 \frac{\lambda \cdot F}{n}$$

### 奈奎斯特采样极限

$$f_{\text{Nyquist}} = \frac{1}{2p}$$

- $p$：像素间距（mm/像素）

### 镜头-传感器匹配条件

$$\text{镜头分辨率} \geq \text{传感器奈奎斯特频率}$$

### 空间频率转换

$$f_{\text{lp/mm}} = \frac{f_{\text{cy/px}}}{M \cdot p}$$

- $M$：系统放大率
- $p$：像素尺寸（mm）

## 远心系统

### 物方远心条件

入瞳位于物方无穷远处，主光线平行于光轴。

$$\text{放大率} = \text{常数} \quad \text{（与物距无关）}$$

## 接口相关

### C-mount 法兰距

$$f_{\text{flange}} = 17.526 \text{ mm}$$

### 背焦距离（Back Focal Length）

$$\text{BFL} = \text{最后一面到像平面距离}$$

### 适配计算

$$\text{接圈厚度} = f_{\text{flange,镜头}} - f_{\text{flange,相机}}$$

## 相关概念

→ 参见 [[concepts|模块乙概念 MOC]]
