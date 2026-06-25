---

id: formula.coverage-ratio
title: 像圈覆盖比
type: formula
domains: [general]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: []---

# 像圈覆盖比

## 公式
$$ \text{Coverage} = \left(\frac{\text{IC}}{D_{\text{sensor}}}\right)^2 $$

## 变量与单位
| 变量 | 含义 | 单位 |
|------|------|------|
| $\text{Coverage}$ | 像圈覆盖比 | 无量纲 |
| $\text{IC}$ | 镜头像圈直径 | mm |
| $D_{\text{sensor}}$ | 传感器对角线 | mm |

## 适用条件
- 评估镜头像圈是否完全覆盖传感器
- 镜头选型时的匹配性判断
- 基于面积比来评估光能利用和渐晕程度

## 判断标准
| 覆盖比 | 评价 |
|--------|------|
| $\geq 1.0$ | 完全覆盖，无渐晕 |
| $0.8 - 1.0$ | 轻微渐晕，边缘亮度下降 |
| $< 0.8$ | 严重渐晕，边缘不可用 |

## 推导或解释
像圈是镜头能够成像的清晰区域。若像圈直径小于传感器对角线，传感器四角会接收不到光线，产生渐晕。采用面积比（直径比的平方）能更直观反映光通量损失程度。

## 验证样例
像圈 $\text{IC} = 11\,\text{mm}$，传感器对角线 $D_{\text{sensor}} = 8\,\text{mm}$（1/2" 传感器）：

$$ \text{Coverage} = \left(\frac{11}{8}\right)^2 = (1.375)^2 \approx 1.89 $$

覆盖比远大于 1.0，说明该镜头完全覆盖此传感器，无渐晕风险。若 $\text{IC} = 6\,\text{mm}$，则 $\text{Coverage} = (6/8)^2 = 0.56$，属于严重渐晕。

## 关键关系
- 相关概念：[[10-concepts/像圈|像圈]]、[[10-concepts/渐晕|渐晕]]
- 相关教程：[[50-learning/05-matching-basics|第5章]]

## 可视化辅助

![[attachments/visuals/image-circle-coverage.svg]]
*图：Image Circle Coverage*

## 来源

## 关联实验

- [[90-maps/Optics Lab#sensor-coverage|像圈与传感器覆盖实验]] — 调整传感器尺寸和镜头像圈，观察覆盖率与渐晕区域。
