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
| ![[attachments/visuals/thin-lens-geometry.svg]] | [[10-concepts/focal-length\|焦距]]、[[20-formulas/thin-lens-gauss\|薄透镜高斯公式]] |
| ![[attachments/visuals/angle-of-view.svg]] | [[10-concepts/focal-length\|焦距]]、[[20-formulas/angle-of-view\|视角公式]] |
| ![[attachments/visuals/image-circle-coverage.svg]] | [[10-concepts/image-circle\|像圈]]、[[20-formulas/coverage-ratio\|像圈覆盖比]] |
| ![[attachments/visuals/aperture-f-number.svg]] | [[10-concepts/f-number\|F值]] |
| ![[attachments/visuals/depth-of-field.svg]] | [[10-concepts/depth-of-field\|景深]] |
| ![[attachments/visuals/airy-disk.svg]] | [[10-concepts/airy-disk\|艾里斑]] |
| ![[attachments/visuals/nyquist-aliasing.svg]] | [[10-concepts/nyquist-frequency\|奈奎斯特频率]] |
| ![[attachments/visuals/refractive-index.svg]] | [[10-concepts/refractive-index\|折射率]] |
| ![[attachments/visuals/dispersion.svg]] | [[10-concepts/dispersion\|色散]] |
| ![[attachments/visuals/chromatic-aberration.svg]] | [[10-concepts/chromatic-aberration\|色差]] |

---

## 光谱与成像技术

| 图 | 对应笔记 |
|---|---|
| ![[attachments/visuals/color-temperature.svg]] | [[10-concepts/color-temperature\|色温]] |
| ![[attachments/visuals/spectral-power-distribution.svg]] | [[10-concepts/spectral-power-distribution\|光谱功率分布]] |
| ![[attachments/visuals/multispectral-hyperspectral.svg]] | [[10-concepts/multispectral-imaging\|多光谱成像]]、[[10-concepts/hyperspectral-imaging\|高光谱成像]] |
| ![[attachments/visuals/fluorescence.svg]] | [[10-concepts/fluorescence\|荧光]] |
| ![[attachments/visuals/raman-scattering.svg]] | [[10-concepts/raman-scattering\|拉曼散射]] |

---

## 设备与器件

| 图 | 对应笔记 |
|---|---|
| ![[attachments/visuals/telecentricity.svg]] | [[40-devices/telecentric-lens\|远心镜头]] |
| ![[attachments/visuals/global-vs-rolling-shutter.svg]] | [[10-concepts/全局快门\|全局快门]]、[[10-concepts/卷帘快门\|卷帘快门]] |

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
3. 在对应的概念/公式/学习章节中用 `![[attachments/visuals/xxx.svg]]` 嵌入。
