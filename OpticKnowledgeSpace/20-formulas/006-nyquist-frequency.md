---
id: formula.nyquist-frequency
title: 奈奎斯特频率
type: formula
domains:
- general
status: reviewed
aliases: []
---


# 奈奎斯特频率

## 公式
$$ f_N = \frac{1000}{2p} \quad [\text{lp/mm}] $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $f_N$ | 奈奎斯特频率 | lp/mm（线对/毫米） |
| $p$ | 像元尺寸 | μm |

## 适用条件
- 离散采样系统（CCD/CMOS 传感器）
- 根据采样定理，系统可分辨的最高空间频率
- 适用于单色或拜耳阵列的极限分析

## 推导或解释
根据奈奎斯特采样定理，要无混叠地恢复一个信号，采样频率至少为信号最高频率的两倍。在成像中，一个线对至少需要两个像元来分辨，因此传感器极限分辨率为 $1/(2p)$。将 $p$ 从 μm 换算为 mm，即得 $f_N = 1000/(2p)$。

## 验证样例
像元尺寸 $p = 3.45\,\mu\text{m}$：

$$ f_N = \frac{1000}{2 \times 3.45} = \frac{1000}{6.9} \approx 144.9\,\text{lp/mm} $$

即该传感器可分辨的最高空间频率约为 $145\,\text{lp/mm}$。若镜头 MTF 在此频率处仍有较高值，则需要考虑抗混叠措施。

## 关键关系
- 相关概念：[[10-concepts/039-奈奎斯特频率|奈奎斯特频率]]、[[10-concepts/041-混叠|混叠]]
- 相关教程：[[50-learning/004-sensors|第4章]]、[[50-learning/005-matching-basics|第5章]]

## 可视化辅助

![[attachments/visuals/nyquist-aliasing.svg]]
*图：Nyquist Aliasing*

## 来源