---

id: formula.angle-of-view
title: 视角公式
type: formula
domains: [general]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: []---

# 视角公式

## 公式
$$ \text{AFOV} = \frac{360}{\pi} \cdot \arctan\left(\frac{s}{2f}\right) $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $\text{AFOV}$ | 对角（或水平/垂直）视角 | °（度） |
| $s$ | 传感器宽度（或高度/对角线） | mm |
| $f$ | 焦距 | mm |

## 适用条件
- 薄透镜，近轴近似
- $s$ 与 $f$ 取同一方向（宽对宽、高对高、对角线对对角线）
- 角度换算系数 $360/\pi \approx 57.296$

## 推导或解释
由几何关系，从透镜中心看去，传感器边缘与光轴夹角为 $\arctan(s/2f)$。两侧对称，总视角为该角的两倍。乘以弧度转角度系数 $180/\pi$ 即得。

## 验证样例
全画幅传感器宽度 $s = 36\,\text{mm}$，焦距 $f = 50\,\text{mm}$：

$$ \text{AFOV} = \frac{360}{\pi} \cdot \arctan\left(\frac{36}{2 \times 50}\right) = \frac{360}{\pi} \cdot \arctan(0.36) \approx 57.296 \times 0.345 \approx 39.6° $$

即标准 $50\,\text{mm}$ 镜头在 $36\,\text{mm}$ 传感器上的水平视角约为 $40°$。

## 关键关系
- 相关概念：[[10-concepts/视角|视角]]、[[10-concepts/焦距|焦距]]
- 相关教程：[[50-learning/02-geometric-optics|第2章]]

## 可视化辅助

![[attachments/visuals/angle-of-view.svg]]
*图：Angle Of View*

## 来源

## 关联实验

- [[90-maps/Optics Lab#angle-of-view|视角与传感器尺寸实验]] — 给定焦距和传感器尺寸，观察水平、垂直、对角线视角的变化。
