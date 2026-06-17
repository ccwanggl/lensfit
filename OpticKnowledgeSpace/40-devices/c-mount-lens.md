---

id: device.c-mount-lens
title: C-mount镜头
type: device
domains: []
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: []---

# C-mount镜头

## 定义/概述
工业视觉标准螺纹接口镜头，1"直径，32牙/英寸。

## 关键参数
| 参数 | 典型值 | 说明 |
|------|--------|------|
| 法兰距 | 17.526mm | 镜头安装基准到像面的距离 |
| 像圈 | 8–16mm | 必须覆盖传感器对角线 |

## 选型要点
- 确认像圈覆盖传感器：传感器对角线必须小于像圈直径
- 确认WD（工作距离）范围：不同镜头WD差异大
- 与CS-mount的区别：CS-mount法兰距为12.526mm，加5mm接圈可兼容

## 常见型号/品牌
（可选）

## 关键关系
- 相关概念：[[../10-concepts/像圈|像圈]]、[[10-concepts/法兰距|法兰距]]、[[../10-concepts/工作距离|工作距离]]
- 相关教程：[[50-learning/07-interfaces-and-mounts|第7章接口]]

## 常见误区
- **错误**：C-mount和CS-mount镜头可以随意互换使用
- **事实**：法兰距不同，直接互换会导致无法合焦；需使用接圈转换

## 来源
