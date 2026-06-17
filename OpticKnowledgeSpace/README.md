---
id: knowledge.home
title: LensFit 光学知识库
type: map
status: maintained
aliases:
  - Knowledge Home
---

# LensFit 光学知识库

本目录是 LensFit 的 Obsidian Vault，用于维护成像光学概念、公式、领域知识、学习教程和资料来源。Git 是版本事实源，Obsidian 用于编辑、双链、检索和关系浏览。

研发过程、软件架构、计划和审查记录位于 [docs](../docs/README.md)。

## 开始使用

1. 在 Obsidian 中选择“打开本地仓库”。
2. 选择仓库中的 `OpticKnowledgeSpace/` 目录作为 Vault。
3. 从 [[90-maps/Learning Path|从零到深入学习路径]]、[[90-maps/Knowledge Architecture|知识库架构]] 或 [[90-maps/Knowledge Map|知识地图]] 开始；视觉学习者先看 [[90-maps/Visual Learning Toolkit|视觉学习工具箱]]。
4. 新笔记先放入 `00-inbox/`，整理后再移动到正式目录。

## 目录

| 目录 | 内容 | 阶段 |
|---|---|---|
| `00-inbox/` | 待分类、待核验的临时笔记 | — |
| `10-concepts/` | 核心概念原子笔记（折射率、艾里斑、焦距、像圈、奈奎斯特频率等） | 入门/进阶 |
| `20-formulas/` | 公式与计算模型原子笔记（薄透镜、视角、奈奎斯特、覆盖比等） | 入门/进阶 |
| `30-domains/` | 工业视觉、摄影、显微镜、红外成像、光谱成像 | 领域深入 |
| `40-devices/` | 设备类型、接口和选型知识（镜头、传感器、光源、探测器、光谱设备） | 工程实践 |
| `50-learning/` | 按顺序阅读的完整教程（16章：入门→进阶→深入→实践→专项） | 主线学习 |
| `80-sources/` | 标准、论文、厂商资料和引用来源 | 参考 |
| `90-maps/` | 知识地图、知识架构和学习路径 | 导航 |
| `attachments/` | 图片、PDF 截图等附件 | 附件 |
| `templates/` | Obsidian 笔记模板 | 模板 |

## 学习路径总览

本知识库提供 **16章** 从入门到实践、再到专项深入的完整成像光学学习路径。完整路线见 [[90-maps/Learning Path|从零到深入学习路径]]，知识组织方式见 [[90-maps/Knowledge Architecture|知识库架构]]。

```
入门阶段（第0-9章）
  绪论 → 光与波 → 几何光学 → 镜头参数 → 传感器 → 匹配基础 → 像差 → 接口 → 领域应用 → 习题

进阶阶段（第10-13章）
  物理光学深入 → 光学设计基础 → 光学传递函数与图像质量 → 照明系统设计

前沿与实践阶段（第14-15章）
  计算光学与计算成像 → 工程案例与选型实战

专项深入（第16章）
  光谱学与色彩科学
```

## 推荐入口

| 入口 | 适合谁 | 用途 |
|---|---|---|
| [[90-maps/Learning Path|从零到深入学习路径]] | 初学者 | 按顺序学习，知道每阶段要掌握什么 |
| [[90-maps/Knowledge Architecture|知识库架构]] | 维护者/系统学习者 | 理解教程、概念、公式、设备和领域如何连接 |
| [[90-maps/Knowledge Map|知识地图]] | 查资料的人 | 快速跳转到概念、公式、设备和领域 |
| [[90-maps/Interactive Explorer|交互式探索器]] | 视觉/探索型学习者 | 用 D3 图谱或 Obsidian Canvas 拖拽浏览 |
| [[50-learning/README|学习教程目录]] | 顺序阅读者 | 查看 16 章主线目录 |

## 光谱学科专项

光谱学是光的"指纹"识别科学，涵盖：
- [[50-learning/16-spectroscopy|第16章：光谱学与色彩科学]] — 系统的光谱学学习章节
- [[30-domains/spectroscopy|光谱成像领域参考]] — 工业应用与选型
- 10 个光谱相关概念笔记（色散、色度图、色温、荧光、拉曼、多光谱、高光谱等）
- 5 个光谱相关公式（光栅方程、光谱分辨率、Delta E 等）
- 5 个光谱相关设备（光谱仪、高光谱相机、衍射光栅、滤光片、积分球）

## 内容状态

Frontmatter 的 `status` 使用以下值：

