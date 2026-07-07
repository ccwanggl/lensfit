---
id: module.geometric
title: 模块乙｜几何光学与一阶成像
type: module
domains: []
status: draft
---

# 模块乙｜几何光学与一阶成像

## 模块目标

能用光线模型解释成像，掌握典型系统结构与一阶光学设计能力。

## 先修知识

- [[../10-foundations/README|模块甲｜桥接]]（必修）

## 核心概念（25个）

| 概念 | 说明 |
|------|------|
| [[../../10-concepts/focal-length\|焦距]] | 平行光线经透镜汇聚点到光心的距离 |
| [[../../10-concepts/f-number\|F值]] | 焦距与入瞳直径之比，表征通光量 |
| [[../../10-concepts/image-circle\|像圈]] | 镜头能覆盖的有效成像区域直径 |
| [[../../10-concepts/depth-of-field\|景深]] | 成像保持可接受清晰度的物空间深度范围 |
| [[../../10-concepts/numerical-aperture\|NA]] | 数值孔径，衡量光学系统集光能力 |
| [[../../10-concepts/magnification\|放大率]] | 像高与物高之比，描述成像缩放 |
| [[../../10-concepts/field-of-view\|视场]] | 光学系统能观察到的物空间范围 |
| [[../../10-concepts/angle-of-view\|视角]] | 视场在像方对应的张角 |
| [[../../10-concepts/aperture-stop\|孔径光阑]] | 限制光束截面积的实际物理孔径 |
| [[../../10-concepts/entrance-exit-pupil\|入瞳/出瞳]] | 孔径光阑在物方/像方共轭的像 |
| [[../../10-concepts/paraxial-approximation\|近轴近似]] | 小角度假设下光线追迹的简化模型 |
| [[../../10-concepts/spherical-aberration\|球差]] | 轴上物点因孔径不同导致的光线汇聚差异 |
| [[../../10-concepts/coma\|彗差]] | 轴外物点因不对称孔径导致的彗星状像斑 |
| [[../../10-concepts/astigmatism\|像散]] | 轴外物点子午与弧矢面焦距不同导致的像差 |
| [[../../10-concepts/field-curvature\|场曲]] | 平坦物面成像在曲面上的像差 |
| [[../../10-concepts/distortion\|畸变]] | 放大率随视场变化导致的图像变形 |
| [[../../10-concepts/chromatic-aberration\|色差]] | 不同波长光线焦距不同导致的色边 |
| [[../../10-concepts/thin-lens\|薄透镜]] | 厚度可忽略的理想化透镜模型 |
| [[../../10-concepts/doublet\|双透镜]] | 两片透镜胶合用于校正色差 |
| [[../../10-concepts/telecentricity\|远心]] | 主光线平行于光轴的成像特性 |
| [[../../10-concepts/perspective-distortion\|透视畸变]] | 因拍摄距离与视角导致的透视变形 |
| [[../../10-concepts/parallax\|视差]] | 不同观察点导致的目标位置差异 |
| [[../../10-concepts/flange-distance\|法兰距]] | 镜头安装基准面到像平面的距离 |
| [[../../10-concepts/c-mount\|C-mount]] | 工业镜头常用螺纹接口标准 |
| [[../../10-concepts/matching-basics\|匹配基础]] | 镜头与传感器、接口的兼容性原则 |

## 学习内容索引

| 章节 | 链接 | 内容概要 |
|------|------|----------|
| 几何光学 | [[../../50-learning/002-geometric-optics\|几何光学]] | 光线追迹、反射/折射定律、成像作图法 |
| 镜头参数 | [[../../50-learning/003-lens-parameters\|镜头参数]] | 焦距、F值、视场、工作距离、分辨率 |
| 传感器 | [[../../50-learning/004-sensors\|传感器]] | CCD/CMOS 原理、像素尺寸、像元与奈奎斯特极限 |
| 匹配基础 | [[../../50-learning/005-matching-basics\|匹配基础]] | 镜头与传感器分辨率匹配、放大率匹配 |
| 像差（上） | [[./learning/06a-geometric-aberrations\|像差（上）｜几何像差入门]] | 色差、球差、彗差、像散——几何像差的直觉与入门 |
| 像差（下） | [[../50-optical-design/learning/06b-wavefront-aberrations\|像差（下）｜高阶像差与设计关联]] | 场曲、畸变、校正等级、常见误区——设计视角的像差分析 |
| 接口与安装 | [[../../50-learning/007-interfaces-and-mounts\|接口与安装]] | C-mount、F-mount、法兰距、背焦距离 |
| 照明几何设计 | [[../../modules/20-geometric-optics/learning/13a-illumination-geometry\|照明几何设计与布局]] | 照明方式、均匀性、频闪同步、镜头配合 |
| 领域应用 | [[../../50-learning/008-domain-applications\|领域应用]] | 机器视觉、显微成像、摄影光学 |

## 三本账指引

- **概念账**：掌握光线追迹原理、近轴近似适用范围、各像差的产生机理与视觉表现。理解孔径光阑、入瞳/出瞳的共轭关系，以及远心光路的工程价值。
- **计算账**：熟练使用薄透镜公式、牛顿公式、放大率公式进行一阶光学计算。能根据传感器尺寸和视场要求反推焦距，估算景深与NA，进行基本的镜头-传感器匹配计算。
- **项目账**：完成「一阶光学系统设计」项目——根据给定的传感器尺寸（如 1/2"）、工作距离和视场要求，选择合适的焦距，计算F值与景深，绘制光路草图，并评估所需的像差校正级别。

## 下一模块

→ [[../30-wave-optics/README|模块丙｜波动光学]] 或 [[../40-spectroscopy/README|模块丁｜光谱学]]

（模块丙侧重波动光学与干涉/衍射；模块丁侧重光谱分析与色散系统。两条路径可独立学习，均依赖本模块基础。）
