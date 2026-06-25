---

id: concept.chromaticity-diagram
title: 色度图
type: concept
domains: [spectroscopy]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: [chromaticity-diagram, CIE-1931, 色品图, chromaticity-chart]---
# 色度图

## 定义

色度图（Chromaticity Diagram）是**用二维坐标表示颜色色品**的图表，最经典的是 **CIE 1931 色度图**。它以人眼三刺激值为基础，将颜色映射到二维平面，横轴为 x，纵轴为 y。

色度图只表示颜色的色品（色相和饱和度），不表示亮度（明度）。

## 直观理解

- 图的外围马蹄形曲线是**光谱轨迹**，曲线上每一点代表纯光谱色（单色光）。
- 曲线包围的所有区域是**人眼可见的全部颜色**。
- 中心区域颜色不饱和，越靠近边缘越纯、越鲜艳。
- 连接两点的直线上的颜色可由两端颜色混合得到。

## 关键参数/公式

| 参数 | 说明 |
|------|------|
| x, y | CIE 1931 色度坐标，由三刺激值 X, Y, Z 归一化得到 |
| 光谱轨迹 | 380 nm ~ 780 nm 单色光在图中的轨迹 |
| 白光点 | 色温对应的等能白点（如 D65: x=0.3127, y=0.3290） |

色度坐标计算：
```
x = X / (X + Y + Z)
y = Y / (X + Y + Z)
z = 1 - x - y
```

## 适用场景

- **色彩测量与比较**：用色度坐标定量描述颜色。
- **光源显色性评估**：在图上比较光源与标准光源的色差。
- **显示技术**：确定显示屏的色域（Gamut）范围。
- **LED 色分选**：在色度图上设定 bin 区。
- **色差计算**：配合 ΔE 公式评估颜色差异。

## 关键关系

- 相关概念：[[./color-temperature|色温]]（白光点在图上的位置）
- 相关概念：[[./spectral-power-distribution|光谱分布函数]]（决定色度坐标）
- 相关公式：[[../20-formulas/delta-e|Delta E 色差]]
- 相关教程：[[50-learning/12-otf-and-image-quality|色彩科学]]
- 相关教程：[[50-learning/16-spectroscopy|色度学]]

## 常见误区

1. **色度图不是均匀色空间**：相同距离不代表相同视觉色差，CIE 1976 UCS（u', v'）改进了均匀性。
2. **色度图外无颜色**：色度图外不存在物理上可实现的颜色。
3. **色度图不表示亮度**：Y（亮度）信息需单独给出。
4. **所有颜色都可由 RGB 显示**：显示屏色域（三角形）远小于人眼可见色域。

## 可视化辅助

![[attachments/visuals/chromaticity-diagram.svg]]
*图：Chromaticity Diagram*

## 来源

- CIE 15:2004, Colorimetry, 4th edition
- 光学工程教材，第 12 章（色彩科学）与第 16 章（色度学）

## 关联实验

- [[90-maps/Optics Lab#光谱混色实验|光谱混色实验]] — 混合两种单色光，观察合成光谱和感知颜色。
