---
id: map.visual-index
title: 可视化索引
type: map
status: reviewed
aliases:
  - Visual Index
  - 图解索引
---

# 可视化索引

本页汇总了知识库中所有由 Python 生成的静态图解，方便视觉学习者快速定位。

> 提示：Obsidian 中可直接查看 SVG；若想在浏览器或演示中单独打开，可访问 `attachments/visuals/` 目录下的同名文件。

---

## 学习路径与知识结构

| 图 | 适用场景 |
|---|---|
| ![[attachments/visuals/learning-path-roadmap.svg]] | 规划整体学习顺序 |
| ![[attachments/visuals/knowledge-graph.svg]] | 理解核心概念之间的关系 |
| ![[attachments/visuals/domain-selection-map.svg]] | 判断自己属于哪个应用领域 |

---

## 核心概念图解

| 图 | 对应笔记 |
|---|---|
| ![[attachments/visuals/thin-lens-geometry.svg]] | [[10-concepts/003-focal-length|焦距]]、[[20-formulas/000-thin-lens-gauss|薄透镜高斯公式]] |
| ![[attachments/visuals/angle-of-view.svg]] | [[10-concepts/003-focal-length|焦距]]、[[20-formulas/003-angle-of-view|视角公式]] |
| ![[attachments/visuals/image-circle-coverage.svg]] | [[10-concepts/009-image-circle|像圈]]、[[20-formulas/004-coverage-ratio|像圈覆盖比]] |
| ![[attachments/visuals/aperture-f-number.svg]] | [[10-concepts/005-f-number|F值]] |
| ![[attachments/visuals/depth-of-field.svg]] | [[10-concepts/007-depth-of-field|景深]] |
| ![[attachments/visuals/airy-disk.svg]] | [[10-concepts/027-airy-disk|艾里斑]] |
| ![[attachments/visuals/nyquist-aliasing.svg]] | [[10-concepts/038-nyquist-frequency|奈奎斯特频率]] |
| ![[attachments/visuals/refractive-index.svg]] | [[10-concepts/000-refractive-index|折射率]] |
| ![[attachments/visuals/dispersion.svg]] | [[10-concepts/017-dispersion|色散]] |
| ![[attachments/visuals/chromatic-aberration.svg]] | [[10-concepts/019-chromatic-aberration|色差]] |
| ![[attachments/visuals/abbe-number.svg]] | [[10-concepts/016-abbe-number|阿贝数]] |
| ![[attachments/visuals/numerical-aperture.svg]] | [[10-concepts/006-数值孔径|数值孔径]] |
| ![[attachments/visuals/vignetting.svg]] | [[10-concepts/057-渐晕|渐晕]] |
| ![[attachments/visuals/sensor-parameter-map.svg]] | [[10-concepts/061-读出噪声|读出噪声]]、[[10-concepts/062-NETD|NETD]]、[[10-concepts/063-微测辐射热计|微测辐射热计]] |

---

## 光谱与成像技术

| 图 | 对应笔记 |
|---|---|
| ![[attachments/visuals/color-temperature.svg]] | [[10-concepts/067-color-temperature|色温]] |
| ![[attachments/visuals/spectral-power-distribution.svg]] | [[10-concepts/066-spectral-power-distribution|光谱功率分布]] |
| ![[attachments/visuals/multispectral-hyperspectral.svg]] | [[10-concepts/072-multispectral-imaging|多光谱成像]]、[[10-concepts/073-hyperspectral-imaging|高光谱成像]] |
| ![[attachments/visuals/multispectral-filter-array.svg]] | [[10-concepts/076-multispectral-filter-array|多光谱滤光片阵列]] |
| ![[attachments/visuals/fluorescence.svg]] | [[10-concepts/070-fluorescence|荧光]] |
| ![[attachments/visuals/raman-scattering.svg]] | [[10-concepts/071-raman-scattering|拉曼散射]] |
| ![[attachments/visuals/chromaticity-diagram.svg]] | [[10-concepts/069-chromaticity-diagram|色度图]] |
| ![[attachments/visuals/spectral-resolution.svg]] | [[10-concepts/074-spectral-resolution|光谱分辨率]]、[[20-formulas/010-瑞利分辨率|瑞利分辨率]] |

---

## 设备与器件

| 图 | 对应笔记 |
|---|---|
| ![[attachments/visuals/telecentricity.svg]] | [[40-devices/001-telecentric-lens|远心镜头]] |
| ![[attachments/visuals/global-vs-rolling-shutter.svg]] | [[10-concepts/058-全局快门|全局快门]]、[[10-concepts/059-卷帘快门|卷帘快门]] |

---

## 工程与选型方法

| 图 | 用途 |
|---|---|
| ![[attachments/visuals/matching-workflow.svg]] | 理解 LensFit 自动匹配流水线的 7 个阶段 |
| ![[attachments/visuals/lens-selection-checklist.svg]] | 按清单逐项确认镜头选型 |
| ![[attachments/visuals/sensor-parameter-map.svg]] | 比较不同传感器在各维度上的取舍 |

---

## 如何新增/更新图解

所有 SVG 均由仓库根目录下的 `scripts/generate_vault_visuals.py` 生成，依赖 `scripts/.venv-viz/` 中的 matplotlib、networkx 与 scipy。

```bash
python scripts/generate_vault_visuals.py
```

新增图解后，建议：

1. 把图片保存到 `OpticKnowledgeSpace/attachments/visuals/`。
2. 在本索引表中添加一行，方便视觉学习者查找。
3. 在对应的概念/公式/学习章节中用图片嵌入语法嵌入，例如 `attachments/visuals/你的图.svg`（将 `你的图.svg` 替换为实际文件名）。
