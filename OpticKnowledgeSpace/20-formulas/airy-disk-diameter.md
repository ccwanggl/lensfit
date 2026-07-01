---
id: formula.airy-disk-diameter
title: 艾里斑直径
type: formula
domains:
- general
status: reviewed
aliases: []
---


# 艾里斑直径

## 公式
$$ d = 2.44 \cdot \lambda \cdot F\# $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $d$ | 艾里斑直径 | μm |
| $\lambda$ | 光波长 | μm |
| $F\#$ | 光圈值（F数） | 无量纲 |

## 适用条件
- 圆孔径衍射（理想光学系统）
- 衍射极限分辨率
- 可见光或近红外波段

## 推导或解释
圆孔径夫琅禾费衍射的第一极小值出现在角半径 $\theta = 1.22\lambda/D$ 处。艾里斑直径（第一暗环直径）在焦平面上的线度为 $d = 2 \times 1.22 \lambda \times f/D = 2.44 \lambda \cdot F\#$，其中 $F\# = f/D$。

## 验证样例
绿光 $\lambda = 0.55\,\mu\text{m}$，光圈 $F\# = 2.8$：

$$ d = 2.44 \times 0.55 \times 2.8 \approx 3.76\,\mu\text{m} $$

即该光学系统的衍射极限光斑直径约为 $3.76\,\mu\text{m}$，若像元尺寸大于此值，则系统受像元限制；若小于此值，则受衍射限制。

## 关键关系
- 相关概念：[[10-concepts/衍射极限|衍射极限]]、[[10-concepts/艾里斑|艾里斑]]
- 相关教程：[[50-learning/01-light-and-waves|第1章]]、[[50-learning/03-lens-parameters|第3章]]

## 可视化辅助

![[attachments/visuals/airy_disk_pattern.png]]
*图：艾里斑径向强度分布与二维图样。左图显示不同波长和 F# 下第一暗环位置：蓝光（短波）暗环更近，F/5.6 暗环比 F/2.8 明显外移。右图是绿光 550nm、F/2.8 的二维衍射斑，青色虚线圈出第一暗环。*

## 来源