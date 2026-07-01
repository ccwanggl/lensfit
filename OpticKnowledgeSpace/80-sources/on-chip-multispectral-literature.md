---
id: source.on-chip-multispectral-literature
title: 片上多光谱/高光谱文献与学习路线
type: source
domains: [spectroscopy, on-chip-multispectral]
status: reviewed
aliases:
  - 光谱探测入门
  - 片上多光谱综述
  - on-chip-multispectral-literature
---

# 光谱探测入门：红外分段、片上多光谱信息采集、成像与反演

> 版本：2026-06-26  
> 主题：光谱学科科普 + 红外 SWIR/MWIR/LWIR 分段 + 片上多光谱/高光谱论文清单  
> 说明：本文整理了前面对话中的讨论，并补充近五年代表性论文入口。文献获取部分只提供 DOI、出版商、Google Scholar、arXiv、PMC、Optica Open、作者主页等合法入口；不提供 Sci-Hub、盗版镜像或绕过付费墙的方法。

---

## 0. 一句话总览

光谱学研究的是：**光在不同波长上与物体发生了什么相互作用**。

普通相机主要得到二维图像：

[
I(x,y)
]

光谱成像得到的是三维数据立方体：

[
I(x,y,\lambda)
]

其中两维是空间位置，一维是波长。  
因此，光谱成像不仅能“看见形状”，还能进一步识别材料、成分、水分、温度、厚度、气体吸收、组织状态等信息。

片上多光谱/高光谱系统的核心思想是：

> **微纳光学结构负责对不同波长进行编码，探测器负责采样，算法负责解码与反演。**

---

## 1. 光谱学到底在看什么？

物体和光相互作用，常见形式包括：

- **吸收**：某些波长被材料吸收；
- **反射**：某些波长被反射回来；
- **透射**：某些波长穿过材料；
- **发射**：物体自身发出辐射；
- **散射**：颗粒、粗糙度、组织结构改变光的传播方向和强度。

所以光谱系统通常关注：

[
I(\lambda), \quad R(\lambda), \quad T(\lambda), \quad A(\lambda)
]

即光强、反射率、透过率、吸收率随波长的变化。

### 1.1 RGB、多光谱、高光谱的区别

| 类型  |    通道数 | 信息特点     | 典型用途             |
| --- | -----: | -------- | ---------------- |
| RGB |      3 | 红、绿、蓝宽通道 | 普通摄影、视觉显示        |
| 多光谱 | 几个到几十个 | 离散波段     | 农业、工业检测、遥感、材料分类  |
| 高光谱 | 数十到数百个 | 连续窄波段    | 定量光谱分析、成分反演、精细分类 |

多光谱更偏工程实用，高光谱更偏高维精细测量。  
片上化系统中，二者经常共用类似的硬件逻辑：**滤波/编码 + 探测 + 重建**。

---

## 2. 红外为什么分成短波、中波和长波？

红外分段不是随便命名，而是由三类因素共同决定：

1. **物体热辐射规律**：温度不同，主要辐射波长不同；
2. **大气透过窗口**：空气中的水汽、CO₂ 等会吸收某些红外波段；
3. **探测器和光学材料**：不同波段需要不同探测器、透镜材料、镀膜和制冷方案。

常见工程划分如下：

| 波段      | 英文      |                    常见范围 | 主要机制            | 典型探测器/材料             |
| ------- | ------- | ----------------------: | --------------- | -------------------- |
| 近红外     | NIR     |   0.7–1.0 或 0.75–1.4 μm | 接近可见光，部分硅探测器可响应 | Si CMOS/CCD          |
| 短波红外    | SWIR    | 0.9–1.7 μm；也常扩展到 2.5 μm | 反射成像为主          | InGaAs、量子点、扩展 InGaAs |
| 中波红外    | MWIR    |                  3–5 μm | 高温热辐射、气体吸收      | InSb、HgCdTe/MCT，常需制冷 |
| 长波红外    | LWIR    |                 8–14 μm | 常温物体热辐射         | 微测辐射热计、HgCdTe、QWIP 等 |
| 远红外/太赫兹 | FIR/THz |                15 μm 以上 | 低温、天文、材料振动等     | 专用探测器                |

