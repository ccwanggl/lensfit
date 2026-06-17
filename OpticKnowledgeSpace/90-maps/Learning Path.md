---
id: knowledge.map.learning-path
title: 从零到深入学习路径
type: map
status: maintained
aliases:
  - Learning Path
  - 光学学习路径
---

# 从零到深入学习路径

这条路径面向“光学小白”：不要求先会高等光学，也不要求能读镜头规格书。目标是从直觉开始，逐步学到能看懂镜头、传感器、照明、像质、光谱和工程选型。

## 学习方法

每一章按四步走：

1. 先读主线章节，抓住直觉。
2. 遇到术语时跳到概念笔记，只看定义、边界和误区。
3. 遇到计算时跳到公式笔记，确认变量和单位。
4. 最后用领域或设备笔记，把知识放回工程场景。

不要一开始就追求“全懂”。光学的难点不是公式多，而是同一个词在不同场景里权重不同。

## 给视觉学习者的建议

如果你更擅长通过图像、关系图和流程图学习，推荐先阅读 [[90-maps/Visual Learning Toolkit|视觉学习工具箱]]，再按下面顺序使用本库：

1. **先看大图**：从 [[Knowledge Architecture|知识库架构]] 和下方的「学习路径总览图」了解整体结构。
2. **再进概念页**：每个概念笔记都尽量配图；遇到公式时，先看图再读变量定义。
3. **用关系图定位**：参考「核心知识关联图」，知道自己当前学的概念与哪些领域/设备相连。
4. **动手画**：把薄透镜、像圈覆盖、景深等图自己默画一遍，比背公式更有效。

![[attachments/visuals/learning-path-roadmap.svg]]
*图：LensFit 光学学习路径总览。建议先完成 0–9 章建立直觉，再进入进阶与专项。*

![[attachments/visuals/knowledge-graph.svg]]
*图：核心概念、公式、领域与设备的关系子集。节点颜色：绿色=概念，蓝色=公式，红色=领域，橙色=设备。*

![[attachments/visuals/domain-selection-map.svg]]
*图：不确定从哪个领域开始时，用这张图判断自己的核心目标对应哪个光学应用领域。*

> 全部图解的索引见 [[90-maps/Visual Index|可视化索引]]。

## 0. 准备阶段：知道自己在学什么

| 顺序 | 阅读 | 目标 |
|---|---|---|
| 0.1 | [[50-learning/00-introduction|绪论：走进成像光学]] | 知道成像系统由光源、物体、镜头、传感器和算法组成 |
| 0.2 | [[90-maps/Knowledge Architecture|知识库架构]] | 明确教程、概念、公式、设备、领域之间的关系 |

完成标志：能用自己的话解释“镜头选型不是只看焦距”。

## 1. 入门阶段：建立光学直觉

| 顺序 | 阅读 | 配套笔记 | 目标 |
|---|---|---|---|
| 1.1 | [[50-learning/01-light-and-waves|光与波]] | [[10-concepts/refractive-index|折射率]]、[[10-concepts/dispersion|色散]] | 理解光既有波长，也会折射、反射、衍射 |
| 1.2 | [[50-learning/02-geometric-optics|几何光学]] | [[20-formulas/thin-lens-gauss|薄透镜高斯公式]] | 会用物距、像距、焦距描述成像 |
| 1.3 | [[50-learning/03-lens-parameters|镜头参数]] | [[10-concepts/focal-length|焦距]]、[[10-concepts/f-number|F值]]、[[10-concepts/image-circle|像圈]] | 看懂镜头规格表的核心参数 |
| 1.4 | [[50-learning/04-sensors|传感器]] | [[10-concepts/pixel|像元]]、[[10-concepts/nyquist-frequency|奈奎斯特频率]] | 理解像元、分辨率、快门和采样极限 |

完成标志：给定视场、工作距离、传感器尺寸，能估算焦距范围。

## 2. 匹配阶段：把镜头和传感器配起来

