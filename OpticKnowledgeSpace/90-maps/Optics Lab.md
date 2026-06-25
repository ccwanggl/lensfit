---
id: map.optics-lab
title: 光学实验室
type: map
status: reviewed
aliases:
  - Optics Lab
  - 实验室
---

# 光学实验室

本页汇总 LensFit 中所有可交互的光学实验。每个实验都与知识库中的概念/公式笔记双向链接，你可以在阅读笔记后打开实验，通过调整参数来建立直觉。

> 在 LensFit 桌面应用中，点击顶部导航栏的「光学实验室」即可运行这些实验。

---

## 实验目录

### 像圈与传感器覆盖实验

- **难度**: 基础
- **说明**: 调整传感器尺寸和镜头像圈，观察覆盖率与渐晕区域。
- **学习目标**: 理解像圈直径必须大于传感器对角线才能无渐晕。, 观察四角超出像圈时出现的渐晕区域。
- **关联笔记**: [[10-concepts/image-circle|image-circle]], [[20-formulas/coverage-ratio|coverage-ratio]], [[10-concepts/渐晕|渐晕]]

### 光谱混色实验

- **难度**: 基础
- **说明**: 混合两种单色光，观察合成光谱和感知颜色。
- **学习目标**: 理解颜色是光谱分布在人眼中的综合感知。, 观察两种单色光混合后如何产生新的色相。
- **关联笔记**: [[10-concepts/spectral-power-distribution|spectral-power-distribution]], [[10-concepts/color-temperature|color-temperature]], [[10-concepts/chromaticity-diagram|chromaticity-diagram]], [[10-concepts/色温|色温]]

### 放大倍率与像素精度实验

- **难度**: 基础
- **说明**: 给定焦距、工作距离和像元尺寸，计算横向放大倍率、像素精度及物体特征在传感器上占据的像素数。
- **学习目标**: 理解放大倍率 β = f / (WD - f) 的物理意义。, 认识像素精度 = 像元尺寸 / |β|。, 估算物体特征在成像平面上占据的像素数。
- **关联笔记**: [[10-concepts/像素精度|像素精度]], [[10-concepts/工作距离|工作距离]], [[10-concepts/focal-length|focal-length]], [[20-formulas/lateral-magnification|lateral-magnification]], [[20-formulas/pixel-precision|pixel-precision]], [[20-formulas/focal-length-from-wd|focal-length-from-wd]]

### 斯涅尔定律与全反射实验

- **难度**: 基础
- **说明**: 改变入射角和两种介质的折射率，观察折射、反射和全反射现象。
- **学习目标**: 掌握 n₁ sin θ₁ = n₂ sin θ₂ 的折射定律。, 认识光从光密介质到光疏介质时的全反射临界角。, 了解反射率随入射角的变化趋势。
- **关联笔记**: [[10-concepts/refractive-index|refractive-index]], [[10-concepts/dispersion|dispersion]], [[10-concepts/色散|色散]]

### 景深实验

- **难度**: 基础
- **说明**: 给定焦距、光圈、对焦距离和传感器参数，计算景深的前后界限和超焦距。
- **学习目标**: 理解光圈、焦距和对焦距离如何共同影响景深。, 认识超焦距的意义及其与景深远/近界的关系。
- **关联笔记**: [[10-concepts/depth-of-field|depth-of-field]], [[10-concepts/f-number|f-number]]

### 薄透镜成像实验

- **难度**: 基础
- **说明**: 改变焦距和物距，观察像距、放大倍率和光路图的变化。
- **学习目标**: 理解 1/f = 1/u + 1/v 的物像关系。, 观察物距接近焦距时像距趋向无穷远。, 认识放大率与物距、焦距的关系。
- **关联笔记**: [[10-concepts/focal-length|focal-length]], [[20-formulas/thin-lens-gauss|thin-lens-gauss]], [[10-concepts/焦距|焦距]]

### 视角与传感器尺寸实验

- **难度**: 基础
- **说明**: 给定焦距和传感器尺寸，观察水平、垂直、对角线视角的变化。
- **学习目标**: 理解视角同时取决于焦距和传感器尺寸。, 比较同一焦距在不同传感器上的视野差异。
- **关联笔记**: [[10-concepts/focal-length|focal-length]], [[10-concepts/焦距|焦距]], [[20-formulas/angle-of-view|angle-of-view]]

### 圆孔衍射与艾里斑

- **难度**: 进阶
- **说明**: 改变波长和光圈孔径，观察艾里斑大小和衍射图样的变化。
- **学习目标**: 理解艾里斑是理想光学系统的极限点扩散函数。, 观察光圈越小、波长越长，艾里斑越大。
- **关联笔记**: [[10-concepts/airy-disk|airy-disk]], [[10-concepts/衍射极限|衍射极限]], [[20-formulas/rayleigh-criterion|rayleigh-criterion]], [[10-concepts/艾里斑|艾里斑]]

### 奈奎斯特采样与混叠实验

- **难度**: 进阶
- **说明**: 比较镜头 MTF50 与传感器奈奎斯特频率，判断是否存在混叠风险或过度采样。
- **学习目标**: 理解传感器奈奎斯特频率是它能无歧义记录的最高空间频率。, 认识镜头 MTF50 超过奈奎斯特频率时会出现混叠。, 了解过度采样与欠采样的权衡。
- **关联笔记**: [[10-concepts/nyquist-frequency|nyquist-frequency]], [[10-concepts/奈奎斯特频率|奈奎斯特频率]], [[10-concepts/aliasing|aliasing]], [[10-concepts/混叠|混叠]]

---

## 如何新增实验

1. 在后端创建 `engine/lensfit/lab/experiments/<your-experiment>.py` 并继承 `OpticsExperiment`。
2. 声明 `linked_concepts` 指向本知识库的笔记路径。
3. 运行 `python scripts/sync_experiment_links.py` 更新本页和关联笔记。

详见架构文档：`docs/development/plans/optics-lab-architecture.md`。