---

## 3. SWIR、MWIR、LWIR 的核心区别

### 3.1 SWIR：短波红外

典型范围：**0.9–1.7 μm**，宽泛时可写作 **1–2.5 μm**。

SWIR 很多时候更像“不可见的反射光成像”，需要太阳光、环境光或主动照明。  
它的图像往往更接近普通灰度图，而不是热像图。

典型应用：

- 硅片、太阳能电池片缺陷检测；
- 食品、农产品水分和成熟度检测；
- 塑料、药片、矿物分类；
- 透雾、低照度、烟尘场景；
- 1550 nm 激光雷达、光通信、眼安全测距。

工程关键词：

> 反射率、主动照明、InGaAs、材料识别、水分反演、硅片透视。

---

### 3.2 MWIR：中波红外

典型范围：**3–5 μm**。

MWIR 对较高温目标的热辐射很敏感，同时很多气体在中红外有明显吸收峰。

典型应用：

- 发动机尾焰、导弹尾焰、飞机热源；
- 高温炉膛、金属热处理、玻璃制造；
- 火焰检测；
- 甲烷、CO₂、VOC 等气体检测；
- 高端红外制导与远距离热目标探测。

工程关键词：

> 高温辐射、气体吸收、MCT、InSb、制冷探测器、3–5 μm 大气窗口。

---

### 3.3 LWIR：长波红外

典型范围：**8–14 μm**。

常温物体的热辐射峰值大约在 10 μm 附近，因此 LWIR 是普通热像仪的核心波段。

典型应用：

- 人体、动物、车辆、建筑热成像；
- 电力巡检、设备发热、轴承/电机故障；
- 消防救援、烟雾穿透、搜救；
- 无人机热成像；
- 建筑节能、热泄漏检测；
- 光伏热斑检测。

工程关键词：

> 常温热辐射、热像仪、非制冷微测辐射热计、温度/发射率分离、8–14 μm 大气窗口。

---

## 4. 为什么片上多光谱重要？

传统光谱仪通常依赖光栅、棱镜、狭缝、扫描机构等，体积大、成本高、系统复杂。  
片上多光谱的目标是把“光谱能力”尽量做到芯片级、焦平面级或模组级。

片上化带来的价值：

- 体积小；
- 成本下降；
- 易与 CMOS/InGaAs/MCT/微测辐射热计阵列集成；
- 支持快照成像；
- 适合无人机、机器人、便携设备、医疗和工业在线检测；
- 可与深度学习/压缩感知/物理反演结合。

---

## 5. 片上多光谱信息采集的核心结构

片上光谱系统通常由五层组成：

### 5.1 光学耦合层

负责把场景光送到芯片：

- 微透镜；
- 光阑/孔径；
- 波导耦合；
- 金属透镜；
- 超表面；
- 滤光薄膜。

### 5.2 谱编码层

负责让不同波长产生不同响应：

- 多光谱滤光片阵列；
- Fabry–Pérot 微腔；
- 微环谐振器；
- 阵列波导光栅；
- 干涉结构；
- 超表面；
- 计算型随机编码结构。

### 5.3 探测层

将光转成电信号：

- Si CMOS：可见光到近红外；
- InGaAs：SWIR；
- InSb / HgCdTe：MWIR；
- 微测辐射热计：LWIR；
- 量子点、二维材料、新型半导体：新型片上探测器方向。

### 5.4 读出层

包括：

- 像素积分；
- ADC；
- 增益控制；
- 暗电流/固定图样噪声处理；
- 时序控制。

### 5.5 计算重建层

包括：

- 标定；
- 去噪；
- 光谱重建；
- 材料分类；
- 浓度/厚度/温度/发射率反演；
- 深度学习推理。

---

## 6. 主流技术路线

### 6.1 多光谱滤光片阵列 / MSFA

类似 Bayer 彩色滤光阵列，但从 RGB 三通道扩展到更多谱段。

优点：

- 与图像传感器兼容性高；
- 工程路线清晰；
- 易实现快照式采集；
- 适合可见、近红外、SWIR、MWIR、LWIR 的焦平面集成。