| 顺序 | 阅读 | 配套笔记 | 目标 |
|---|---|---|---|
| 2.1 | [[50-learning/05-matching-basics|匹配基础]] | [[20-formulas/focal-length-from-wd|焦距反推公式]]、[[20-formulas/coverage-ratio|像圈覆盖比]] | 建立镜头-传感器匹配流程 |
| 2.2 | [[20-formulas/angle-of-view|视角公式]] | [[20-formulas/lateral-magnification|横向放大倍率]] | 会在视场、焦距、传感器尺寸之间换算 |
| 2.3 | [[20-formulas/pixel-precision|像素精度]] | [[20-formulas/oversampling-ratio|过采样率]] | 判断分辨率是被镜头限制还是被传感器限制 |
| 2.4 | [[50-learning/09-exercises|习题与练习]] | 按题目回查公式 | 巩固基本计算 |

完成标志：能判断一个组合是否存在像圈不足、视场不够、精度不够或过采样问题。

## 3. 像质阶段：知道为什么“不清楚”

| 顺序 | 阅读 | 配套笔记 | 目标 |
|---|---|---|---|
| 3.1 | [[50-learning/06-aberrations|像差]] | [[10-concepts/chromatic-aberration|色差]] | 理解清晰度、边缘颜色、畸变和场曲的来源 |
| 3.2 | [[10-concepts/airy-disk|艾里斑]] | [[20-formulas/airy-disk-diameter|艾里斑直径]] | 知道衍射带来的物理分辨极限 |
| 3.3 | [[20-formulas/rayleigh-criterion|瑞利判据]] | [[10-concepts/aliasing|混叠]] | 区分“光学分辨率”和“采样分辨率” |
| 3.4 | [[50-learning/12-otf-and-image-quality|光学传递函数与图像质量]] | [[10-concepts/nyquist-frequency|奈奎斯特频率]] | 进入 MTF、PSF、SNR 和图像质量评价 |

完成标志：看到一张模糊图，能初步区分是失焦、运动、衍射、像差、采样还是照明问题。

## 4. 工程阶段：进入真实系统

| 顺序 | 阅读 | 配套笔记 | 目标 |
|---|---|---|---|
| 4.1 | [[50-learning/07-interfaces-and-mounts|接口与安装]] | [[40-devices/c-mount-lens|C-mount镜头]] | 理解接口、法兰距、转接和机械安装 |
| 4.2 | [[50-learning/08-domain-applications|领域应用]] | [[30-domains/industrial-vision|工业视觉]]、[[30-domains/microscopy|显微镜]] | 认识不同领域的约束 |
| 4.3 | [[50-learning/13-illumination-design|照明系统设计]] | [[40-devices/led-ring-light|LED环形光源]]、[[40-devices/coaxial-illumination|同轴照明]]、[[40-devices/backlight|背光板]] | 知道光源常常比镜头更决定图像质量 |
| 4.4 | [[50-learning/15-engineering-cases|工程案例与选型实战]] | 按案例回查设备和公式 | 学会完整选型与问题诊断 |

完成标志：能为一个工业检测任务写出“需求参数 → 初选 → 校验 → 风险”的选型清单。

## 5. 进阶阶段：理解更深的物理

| 顺序 | 阅读 | 配套笔记 | 目标 |
|---|---|---|---|
| 5.1 | [[50-learning/10-physical-optics-advanced|物理光学深入]] | [[10-concepts/airy-disk|艾里斑]]、[[20-formulas/rayleigh-criterion|瑞利判据]] | 理解干涉、衍射、相干性 |
| 5.2 | [[50-learning/11-optical-design-basics|光学设计基础]] | [[10-concepts/abbe-number|阿贝数]]、[[10-concepts/chromatic-aberration|色差]] | 知道镜头结构为什么复杂 |
| 5.3 | [[50-learning/14-computational-optics|计算光学与计算成像]] | [[10-concepts/aliasing|混叠]] | 理解算法如何补偿或改变光学系统 |

