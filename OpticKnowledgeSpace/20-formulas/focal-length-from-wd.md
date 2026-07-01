---
id: formula.focal-length-from-wd
title: 焦距反推公式
type: formula
domains:
- general
status: reviewed
aliases: []
---


# 焦距反推公式

## 公式
$$ f = \frac{\text{WD} \cdot s}{\text{FOV} + s} $$

近似形式（当 $\text{FOV} \gg s$ 时）：
$$ f \approx \frac{\text{WD} \cdot s}{\text{FOV}} $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $f$ | 焦距 | mm |
| $\text{WD}$ | 工作距离（物距） | mm |
| $s$ | 传感器宽度 | mm |
| $\text{FOV}$ | 视场宽度 | mm |

## 适用条件
- 薄透镜，近轴近似
- 已知工作距离、传感器尺寸和所需视场，反推所需焦距
- 近似式在视场远大于传感器尺寸时误差很小

## 推导或解释
由放大倍率 $\beta = s/\text{FOV}$ 及高斯公式 $1/f = 1/u + 1/v$，结合 $v = \beta u$ 消去像距，即可反解出焦距 $f$。近似式忽略了分母中的 $s$ 项，常用于快速估算。

## 验证样例
工作距离 $\text{WD} = 300\,\text{mm}$，传感器宽度 $s = 6.4\,\text{mm}$，视场 $\text{FOV} = 64\,\text{mm}$：

$$ f = \frac{300 \times 6.4}{64 + 6.4} = \frac{1920}{70.4} \approx 27.3\,\text{mm} $$

近似值：$f \approx 300 \times 6.4 / 64 = 30\,\text{mm}$，误差约 $10\%$。当 $\text{FOV}$ 更大时近似更准。

## 关键关系
- 相关概念：[[10-concepts/工作距离|工作距离]]、[[10-concepts/视场|视场]]
- 相关教程：[[50-learning/02-geometric-optics|第2章]]

## 来源

## 关联实验

- [[90-maps/Optics Lab#放大倍率与像素精度实验|放大倍率与像素精度实验]] — 给定焦距、工作距离和像元尺寸，计算横向放大倍率、像素精度及物体特征在传感器上占据的像素数。