缺点：

- 每个像素只采一个谱段，空间分辨率损失；
- 需要去马赛克和谱重建；
- 滤光片一致性、串扰、中心波长漂移需要严格标定。

---

### 6.2 Fabry–Pérot 微腔阵列

通过不同腔长/介质厚度形成不同中心波长的窄带滤波单元。

优点：

- 结构清晰；
- 谱选择性好；
- 可直接做在焦平面上；
- 适合 SWIR/MWIR/LWIR 多光谱阵列。

缺点：

- 工艺控制要求高；
- 入射角敏感；
- 谱通道数增加时制备复杂度上升。

---

### 6.3 色散型片上光谱仪

包括：

- 阵列波导光栅 AWG；
- Echelle 光栅；
- 波导光栅；
- 微环谐振器阵列。

优点：

- 光谱分辨率可较高；
- 适合点测量、线测量、片上光谱传感。

缺点：

- 与二维大面阵成像结合较难；
- 温漂、工艺公差、耦合效率问题突出。

---

### 6.4 傅里叶变换型片上光谱

先获取干涉信号，再通过傅里叶变换或重构算法恢复光谱。

优点：

- 可做得很小；
- 波长分辨率可通过光程差设计；
- 适合片上/便携光谱仪。

缺点：

- 稳定性、温漂、标定难度较高；
- 二维成像系统实现较复杂。

---

### 6.5 超表面 / 计算光谱成像

用纳米结构对不同波长产生不同调制，再通过算法从编码图像恢复光谱。

典型形式：

[
y = Hx + n
]

其中：

- (x)：真实光谱图像；
- (H)：系统编码矩阵或前向模型；
- (y)：传感器测得的二维信号；
- (n)：噪声。

优点：

- 极薄、可集成；
- 设计自由度高；
- 适合快照多光谱/高光谱；
- 可与深度学习联合设计。

缺点：

- 依赖标定和重建算法；
- 入射角、偏振、工艺误差会影响谱响应；
- 光通量、谱分辨率、空间分辨率之间存在权衡。

---

## 7. 扫描式 vs 快照式

### 7.1 扫描式

包括点扫描、线扫描、波长扫描。

优点：

- 谱精度高；
- 数据质量好；
- 系统模型相对简单。

缺点：

- 慢；
- 有机械运动；
- 运动目标容易错位。

### 7.2 快照式

一次曝光获取多个谱段或压缩后的谱信息。

优点：

- 适合实时成像；
- 适合动态目标；
- 更符合片上化、小型化需求。

缺点：

- 前向模型复杂；
- 反演依赖算法；
- 标定和噪声建模非常重要。

---

## 8. 反演：从测量信号到物理量

片上多光谱系统往往不是直接输出“真实光谱”，而是输出被编码后的信号。反演就是从测量结果推回目标物理量。

### 8.1 第一层：光谱重建

从原始数据恢复：

[
\hat{I}(x,y,\lambda)
]

### 8.2 第二层：物理参数反演

从光谱进一步求：

- 浓度；
- 水分；
- 薄膜厚度；
- 温度；
- 发射率；
- 气体种类和浓度；
- 血氧、组织状态等。

### 8.3 第三层：任务输出

例如：

- 分类；
- 分割；
- 异常检测；
- 缺陷识别；
- 伪彩显示；
- 报警和定量判断。

---

## 9. 反演为什么难？

主要原因：

1. **欠定问题**：少量通道恢复高维光谱；
2. **噪声**：光子噪声、读出噪声、暗电流、固定图样噪声；
3. **标定误差**：滤波片中心波长偏差、响应漂移、温漂；
4. **照明耦合**：测得的是照明、材料、系统响应的乘积；
5. **空间-光谱混叠**：滤光阵列和压缩成像会造成空间与谱维的耦合。

常用方法：

- 最小二乘；
- Tikhonov 正则化；
- 稀疏重建；
- 全变分；
- 非负约束；
- 压缩感知；
- 深度学习；
- 物理约束神经网络；
- 算法-光学联合优化。

---

## 10. 工程指标与权衡