完成标志：不再把“光学”和“算法”看成割裂的两件事。

## 6. 光谱专项：从颜色走向物质识别

如果目标是学习光谱，请按这条支线走：

| 顺序 | 阅读 | 配套笔记 | 目标 |
|---|---|---|---|
| 6.1 | [[50-learning/01-light-and-waves|光与波]] | [[10-concepts/dispersion|色散]] | 建立波长和色散基础 |
| 6.2 | [[10-concepts/spectral-power-distribution|光谱分布函数]] | [[20-formulas/planck-blackbody|普朗克黑体辐射公式]] | 理解光源光谱和色温 |
| 6.3 | [[50-learning/16-spectroscopy|光谱学与色彩科学]] | [[10-concepts/spectral-resolution|光谱分辨率]] | 系统学习光谱、色彩、荧光、拉曼 |
| 6.4 | [[20-formulas/grating-equation|光栅方程]] | [[20-formulas/grating-resolving-power|光栅光谱分辨率]]、[[20-formulas/prism-dispersion|棱镜色散率]] | 会估算分光角度和分辨率 |
| 6.5 | [[30-domains/spectroscopy|光谱成像]] | [[40-devices/spectrometer|光谱仪]]、[[40-devices/hyperspectral-camera|高光谱相机]] | 理解多光谱/高光谱设备选型 |
| 6.6 | [[10-concepts/chromaticity-diagram|色度图]] | [[20-formulas/delta-e|Delta E 色差]]、[[10-concepts/color-temperature|色温]] | 连接光谱测量和颜色管理 |

完成标志：能解释为什么 RGB 看起来相同的材料，光谱仪可能能区分。

## 7. 领域深入路线

| 目标 | 推荐阅读 |
|---|---|
| 工业视觉选型 | [[30-domains/industrial-vision|工业视觉]] → [[40-devices/c-mount-lens|C-mount镜头]] → [[40-devices/telecentric-lens|远心镜头]] → [[50-learning/15-engineering-cases|工程案例]] |
| 摄影系统理解 | [[30-domains/photography|摄影]] → [[10-concepts/f-number|F值]] → [[10-concepts/depth-of-field|景深]] → [[50-learning/12-otf-and-image-quality|图像质量]] |
| 显微成像 | [[30-domains/microscopy|显微镜]] → [[40-devices/microscope-objective|显微镜物镜]] → [[20-formulas/rayleigh-criterion|瑞利判据]] |
| 红外成像 | [[30-domains/infrared-imaging|红外成像]] → [[40-devices/ir-thermal-detector|红外热像仪探测器]] → [[20-formulas/planck-blackbody|黑体辐射]] |
| 光谱成像 | [[30-domains/spectroscopy|光谱成像]] → [[50-learning/16-spectroscopy|光谱学与色彩科学]] |

## 8. 学习检查表

入门完成后，你应该能回答：

- 焦距、视场、工作距离、传感器尺寸之间是什么关系？
- F 值同时影响曝光、景深和衍射，三者如何权衡？
- 像圈为什么必须覆盖传感器？
- 像元越小为什么不一定越好？
- 镜头很贵但图像仍然差，可能是哪些非镜头因素？

进阶完成后，你应该能回答：

- MTF 比“分辨率”更完整在哪里？
- 衍射极限和像差限制分别在什么情况下主导？
- 照明方式如何改变缺陷可见性？
- 为什么同一个物体在不同光源下颜色不同？
- 多光谱、高光谱、光谱仪分别适合什么任务？

## 9. 不建议的学习顺序

- 不建议直接从第16章开始学光谱。先读第1章，否则波长、色散、SPD 会缺直觉。
- 不建议先背公式。公式必须和变量、单位、适用条件一起学。
- 不建议只看设备笔记。设备参数必须回到应用目标，否则容易陷入规格堆叠。
- 不建议一开始追求 Zemax/Code V 级光学设计。先能做系统级选型，再进入专业设计软件。
