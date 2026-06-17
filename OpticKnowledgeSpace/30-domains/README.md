---
id: map.domains
title: 领域
type: map
status: maintained
aliases:
  - Domain Index
---

# 领域

领域笔记用于回答“同一套光学知识在不同应用里如何取舍”。它不替代概念、公式和设备笔记，而是把它们组合成工程判断。

## 已收录领域

| 领域 | 文件 | 核心问题 | 推荐先修 |
|---|---|---|---|
| 工业视觉 | [[industrial-vision|industrial-vision.md]] | 如何稳定检测、测量、定位 | 第1-8章、C-mount、远心镜头、照明 |
| 摄影 | [[photography|photography.md]] | 如何平衡焦段、光圈、景深、画质 | 焦距、F值、景深、MTF |
| 显微镜 | [[microscopy|microscopy.md]] | 如何在高倍率下获得足够分辨率和亮度 | NA、瑞利判据、显微镜物镜 |
| 红外成像 | [[infrared-imaging|infrared-imaging.md]] | 如何按波段、温度和探测器能力选型 | 黑体辐射、红外探测器 |
| 光谱成像 | [[spectroscopy|spectroscopy.md]] | 如何用波长维度识别材料和颜色 | 第16章、光谱仪、高光谱相机 |

## 学习顺序

1. 先读 [[../50-learning/08-domain-applications|第8章：领域应用]]，理解为什么不同领域的指标不同。
2. 再按目标领域阅读对应领域笔记。
3. 遇到参数和公式时回查 [[../20-formulas/README|公式目录]]。
4. 进入硬件选型时回查 [[../40-devices/README|设备与测量]]。

## 领域之间的关键差异

| 维度 | 工业视觉 | 摄影 | 显微镜 | 红外 | 光谱 |
|---|---|---|---|---|---|
| 第一目标 | 稳定检测 | 视觉表现 | 微小结构 | 热/红外信息 | 材料识别 |
| 核心约束 | 精度、节拍、照明 | 焦段、光圈、虚化 | NA、工作距离、照明 | 波段、NETD、材料 | 波段、分辨率、SNR |
| 常见风险 | 光源不稳定、景深不足 | 边缘像质、色差 | 衍射、样品制备 | 玻璃不透红外、发射率 | 数据量大、光源光谱不匹配 |

## 与学习路径的关系

- 初学者先走 [[../90-maps/Learning Path|从零到深入学习路径]]。
- 需要查领域取舍时，从本页进入具体领域。
- 需要查完整结构时，看 [[../90-maps/Knowledge Architecture|知识库架构]]。

## 可视化辅助

![[attachments/visuals/domain-selection-map.svg]]
*图：根据核心目标选择光学应用领域*
