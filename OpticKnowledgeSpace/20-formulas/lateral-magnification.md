---

id: formula.lateral-magnification
title: 横向放大倍率
type: formula
domains: [general]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: []---

# 横向放大倍率

## 公式
$$ \beta = \frac{v}{u} = \frac{s}{\text{FOV}} $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $\beta$ | 横向放大倍率 | 无量纲 |
| $v$ | 像距 | mm |
| $u$ | 物距 | mm |
| $s$ | 传感器宽度（或高度） | mm |
| $\text{FOV}$ | 视场宽度（或高度） | mm |

## 适用条件
- 薄透镜，近轴近似
- 物像共轭关系成立
- $s$ 与 $\text{FOV}$ 取对应方向（宽对宽、高对高）

## 推导或解释
由相似三角形关系：像高与物高之比等于像距与物距之比。在机器视觉中，常用传感器尺寸与视场尺寸之比来直接计算放大倍率，便于系统选型。

## 验证样例
传感器宽度 $s = 12.8\,\text{mm}$，视场 $\text{FOV} = 64\,\text{mm}$：

$$ \beta = \frac{12.8}{64} = 0.2\times $$

即物体在传感器上成像缩小为原物的 $1/5$。

## 关键关系
- 相关概念：[[10-concepts/放大倍率|放大倍率]]、[[../10-concepts/视场|视场]]
- 相关教程：[[50-learning/02-geometric-optics|第2章]]

## 来源