- `draft`：内容尚未整理完成。
- `reviewed`：已经过技术审阅。
- `verified`：公式、来源或样例已经验证。
- `maintained`：持续维护的导航页。
- `deprecated`：保留历史引用，不再作为现行知识。

## 可视化资源

为帮助视觉学习者，本库用 Python（matplotlib + networkx）生成了一组静态图解，已嵌入到对应的概念、公式和学习章节中：

| 图 | 说明 | 所在笔记 |
|---|---|---|
| `learning-path-roadmap.svg` | 16 章学习路径总览 | [[90-maps/Learning Path|从零到深入学习路径]] |
| `knowledge-graph.svg` | 核心知识关联图 | [[90-maps/Learning Path|从零到深入学习路径]] |
| `thin-lens-geometry.svg` | 薄透镜物距/像距/焦距关系 | [[10-concepts/focal-length\|焦距]]、[[20-formulas/thin-lens-gauss\|薄透镜高斯公式]] |
| `angle-of-view.svg` | 焦距与视角关系 | [[10-concepts/focal-length\|焦距]]、[[20-formulas/angle-of-view\|视角公式]] |
| `image-circle-coverage.svg` | 像圈与传感器覆盖 | [[10-concepts/image-circle\|像圈]]、[[20-formulas/coverage-ratio\|像圈覆盖比]]、[[50-learning/05-matching-basics\|匹配基础]] |
| `nyquist-aliasing.svg` | 采样不足导致的混叠 | [[10-concepts/nyquist-frequency\|奈奎斯特频率]]、[[20-formulas/nyquist-frequency\|奈奎斯特频率]] |
| `airy-disk.svg` | 艾里斑强度分布 | [[10-concepts/airy-disk\|艾里斑]] |
| `depth-of-field.svg` | 景深与弥散圆 | [[10-concepts/depth-of-field\|景深]] |
| `aperture-f-number.svg` | 光圈孔径与 F 值 | [[10-concepts/f-number\|F值]] |
| `refractive-index.svg` | 折射率与斯涅尔定律 | [[10-concepts/refractive-index\|折射率]] |
| `dispersion.svg` | 棱镜色散 | [[10-concepts/dispersion\|色散]] |
| `chromatic-aberration.svg` | 透镜色差 | [[10-concepts/chromatic-aberration\|色差]] |
| `color-temperature.svg` | 色温与黑体辐射 | [[10-concepts/color-temperature\|色温]] |
| `multispectral-hyperspectral.svg` | 多光谱 vs 高光谱 | [[10-concepts/multispectral-imaging\|多光谱]]、[[10-concepts/hyperspectral-imaging\|高光谱]] |
| `spectral-power-distribution.svg` | 光谱功率分布 | [[10-concepts/spectral-power-distribution\|SPD]] |
| `fluorescence.svg` | 荧光能级图 | [[10-concepts/fluorescence\|荧光]] |
| `raman-scattering.svg` | 拉曼散射能级图 | [[10-concepts/raman-scattering\|拉曼散射]] |
| `global-vs-rolling-shutter.svg` | 全局快门 vs 卷帘快门 | [[10-concepts/全局快门\|全局快门]]、[[10-concepts/卷帘快门\|卷帘快门]] |
| `telecentricity.svg` | 远心镜头主光线 | [[40-devices/telecentric-lens\|远心镜头]] |
| `domain-selection-map.svg` | 如何选择应用领域 | [[30-domains/README\|应用领域]]、[[90-maps/Visual Index\|可视化索引]] |
| `matching-workflow.svg` | LensFit 匹配工作流程 | [[50-learning/05-matching-basics\|匹配基础]] |
| `sensor-parameter-map.svg` | 传感器选型雷达图 | [[50-learning/04-sensors\|传感器]]、[[40-devices/README\|设备类型]] |
| `lens-selection-checklist.svg` | 镜头选型七步清单 | [[50-learning/03-lens-parameters\|镜头参数]]、[[50-learning/05-matching-basics\|匹配基础]] |

完整索引见 [[90-maps/Visual Index\|可视化索引]]。

如需重新生成，运行仓库根目录下的 `scripts/generate_vault_visuals.py`（依赖 `scripts/.venv-viz` 中的 matplotlib、networkx、scipy）。


## 维护规则

- `id` 是稳定标识，移动或重命名文件时不得修改。
- 公式必须写明变量、单位、适用条件和来源。
- 经验性结论应标明适用场景，不写成普遍规律。
- 厂商规格应记录来源和确认日期。
- 双链用于知识关系，程序运行时数据不直接依赖 Obsidian 私有语法。
- Dataview、Canvas 等插件只能改善编辑体验，不能成为唯一的数据来源。