片上多光谱/高光谱系统最关键的指标包括：

| 指标    | 含义            | 典型权衡               |
| ----- | ------------- | ------------------ |
| 光谱分辨率 | 能分多细的波长差      | 通道越窄，光通量越低         |
| 空间分辨率 | 图像细节能力        | 谱通道越多，单通道空间采样可能下降  |
| 时间分辨率 | 帧率            | 帧率越高，曝光时间和信噪比受限    |
| 光通量   | 有效进入探测器的能量    | 编码复杂度和效率之间权衡       |
| 信噪比   | 测量可靠性         | 低照度/窄带/高帧率下更难      |
| 标定复杂度 | 系统响应矩阵是否稳定    | 超表面、随机编码结构标定要求高    |
| 可制造性  | 工艺是否可量产       | 纳米结构一致性是关键         |
| 成本    | 器件、制冷、封装、算法平台 | MWIR/LWIR 高端系统成本更高 |

---

## 11. 近五年片上多光谱/高光谱代表论文清单

> 检索范围：约 2021–2026；关键词包括 on-chip multispectral imaging、on-chip hyperspectral imaging、spectral imaging chip、multispectral filter array、metasurface spectral imaging、SWIR/MWIR/LWIR multispectral detector 等。  
> 链接说明：优先列出出版商/官方页面；若存在合法开放版本，列出 arXiv、PMC、Optica Open、机构 PDF 或开放全文。

