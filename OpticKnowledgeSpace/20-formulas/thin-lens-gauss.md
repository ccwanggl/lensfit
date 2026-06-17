---
id: formula.thin-lens-gauss
title: 薄透镜高斯公式
type: formula
domains: [general]
status: draft
source_ids: []
reviewed_at:
owners: []
aliases: []
---

# 薄透镜高斯公式

## 公式
$$ \frac{1}{f} = \frac{1}{u} + \frac{1}{v} $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $f$ | 焦距 | mm |
| $u$ | 物距 | mm |
| $v$ | 像距 | mm |

## 适用条件
- 薄透镜（透镜厚度远小于焦距）
- 近轴近似（光线与光轴夹角很小）
- 均匀介质中

## 推导或解释
由几何光学中的近轴光线追迹可得：平行于光轴的光线经透镜后汇聚于焦点，通过透镜中心的光线不偏折。两束光线的交点即像点，整理后即得高斯公式。

## 验证样例
已知 $f = 50\,\text{mm}$，$u = 2\,\text{m} = 2000\,\text{mm}$，求像距 $v$：

$$ \frac{1}{v} = \frac{1}{f} - \frac{1}{u} = \frac{1}{50} - \frac{1}{2000} = 0.02 - 0.0005 = 0.0195 $$

$$ v = \frac{1}{0.0195} \approx 51.28\,\text{mm} $$

物距远大于焦距时，像距略大于焦距，像靠近焦点。

## 关键关系
- 相关概念：[[10-concepts/近轴近似|近轴近似]]、[[../10-concepts/焦距|焦距]]
- 相关教程：[[50-learning/01-light-and-waves|第1章]]

## 可视化辅助

![[attachments/visuals/thin-lens-geometry.svg]]
*图：Thin Lens Geometry*

## 来源