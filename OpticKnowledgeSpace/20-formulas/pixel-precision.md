---

id: formula.pixel-precision
title: 像素精度
type: formula
domains: [general]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: []---

# 像素精度

## 公式
$$ \text{Precision} = \frac{p}{1000 \cdot \beta} \quad [\text{mm/px}] $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $\text{Precision}$ | 像素精度 | mm/px |
| $p$ | 像元尺寸 | μm |
| $\beta$ | 横向放大倍率 | 无量纲 |

## 适用条件
- 已知放大倍率和像元尺寸，计算物方单个像素代表的物理尺寸
- 用于视觉测量系统的精度估算
- 假设系统无畸变、无离焦

## 推导或解释
像元尺寸 $p$ 在物方对应的长度为 $p/\beta$。将 $p$ 从 μm 换算为 mm，即得物方像素精度。值越小表示系统分辨能力越强（每个像素代表更小的物理尺寸）。

## 验证样例
像元尺寸 $p = 3.45\,\mu\text{m}$，放大倍率 $\beta = 0.2\times$：

$$ \text{Precision} = \frac{3.45}{1000 \times 0.2} = \frac{3.45}{200} = 0.01725\,\text{mm/px} = 17.25\,\mu\text{m/px} $$

即每个像素对应物方约 $17.25\,\mu\text{m}$，该系统的单像素测量精度约为 $17\,\mu\text{m}$。

## 关键关系
- 相关概念：[[10-concepts/像素精度|像素精度]]、[[../10-concepts/放大倍率|放大倍率]]
- 相关教程：[[50-learning/05-matching-basics|第5章]]

## 来源