---
id: concept.hyperspectral-imaging
title: 高光谱成像
type: concept
domains:
- spectroscopy
status: reviewed
aliases:
- hyperspectral-imaging
- 高光谱
- HSI
- 成像光谱
---

# 高光谱成像

## 定义

高光谱成像（Hyperspectral Imaging）是指使用**连续窄波段（数十到数百个）**对场景进行成像的技术，形成包含二维空间信息和一维光谱信息的**数据立方体（Data Cube）**。

每个像素点都包含一条完整的光谱曲线，因此高光谱成像也被称为“成像光谱学（Imaging Spectroscopy）”。

## 直观理解

想象在普通照片（RGB）的每个像素上“长”出一条光谱曲线：
- 传统彩色照片：每个像素有 3 个数值（R, G, B）。
- 高光谱图像：每个像素有 100+ 个数值（从 400 nm 到 1000 nm，每 5 nm 一个值）。
- 数据立方体：两个空间轴（x, y）+ 一个光谱轴（λ）。

## 关键参数/公式

| 参数 | 说明 | 典型值 |
|------|------|--------|
| 波段数 | 光谱通道数量 | 数十 ~ 数百 |
| 光谱分辨率 | 单个波段带宽 | 1 ~ 10 nm |
| 光谱范围 | 覆盖的波长范围 | 400 ~ 1000 nm（可见-近红外） |
| 数据立方体大小 | 空间 × 空间 × 光谱 | 如 1024 × 1024 × 224 |
| 光谱采样间隔 | 相邻波段中心波长差 | 约等于光谱分辨率 |

常用分析方法：
- 光谱角匹配（SAM）
- 光谱特征拟合
- 机器学习分类

## 适用场景

- **遥感**：矿物识别、植被类型、环境监测、军事侦察。
- **精准农业**：作物营养、病害、水分胁迫早期诊断。
- **食品检测**：异物、掺假、品质无损检测。
- **医学**：组织氧合、肿瘤边界检测。
- **工业**：材料成分、涂层均匀性检测。
- **考古/艺术**：颜料成分分析、真伪鉴定。

## 关键关系

- 相关概念：[[./072-multispectral-imaging|多光谱成像]]（波段少、离散）
- 相关概念：[[./074-spectral-resolution|光谱分辨率]]
- 相关概念：[[./066-spectral-power-distribution|光谱分布函数]]（每个像素的光谱曲线）
- 相关领域：[[../30-domains/005-on-chip-multispectral|片上多光谱成像]]（集成化实现方向）
- 相关设备：[[../40-devices/012-hyperspectral-camera|高光谱相机]]（推扫式、快照式）
- 相关领域：[[../30-domains/004-spectroscopy|光谱学领域]]
- 相关教程：[[50-learning/016-spectroscopy|光谱学]]
- 相关文献：[[../80-sources/009-on-chip-multispectral-literature|片上多光谱/高光谱文献雷达]]

## 常见误区

1. **高光谱数据量巨大**：一个数据立方体可达数百 MB，对存储和计算要求高。
2. **波段连续 ≠ 无间隙**：部分系统有微小间隙或重叠，需查看具体参数。
3. **空间分辨率与光谱分辨率矛盾**：光谱分辨率提高通常需要更宽狭缝，降低空间分辨率。
4. **高光谱不是“更彩色的照片”**：其信息维度远超人眼感知，需要光谱分析算法提取信息。
5. **所有像素光谱可比较**：光照不均匀、大气散射等会降低像素间可比性，需预处理。

## 可视化辅助

![[attachments/visuals/multispectral-hyperspectral.svg]]
*图：Multispectral Hyperspectral*

## 教材参考

- [[../80-sources/002-hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/003-saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]]：适合核对探测器、光与物质相互作用、光子学器件和现代光学系统。
- [[../80-sources/001-Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 来源

- 光学工程教材，第 16 章 光谱学
- Spectral Imaging: A Comprehensive Guide (Goetz)
