---

id: formula.rayleigh-criterion
title: 瑞利判据
type: formula
domains: [general]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: []---

# 瑞利判据

## 公式
$$ d = \frac{0.61 \cdot \lambda}{\text{NA}} $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $d$ | 最小可分辨距离 | μm |
| $\lambda$ | 光波长 | μm |
| $\text{NA}$ | 数值孔径 | 无量纲 |

## 适用条件
- 显微镜等高 NA 光学系统
- 衍射极限分辨率判定
- 两个点光源刚好能被分辨的最小间距

## 推导或解释
瑞利判据指出：当一个点光源的衍射图样（艾里斑）中心恰好落在另一个点光源衍射图样的第一极小处时，两者刚好可被分辨。圆孔径的艾里斑第一极小角半径为 $1.22\lambda/D$，换算为物空间线度并引入数值孔径 $\text{NA} = n\sin\theta$，整理得 $d = 0.61\lambda/\text{NA}$。

## 验证样例
绿光 $\lambda = 0.55\,\mu\text{m}$，物镜 NA = 0.9：

$$ d = \frac{0.61 \times 0.55}{0.9} = \frac{0.3355}{0.9} \approx 0.373\,\mu\text{m} $$

即该显微镜在绿光下的理论分辨极限约为 $0.37\,\mu\text{m}$（$370\,\text{nm}$）。要获得更高分辨率，需使用更短波长或更大 NA 的物镜。

## 关键关系
- 相关概念：[[10-concepts/瑞利判据|瑞利判据]]、[[10-concepts/数值孔径|数值孔径]]、[[../10-concepts/衍射极限|衍射极限]]
- 相关教程：[[50-learning/08-domain-applications|第8章]]

## 可视化辅助

![[attachments/visuals/airy-disk.svg]]
*图：Airy Disk*

## 来源

## 关联实验

- [[90-maps/Optics Lab#diffraction|圆孔衍射与艾里斑]] — 改变波长和光圈孔径，观察艾里斑大小和衍射图样的变化。