|  # |   年份 | 论文                                                                                                         | 期刊/会议                          | DOI                        | 官方入口                                                                          | 开放入口                                                                                                                                                                | Google Scholar                                                                                                                                                 |
| -: | ---: | ---------------------------------------------------------------------------------------------------------- | ------------------------------ | -------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1 | 2024 | A broadband hyperspectral image sensor with high spatio-temporal resolution                                | Nature                         | 10.1038/s41586-024-08109-1 | [出版商/官方](https://www.nature.com/articles/s41586-024-08109-1)                  | [开放/预印本](https://arxiv.org/abs/2306.11583)                                                                                                                          | [Scholar](https://scholar.google.com/scholar?q=A+broadband+hyperspectral+image+sensor+with+high+spatio-temporal+resolution)                                    |
|  2 | 2023 | Video-rate hyperspectral camera based on a CMOS-compatible random array of Fabry–Pérot filters             | Nature Photonics               | 10.1038/s41566-022-01141-5 | [出版商/官方](https://www.nature.com/articles/s41566-022-01141-5)                  | —                                                                                                                                                                   | [Scholar](https://scholar.google.com/scholar?q=Video-rate+hyperspectral+camera+based+on+a+CMOS-compatible+random+array+of+Fabry%E2%80%93P%C3%A9rot+filters)    |
|  3 | 2022 | Dynamic brain spectrum acquired by a real-time ultraspectral imaging chip with reconfigurable metasurfaces | Optica                         | 10.1364/OPTICA.449010      | [出版商/官方](https://opg.optica.org/abstract.cfm?uri=optica-9-5-461)              | [开放/预印本](https://arxiv.org/abs/2005.02689)                                                                                                                          | [Scholar](https://scholar.google.com/scholar?q=Dynamic+brain+spectrum+acquired+by+a+real-time+ultraspectral+imaging+chip+with+reconfigurable+metasurfaces)     |
|  4 | 2022 | Ultraspectral Imaging Based on Metasurfaces with Freeform Shaped Meta-Atoms                                | Laser & Photonics Reviews      | 10.1002/lpor.202100663     | [出版商/官方](https://onlinelibrary.wiley.com/doi/full/10.1002/lpor.202100663)     | —                                                                                                                                                                   | [Scholar](https://scholar.google.com/scholar?q=Ultraspectral+Imaging+Based+on+Metasurfaces+with+Freeform+Shaped+Meta-Atoms)                                    |
|  5 | 2024 | Angle-Insensitive Spectral Imaging Based on Topology-Optimized Plasmonic Metasurfaces                      | Laser & Photonics Reviews      | 10.1002/lpor.202400255     | [出版商/官方](https://onlinelibrary.wiley.com/doi/10.1002/lpor.202400255)          | [开放/预印本](https://arxiv.org/abs/2212.07813)                                                                                                                          | [Scholar](https://scholar.google.com/scholar?q=Angle-Insensitive+Spectral+Imaging+Based+on+Topology-Optimized+Plasmonic+Metasurfaces)                          |
|  6 | 2024 | Multispectral imaging through metasurface with quasi-bound states in the continuum                         | Optics Express                 | 10.1364/OE.523676          | [出版商/官方](https://opg.optica.org/abstract.cfm?uri=oe-32-13-23268)              | [开放/预印本](https://in.iphy.ac.cn/upload/s22/m/02669_2024121817504118357.pdf)                                                                                          | [Scholar](https://scholar.google.com/scholar?q=Multispectral+imaging+through+metasurface+with+quasi-bound+states+in+the+continuum)                             |
|  7 | 2025 | A Spatiotemporal Tunable Filter Array Chip for Video-Rate Hyperspectral Imaging                            | Advanced Science               | 待补/见论文页                    | [出版商/官方](https://pmc.ncbi.nlm.nih.gov/articles/PMC11887441/)                  | [开放/预印本](https://pmc.ncbi.nlm.nih.gov/articles/PMC11887441/)                                                                                                        | [Scholar](https://scholar.google.com/scholar?q=A+Spatiotemporal+Tunable+Filter+Array+Chip+for+Video-Rate+Hyperspectral+Imaging)                                |
|  8 | 2023 | Deep-learning based on-chip rapid spectral imaging with high spatial resolution                            | Chip / arXiv version           | 待补/见论文页                    | [出版商/官方](https://arxiv.org/abs/2301.06321)                                    | [开放/预印本](https://arxiv.org/abs/2301.06321)                                                                                                                          | [Scholar](https://scholar.google.com/scholar?q=Deep-learning+based+on-chip+rapid+spectral+imaging+with+high+spatial+resolution)                                |
|  9 | 2022 | On-chip short-wave infrared multispectral detector based on integrated Fabry–Perot microcavities array     | Chinese Optics Letters         | 10.3788/COL202220.061302   | [出版商/官方](https://www.opticsjournal.net/Articles/OJcdbb3145705aa94b/FullText)  | [开放/预印本](https://www.researching.cn/articles/OJcdbb3145705aa94b)                                                                                                    | [Scholar](https://scholar.google.com/scholar?q=On-chip+short-wave+infrared+multispectral+detector+based+on+integrated+Fabry%E2%80%93Perot+microcavities+array) |
| 10 | 2025 | Gas detection based on a mid-infrared super-pixel multi-spectral imaging device                            | Applied Optics                 | 10.1364/AO.543249          | [出版商/官方](https://opg.optica.org/ao/fulltext.cfm?uri=ao-64-1-149)              | —                                                                                                                                                                   | [Scholar](https://scholar.google.com/scholar?q=Gas+detection+based+on+a+mid-infrared+super-pixel+multi-spectral+imaging+device)                                |
| 11 | 2025 | Mid-wave infrared multispectral imaging with HgCdTe photodetector                                          | Optics Express                 | 10.1364/OE.567467          | [出版商/官方](https://opg.optica.org/oe/fulltext.cfm?uri=oe-33-13-27026)           | —                                                                                                                                                                   | [Scholar](https://scholar.google.com/scholar?q=Mid-wave+infrared+multispectral+imaging+with+HgCdTe+photodetector)                                              |
| 12 | 2025 | Long-wave infrared computational multispectral metasurface and spectral reconstruction method              | Scientific Reports             | 10.1038/s41598-025-06599-1 | [出版商/官方](https://www.nature.com/articles/s41598-025-06599-1)                  | [开放/预印本](https://preprints.opticaopen.org/articles/preprint/Long-wave_Infrared_Computational_Multispectral_Metasurface_and_Spectral_Reconstruction_Method/27626214) | [Scholar](https://scholar.google.com/scholar?q=Long-wave+infrared+computational+multispectral+metasurface+and+spectral+reconstruction+method)                  |
| 13 | 2023 | Longwave infrared multispectral image sensor system using aluminum-germanium plasmonic filter arrays       | Nano Research / arXiv version  | 10.1007/s12274-023-5669-z  | [出版商/官方](https://www.sciopen.com/article/10.1007/s12274-023-5669-z)           | [开放/预印本](https://arxiv.org/abs/2303.01661)                                                                                                                          | [Scholar](https://scholar.google.com/scholar?q=Longwave+infrared+multispectral+image+sensor+system+using+aluminum-germanium+plasmonic+filter+arrays)           |
| 14 | 2025 | Compact Spectral Imaging: A Review of Miniaturized and Integrated Systems                                  | Laser & Photonics Reviews      | 10.1002/lpor.202501042     | [出版商/官方](https://onlinelibrary.wiley.com/doi/full/10.1002/lpor.202501042)     | —                                                                                                                                                                   | [Scholar](https://scholar.google.com/scholar?q=Compact+Spectral+Imaging%3A+A+Review+of+Miniaturized+and+Integrated+Systems)                                    |
| 15 | 2025 | Reconstructive spectrometers: hardware miniaturization and computational reconstruction                    | eLight                         | 10.1186/s43593-025-00101-0 | [出版商/官方](https://link.springer.com/article/10.1186/s43593-025-00101-0)        | [开放/预印本](https://link.springer.com/content/pdf/10.1186/s43593-025-00101-0.pdf)                                                                                      | [Scholar](https://scholar.google.com/scholar?q=Reconstructive+spectrometers%3A+hardware+miniaturization+and+computational+reconstruction)                      |
| 16 | 2025 | Research progress of novel on-chip multispectral photodetectors                                            | Infrared and Laser Engineering | 10.3788/IRLA20250042       | [出版商/官方](https://www.spacejournal.cn/kjkxxb/article/doi/10.3788/IRLA20250042) | [开放/预印本](https://www.spacejournal.cn/hwyjggc/en/article/pdf/preview/10.3788/IRLA20250042.pdf)                                                                       | [Scholar](https://scholar.google.com/scholar?q=Research+progress+of+novel+on-chip+multispectral+photodetectors)                                                |

---

## 12. 建议优先精读的论文顺序

### 第一组：系统级片上高光谱成像

1. **Bian et al., Nature 2024**  
   重点看：片上调制材料、96 通道、VIS–NIR、124 fps、重建算法、应用演示。
2. **Yako et al., Nature Photonics 2023**  
   重点看：CMOS 兼容 Fabry–Pérot 随机滤波阵列、压缩感知、视频级高光谱。
3. **Lin et al., Advanced Science 2025**  
   重点看：时空可调滤波阵列、视频级高光谱与分辨率权衡。

---

### 第二组：超表面片上谱成像

4. **Xiong et al., Optica 2022**  
   重点看：可重构超表面、超光谱成像芯片、生物成像验证。
5. **Yang et al., LPR 2022**  
   重点看：自由形状 meta-atom、谱调制设计、超表面阵列重建。
6. **Yang et al., LPR 2024**  
   重点看：入射角不敏感设计、拓扑优化、宽视场问题。
7. **Shao et al., Optics Express 2024**  
   重点看：quasi-BIC 谐振、窄带多光谱调制。

---

### 第三组：红外片上多光谱

8. **Xuan et al., Chinese Optics Letters 2022**  
   重点看：SWIR InGaAs 焦平面 + Fabry–Pérot 微腔阵列。
9. **Hu et al., Applied Optics 2025**  
   重点看：MIR super-pixel 多光谱滤波阵列与气体检测。
10. **Zhang et al., Optics Express 2025**  
    重点看：MWIR HgCdTe 探测器与像素级滤波阵列。
11. **Wang et al., Scientific Reports 2025**  
    重点看：LWIR 计算多光谱超表面和深度学习重建。
12. **Shaik et al., Nano Research / arXiv 2023**  
    重点看：Al-Ge 等离激元滤波阵列与非制冷热传感器系统。

---

### 第四组：综述

13. **Compact Spectral Imaging: A Review of Miniaturized and Integrated Systems, 2025**  
    适合作为“微型/集成光谱成像系统”的总入口。
14. **Reconstructive spectrometers: hardware miniaturization and computational reconstruction, 2025**  
    适合理解“硬件编码 + 计算重构”的谱仪范式。
15. **Research progress of novel on-chip multispectral photodetectors, 2025**  
    中文综述，适合建立片上多光谱探测器路线图。

---

## 13. 合法获取文献的建议流程

由于本文献列表中有部分论文可能处于付费墙后，建议按以下顺序获取全文：

1. **先点 DOI / 出版商页面**  
   有些论文是 Open Access，可直接下载 PDF。
2. **查 arXiv / PMC / Optica Open / 机构仓储**  
   很多论文有作者上传的预印本或开放版本。
3. **用 Google Scholar 的 “all versions / 所有版本”**  
   常能找到作者主页、大学仓储或预印本。
4. **通过学校/研究所图书馆数据库访问**  
   例如 Web of Science、Scopus、IEEE Xplore、Optica、ACS、Wiley、Springer Nature 等。
5. **ResearchGate 或作者主页请求全文**  
   可以合法向作者请求论文副本。
6. **联系通讯作者**  
   直接发邮件说明研究用途，请求分享作者版 manuscript。

本文不提供 Sci-Hub、盗版 PDF 或绕过付费墙的方法。

---

## 14. 推荐检索关键词

### 英文关键词

```text
on-chip multispectral imaging
on-chip hyperspectral imaging
on-chip spectral imaging sensor
CMOS-compatible hyperspectral camera
multispectral filter array CMOS image sensor
pixel-level spectral filter array
snapshot multispectral imaging chip
snapshot hyperspectral imaging chip
metasurface spectral imaging
metasurface multispectral imaging
ultraspectral imaging chip
computational spectral imaging sensor
filter-free multispectral photodetector
on-chip multispectral photodetector
SWIR multispectral detector chip
MWIR multispectral filter array
LWIR multispectral metasurface
reconstructive spectrometer
computational hyperspectral imaging
```

### 中文关键词

```text
片上多光谱成像
片上高光谱成像
片上光谱成像芯片
多光谱滤波阵列
像素级光谱滤波阵列
超表面光谱成像
计算光谱成像
多光谱光电探测器
无滤光片多光谱探测器
短波红外多光谱探测器
中波红外多光谱成像
长波红外多光谱超表面
重构型光谱仪
计算光谱仪
```

---

## 15. 一个适合继续深入的学习路线

### 阶段 A：基础概念

- 光谱、波长、频率、能量；
- 吸收、反射、透射、发射；
- 黑体辐射和普朗克定律；
- 红外大气窗口；
- 探测器响应和噪声。

### 阶段 B：光谱成像

- 数据立方体；
- 多光谱 vs 高光谱；
- 扫描式 vs 快照式；
- 暗场/白场校正；
- 空间-光谱分辨率权衡。

### 阶段 C：片上硬件

- MSFA 多光谱滤光阵列；
- Fabry–Pérot 微腔；
- 超表面谱调制；
- 硅光子光谱仪；
- SWIR/MWIR/LWIR 探测器材料；
- 焦平面集成工艺。

### 阶段 D：算法与反演

- 前向模型；
- 逆问题；
- 正则化；
- 压缩感知；
- 深度学习谱重建；
- 物理约束网络；
- 温度/发射率/成分反演。

---

## 16. 关键结论

1. 光谱学回答“不同波长的光发生了什么”。
2. 光谱成像回答“这些波长信息在空间上分布在哪里”。
3. 片上多光谱把滤波、调制、探测和重建尽可能集成到芯片或焦平面附近。
4. SWIR 更适合反射光材料识别，MWIR 更适合高温目标和气体，LWIR 更适合常温热成像。
5. 片上多光谱的技术主线正在从“光学直接分光”转向“光学编码 + 计算反演”。
6. 近五年代表性方向包括 CMOS 兼容滤波阵列、Fabry–Pérot 阵列、超表面、重构型微型光谱仪和红外焦平面多光谱滤波阵列。
7. 工程实现中必须同时考虑光谱分辨率、空间分辨率、时间分辨率、信噪比、光通量、标定复杂度和可制造性。

---

## 17. 本地 PDF 副本索引

已将可开放获取的论文下载到 `80-sources/papers/`。映射如下：

| 论文（第一作者/年份） | 本地文件名 | 状态 |
| --- | --- | --- |
| Bian et al., Nature 2024 | `2024_Bian_Nature_Broadband_Hyperspectral_Image_Sensor.pdf` | ✅ |
| Xiong et al., Optica 2022 | `2022_Xiong_Optica_Ultraspectral_Imaging_Chip.pdf` | ✅ |
| Yang et al., LPR 2024 | `2024_Yang_LPR_Angle_Insensitive_Spectral_Imaging.pdf` | ✅ |
| Shao et al., Optics Express 2024 | `2024_Shao_OE_Multispectral_Metasurface_QBIC.pdf` | ✅ |
| Chip / arXiv 2023 | `2023_Chip_Deep_Learning_On_Chip_Rapid_Spectral_Imaging.pdf` | ✅ |
| Shaik et al., Nano Research 2023 | `2023_Shaik_NanoResearch_LWIR_Multispectral_AlGe_Plasmons.pdf` | ✅ |
| Wang et al., Scientific Reports 2025 | `2025_Wang_SciRep_LWIR_Computational_Multispectral_Metasurface.pdf` | ✅ |
| eLight 2025 综述 | `2025_eLight_Reconstructive_Spectrometers_Review.pdf` | ✅ |
| IRL 2025 中文综述 | `2025_IRL_Novel_On_Chip_Multispectral_Photodetectors_Review.pdf` | ✅ |
| Lin et al., Advanced Science / ACS Nano Lett. 2025 | `2025_Lin_AdvSci_Spatiotemporal_Tunable_Filter_Array_Chip.pdf`（尚未存在） | ⚠️ 需手动下载 |
| Xuan et al., Chinese Optics Letters 2022 | `2022_Xuan_COL_SWIR_FP_Microcavities.pdf`（尚未存在） | ⚠️ 需手动下载 |

完整说明见 `80-sources/papers/README.md`。

---

## 18. 后续可扩展内容

后续可以在本文件基础上继续扩展：

- 片上多光谱系统框图；
- SWIR/MWIR/LWIR 探测器材料对比；
- Fabry–Pérot 微腔阵列设计笔记（概念层已补：[[../10-concepts/fabry-perot-microcavity|Fabry–Pérot 微腔]]）；
- 超表面谱调制设计流程（概念层已补：[[../10-concepts/metasurface|超表面]]）；
- 多光谱重建算法 Python 示例（概念层已补：[[../10-concepts/spectral-reconstruction|光谱重建]]）；
- 温度-发射率分离反演示例；
- 气体吸收谱检测方案；
- 论文阅读笔记模板。

---

## 19. 相关 LensFit 知识库入口

### 概念

- [[../10-concepts/multispectral-imaging|多光谱成像]]
- [[../10-concepts/hyperspectral-imaging|高光谱成像]]
- [[../10-concepts/snapshot-spectral-imaging|快照式光谱成像]]
- [[../10-concepts/multispectral-filter-array|多光谱滤光片阵列]]
- [[../10-concepts/fabry-perot-microcavity|Fabry–Pérot 微腔]]
- [[../10-concepts/metasurface|超表面]]
- [[../10-concepts/spectral-reconstruction|光谱重建]]

### 设备

- [[../40-devices/on-chip-spectral-sensor|片上光谱传感器]]
- [[../40-devices/ingaas-focal-plane-array|InGaAs 焦平面阵列]]
- [[../40-devices/mct-detector|MCT 探测器]]
- [[../40-devices/ir-thermal-detector|红外热像仪探测器]]
- [[../40-devices/hyperspectral-camera|高光谱相机]]

### 领域与学习

- [[../30-domains/on-chip-multispectral|片上多光谱成像领域参考]]
- [[../50-learning/16-spectroscopy|第16章：光谱学与色彩科学]]
- [[../80-sources/papers/README|本地论文副本目录]]

