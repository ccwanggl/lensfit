---

id: sources.textbook-index
title: 教材索引
type: source-index
status: reviewed
source_type: textbook-index
aliases:
  - Textbook Index
  - 光学教材索引
---

# 教材索引

本页用于回答两个问题：

1. 某个光学知识点应该查哪本教材。
2. 不同教材的强项、弱项和适用阶段有什么区别。

页码采用保守策略：只有核对过实体书、合法电子书或出版社预览的页码，才写入精确页码。当前没有本地教材文件，因此本页先建立教材级和章节级索引；精确页码统一在 [[Textbook Reference Matrix|教材页码索引矩阵]] 中逐步核验。

## 教材对比

| 教材 | 推荐阶段 | 强项 | 弱项 | 最适合查什么 |
|---|---|---|---|---|
| [[hecht-optics-5e\|Eugene Hecht, *Optics*, 5th ed.]] | 入门到进阶 | 覆盖面广，几何光学、波动光学、干涉、衍射、偏振、傅里叶光学都有系统叙述 | 篇幅大，文字密度高，不适合只想快速做工程选型的人 | 光的本质、几何光学、干涉、衍射、偏振、相干性 |
| [[saleh-teich-fundamentals-photonics-3e\|Bahaa E. A. Saleh & Malvin C. Teich, *Fundamentals of Photonics*, 3rd ed.]] | 进阶到深入 | 工程和物理结合好，覆盖射线光学、波动光学、电磁光学、光与物质、激光、探测器、光纤等 | 内容很厚，初学者容易迷路 | 光子学体系、探测器、激光、光纤、现代光学器件 |
| [[goodman-introduction-fourier-optics-4e\|Joseph W. Goodman, *Introduction to Fourier Optics*, 4th ed.]] | 进阶专项 | 傅里叶光学经典教材，适合系统学习衍射、成像、空间频率、全息和光学信息处理 | 前置数学要求高，不适合作为第一本光学书 | 衍射、傅里叶变换、OTF/MTF、空间频率、全息 |
| [[smith-modern-optical-engineering-4e\|Warren J. Smith, *Modern Optical Engineering*, 4th ed.]] | 工程实践 | 光学系统设计工程味很强，覆盖成像、基本光学器件、像质评价、制造与测试 | 偏系统设计，不负责从零解释全部物理基础 | 镜头系统设计、像差、像质评价、工程约束 |
| [[wyszecki-stiles-color-science-2e\|Wyszecki & Stiles, *Color Science*, 2nd ed.]] | 色彩专项 | 色度学、标准光源、色匹配函数和颜色测量数据系统 | 不适合作为光学入门书，偏资料库 | 色度图、色温、颜色差异、标准光源 |
| [[gonzalez-woods-digital-image-processing-4e\|Gonzalez & Woods, *Digital Image Processing*, 4th ed.]] | 图像处理专项 | 采样、量化、边缘检测、滤波和频域处理讲得系统 | 不负责解释镜头和光学传播 | 混叠、边缘检测、数字图像处理链路 |
| [[driggers-infrared-electro-optical-systems-3e\|Driggers et al., *Introduction to Infrared and Electro-Optical Systems*, 3rd ed.]] | 红外专项 | 红外探测器、NETD、EO/IR 系统性能评价更贴近工程 | 不覆盖通用可见光成像全链路 | NETD、发射率、微测辐射热计、红外系统指标 |

## 选书建议

| 目标 | 首选 | 辅助 |
|---|---|---|
| 光学小白建立基础 | Hecht | 本知识库第0-9章 |
| 机器视觉工程选型 | Smith | Hecht 的几何光学与像差章节 |
| 理解 MTF、PSF、傅里叶成像 | Goodman | Hecht 的衍射与傅里叶光学章节 |
| 学探测器、激光、光纤、现代器件 | Saleh & Teich | Hecht 的波动光学基础 |
| 学光谱和颜色 | Hecht + Saleh & Teich | Wyszecki & Stiles 与 CIE 标准 |
| 学图像采样和边缘检测 | Goodman | Gonzalez & Woods |
| 学红外成像系统 | Driggers et al. | Saleh & Teich 的探测器章节 |

