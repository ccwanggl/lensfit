---
id: knowledge.map.on-chip-multispectral-topic
title: 片上多光谱专题地图
type: map
status: maintained
aliases:
  - On-chip Multispectral Topic
  - 片上多光谱专题
---

# 片上多光谱专题地图

这个专题从光谱成像走向芯片级实现，重点看“谱编码、探测、读出、重建和应用任务”如何一起工作。它适合需要跟踪片上多光谱、片上高光谱、微型光谱仪和红外多谱段探测的人。

## 主入口

- [[../30-domains/005-on-chip-multispectral|片上多光谱成像]]：专题主入口，讲系统模型、技术路线、工程权衡和前沿状态。
- [[../80-sources/009-on-chip-multispectral-literature|片上多光谱/高光谱文献雷达]]：论文、综述、检索关键词和季度跟踪字段。
- [[../40-devices/013-on-chip-spectral-sensor|片上光谱传感器]]：设备选型页，面向采购、样机评估和工程验证。

## 概念链路

| 顺序 | 笔记 | 作用 |
| --- | --- | --- |
| 1 | [[../10-concepts/072-multispectral-imaging|多光谱成像]] | 建立少数离散波段的基本概念 |
| 2 | [[../10-concepts/073-hyperspectral-imaging|高光谱成像]] | 理解连续窄波段和数据立方体 |
| 3 | [[../10-concepts/075-snapshot-spectral-imaging|快照式光谱成像]] | 理解为什么片上系统偏爱单帧或少帧采集 |
| 4 | [[../10-concepts/076-multispectral-filter-array|多光谱滤光片阵列]] | 理解 MSFA 和空间-光谱采样权衡 |
| 5 | [[../10-concepts/077-fabry-perot-microcavity|Fabry-Perot 微腔]] | 理解窄带滤波和红外焦平面集成 |
| 6 | [[../10-concepts/078-metasurface|超表面]] | 理解纳米结构谱编码和前沿路线 |
| 7 | [[../10-concepts/079-spectral-reconstruction|光谱重建]] | 理解响应矩阵、逆问题和算法代价 |
| 8 | [[../10-concepts/074-spectral-resolution|光谱分辨率]] | 回到指标，判断能否分开目标谱特征 |

## 设备链路

- [[../40-devices/012-hyperspectral-camera|高光谱相机]]：传统设备对照。
- [[../40-devices/013-on-chip-spectral-sensor|片上光谱传感器]]：片上方案选型。
- [[../40-devices/009-bandpass-filter|窄带滤光片]]：滤波阵列和通道设计基础。
- [[../40-devices/016-ingaas-focal-plane-array|InGaAs 焦平面阵列]]：SWIR 路线。
- [[../40-devices/017-mct-detector|MCT 探测器]]：MWIR/LWIR 高端探测器路线。
- [[../40-devices/015-ir-thermal-detector|红外热像仪探测器]]：LWIR 非制冷和热成像路线。

## 阅读路线

| 目标 | 推荐顺序 |
| --- | --- |
| 快速理解片上多光谱 | 片上多光谱成像 -> 片上光谱传感器 -> 多光谱滤光片阵列 -> 光谱重建 |
| 做工程选型 | 片上光谱传感器 -> 波段相关探测器 -> 窄带滤光片 -> 文献雷达中的同波段论文 |
| 跟踪前沿 | 文献雷达 -> 超表面 -> Fabry-Perot 微腔 -> 光谱重建 -> 片上多光谱成像 |
| 做红外多谱段 | 红外成像 -> InGaAs/MCT/红外热探测器 -> 片上多光谱成像的波段章节 -> 文献雷达红外论文 |

## 维护规则

- 新论文先进 [[../80-sources/009-on-chip-multispectral-literature|文献雷达]]，不要直接改成知识库结论。
- 只有影响系统模型、选型指标或工程边界的论文，才同步更新专题主入口。
- 概念页只写定义、边界、误区和教材/来源，不承载论文清单。
- 设备页只写选型参数、验证流程和风险，不展开完整技术史。