## 教材到知识库的入口

| 知识库主题 | 推荐教材顺序 |
|---|---|
| 光与波 | Hecht → Saleh & Teich |
| 几何光学 | Hecht → Saleh & Teich → Smith |
| 镜头参数与像差 | Hecht → Smith |
| 传感器与探测器 | Saleh & Teich → Smith |
| 衍射、相干、傅里叶光学 | Hecht → Goodman |
| MTF、OTF、图像质量 | Goodman → Smith |
| 光学系统工程设计 | Smith → Saleh & Teich |
| 光谱学与色彩科学 | Hecht → Saleh & Teich；色彩测量查 Wyszecki & Stiles |
| 红外成像与热探测 | Driggers et al. → Saleh & Teich |
| 数字图像处理 | Gonzalez & Woods → Goodman |

## 官方/可核验来源

| 教材 | 官方或权威链接 | 当前可确认信息 |
|---|---|---|
| Hecht, *Optics*, 5th ed. | [Pearson: Optics, Fifth Edition](https://www.pearson.com/en-ca/subject-catalog/p/optics/P200000006793?view=educator) | 出版社页面确认第5版和目录入口 |
| Saleh & Teich, *Fundamentals of Photonics*, 3rd ed. | [Wiley: Fundamentals of Photonics, 3rd Edition](https://www.wiley.com/en-gb/shop/general-physics/fundamentals-of-photonics-2-volume-set-3rd-edition-p-9781119506874) | 出版社页面确认第3版、双卷本和章节目录 |
| Goodman, *Introduction to Fourier Optics*, 4th ed. | [Macmillan Learning](https://www.macmillanlearning.com/college/us/product/Introduction-to-Fourier-Optics/p/1319119166) | 出版社页面确认第4版；Google Books 可确认书目信息 |
| Smith, *Modern Optical Engineering*, 4th ed. | [McGraw Hill](https://www.mheducation.com/highered/mhp/product/modern-optical-engineering-4e-pb.html)；[SPIE Book Record](https://spie.org/Publications/Book/781851) | 出版社/书目页面确认第4版，覆盖光学工程、成像、像质评价等 |
| Wyszecki & Stiles, *Color Science*, 2nd ed. | [Wiley: Color Science, 2nd Edition](https://www.wiley.com/en-us/Color%2BScience%3A%2BConcepts%2Band%2BMethods%2C%2BQuantitative%2BData%2Band%2BFormulae%2C%2B2nd%2BEdition-p-9780471399186) | 出版社页面确认第2版，覆盖色彩科学概念、方法、数据和公式 |
| Gonzalez & Woods, *Digital Image Processing*, 4th ed. | [ImageProcessingPlace: Digital Image Processing, 4th edition](https://www.imageprocessingplace.com/DIP-4E/dip4e_main_page.htm) | 作者/教材页面确认第4版，覆盖数字图像处理基础 |
| Driggers et al., *Introduction to Infrared and Electro-Optical Systems*, 3rd ed. | [Artech House](https://us.artechhouse.com/Introduction-to-Infrared-and-Electro-Optical-Systems-Third-Edition-P2271.aspx) | 出版社页面确认第3版，覆盖红外和电光系统 |

## 后续应补教材

| 方向 | 候选教材/来源 | 原因 |
|---|---|---|
| 光谱仪器 | 光谱仪/光栅厂商手册、仪器分析教材 | 当前光栅、棱镜、光谱分辨率需要工程页码 |
| 机器视觉照明 | 机器视觉光源厂商应用手册 | 照明选型更依赖工程手册而不是通用光学教材 |
| 色彩标准 | CIE 标准文档 | Wyszecki & Stiles 可支撑教材层，标准值仍应回到 CIE |
| 红外器件参数 | 红外探测器厂商应用手册 | Driggers 可支撑系统层，具体器件参数仍应查厂商 |

## 维护规则

- 不同版本单独记录，不混用页码。
- “章节可确认”和“页码可确认”分开标记。
- 页码未核验时，宁可写“待核验”，不要写估计页。
- 每次给知识笔记补页码时，同时更新 [[Textbook Reference Matrix|教材页码索引矩阵]]。
