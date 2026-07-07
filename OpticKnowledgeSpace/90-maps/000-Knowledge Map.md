---
id: knowledge.map.root
title: 知识地图
type: map
status: maintained
aliases:
  - Knowledge Map
---

# 知识地图

## 核心入口

- **[[modules/README|LensFit 微专业入口]]**：五模块环形微专业，三种学习节奏，适合系统学习者。**（v4.0 新入口）**
- [[001-Learning Path|从零到深入学习路径]]：面向初学者，按阶段串联教程、概念、公式、设备和领域。
- [[002-Knowledge Architecture|知识库架构]]：解释 Vault 的分层模型、光谱知识子图和当前缺口。
- [[../50-learning/README|学习教程目录]]：16 章主线教程总目录。
- [[../80-sources/000-Textbook Index|教材索引]]：优秀教材对比和主题入口。
- [[../80-sources/001-Textbook Reference Matrix|教材页码索引矩阵]]：知识点到教材章节/页码的映射。
- [[008-On-chip Multispectral Topic|片上多光谱专题地图]]：片上多光谱、片上高光谱、微型光谱仪和红外多谱段探测的专题入口。

## 微专业五模块（v4.0）

| 模块 | 核心能力 | 预计时长 | 先修 |
|------|---------|---------|------|
| [[modules/10-foundations/README|模块甲｜桥接]] | 数学/物理/语言最小补齐 | 15-25h | 无 |
| [[modules/20-geometric-optics/README|模块乙｜几何光学]] | 光线模型、典型系统、一阶成像 | 30-45h | 模块甲 |
| [[modules/30-wave-optics/README|模块丙｜波动光学]] | 干涉、衍射、PSF/OTF/MTF、傅里叶 | 35-55h | 模块乙 |
| [[modules/40-spectroscopy/README|模块丁｜光谱学]] | 光谱、色散、仪器、分辨率 | 25-40h | 模块乙 |
| [[modules/50-optical-design/README|模块戊｜光学设计]] | 规格-结构-分析-优化-容差闭环 | 40-60h | 模块丙+丁 |

模块甲 → 模块乙 → 模块丙 → 模块戊 → 综合项目
模块乙 → 模块丁 → 模块戊

## 16章主线教程（传统路径）
- [[50-learning/000-introduction|绪论：走进成像光学]]
- [[50-learning/001-light-and-waves|光与波]]
- [[50-learning/002-geometric-optics|几何光学]]
- [[50-learning/003-lens-parameters|镜头参数]]
- [[50-learning/004-sensors|传感器]]
- [[50-learning/005-matching-basics|匹配基础]]
- [[50-learning/006-aberrations|像差]]
- [[50-learning/007-interfaces-and-mounts|接口与安装]]
- [[50-learning/008-domain-applications|领域应用]]
- [[50-learning/009-exercises|习题与练习]]

### 进阶阶段（深入）
- [[50-learning/010-physical-optics-advanced|物理光学深入]]
- [[50-learning/011-optical-design-basics|光学设计基础]]
- [[50-learning/012-otf-and-image-quality|光学传递函数与图像质量]]
- [[50-learning/013-illumination-design|照明系统设计]]

### 前沿与实践阶段
- [[50-learning/014-computational-optics|计算光学与计算成像]]
- [[50-learning/015-engineering-cases|工程案例与选型实战]]

### 专项深入
- [[50-learning/016-spectroscopy|光谱学与色彩科学]]

## 领域入口

- [[../30-domains/README|领域目录]]
- [[30-domains/000-industrial-vision|工业视觉]]
- [[30-domains/001-photography|摄影]]
- [[30-domains/002-microscopy|显微镜]]
- [[30-domains/003-infrared-imaging|红外成像]]
- [[30-domains/004-spectroscopy|光谱成像]]
- [[30-domains/005-on-chip-multispectral|片上多光谱成像]]
- [[008-On-chip Multispectral Topic|片上多光谱专题地图]]

## 概念索引

### 基础概念
- [[10-concepts/000-refractive-index|折射率]]
- [[10-concepts/027-airy-disk|艾里斑]]
- [[10-concepts/003-focal-length|焦距]]
- [[10-concepts/005-f-number|F值]]
- [[10-concepts/007-depth-of-field|景深]]
- [[10-concepts/009-image-circle|像圈]]
- [[10-concepts/038-nyquist-frequency|奈奎斯特频率]]
- [[10-concepts/036-pixel|像元]]
- [[10-concepts/040-aliasing|混叠]]
- [[10-concepts/019-chromatic-aberration|色差]]

### 光谱与色彩概念
- [[10-concepts/074-spectral-resolution|光谱分辨率]]
- [[10-concepts/017-dispersion|色散]]
- [[10-concepts/069-chromaticity-diagram|色度图]]
- [[10-concepts/067-color-temperature|色温]]
- [[10-concepts/070-fluorescence|荧光]]
- [[10-concepts/071-raman-scattering|拉曼散射]]
- [[10-concepts/072-multispectral-imaging|多光谱成像]]
- [[10-concepts/073-hyperspectral-imaging|高光谱成像]]
- [[10-concepts/075-snapshot-spectral-imaging|快照式光谱成像]]
- [[10-concepts/076-multispectral-filter-array|多光谱滤光片阵列]]
- [[10-concepts/077-fabry-perot-microcavity|Fabry–Pérot 微腔]]
- [[10-concepts/078-metasurface|超表面]]
- [[10-concepts/079-spectral-reconstruction|光谱重建]]
- [[10-concepts/066-spectral-power-distribution|光谱分布函数]]
- [[10-concepts/016-abbe-number|阿贝数]]

更多概念见 [[10-concepts/README|概念目录]]

## 公式索引

### 基础公式
- [[20-formulas/000-thin-lens-gauss|薄透镜高斯公式]]
- [[20-formulas/001-lateral-magnification|横向放大倍率]]
- [[20-formulas/003-angle-of-view|视角公式]]
- [[20-formulas/002-focal-length-from-wd|焦距反推公式]]
- [[20-formulas/008-airy-disk-diameter|艾里斑直径]]
- [[20-formulas/006-nyquist-frequency|奈奎斯特频率]]
- [[20-formulas/005-pixel-precision|像素精度]]
- [[20-formulas/004-coverage-ratio|像圈覆盖比]]
- [[20-formulas/007-oversampling-ratio|过采样率]]
- [[20-formulas/009-rayleigh-criterion|瑞利判据]]

### 光谱与色彩公式
- [[20-formulas/012-grating-equation|光栅方程]]
- [[20-formulas/013-grating-resolving-power|光栅光谱分辨率]]
- [[20-formulas/014-prism-dispersion|棱镜色散率]]
- [[20-formulas/016-delta-e|Delta E色差]]
- [[20-formulas/015-planck-blackbody|普朗克黑体辐射公式]]

更多公式见 [[20-formulas/README|公式目录]]

## 设备索引

### 基础设备
- [[40-devices/000-c-mount-lens|C-mount镜头]]
- [[40-devices/001-telecentric-lens|远心镜头]]
- [[40-devices/002-microscope-objective|显微镜物镜]]
- [[40-devices/003-global-shutter-cmos|全局快门CMOS]]
- [[40-devices/004-rolling-shutter-cmos|卷帘快门CMOS]]
- [[40-devices/015-ir-thermal-detector|红外热像仪探测器]]
- [[40-devices/006-led-ring-light|LED环形光源]]
- [[40-devices/007-coaxial-illumination|同轴照明]]
- [[40-devices/005-backlight|背光板]]
- [[40-devices/008-telecentric-illumination|远心照明]]

### 光谱设备
- [[40-devices/011-spectrometer|光谱仪]]
- [[40-devices/012-hyperspectral-camera|高光谱相机]]
- [[40-devices/013-on-chip-spectral-sensor|片上光谱传感器]]
- [[40-devices/016-ingaas-focal-plane-array|InGaAs 焦平面阵列]]
- [[40-devices/017-mct-detector|MCT 探测器]]
- [[40-devices/015-ir-thermal-detector|红外热像仪探测器]]
- [[40-devices/010-diffraction-grating|衍射光栅]]
- [[40-devices/009-bandpass-filter|窄带滤光片]]
- [[40-devices/014-integrating-sphere|积分球]]

更多设备见 [[40-devices/README|设备目录]]

## 状态速查

| 目录 | 状态 | 说明 |
|------|------|------|
| `50-learning/` | ✅ 完成 | 16章完整学习路径 |
| `10-concepts/` | 🟡 建设中 | 20+ 核心概念原子笔记 |
| `20-formulas/` | 🟡 建设中 | 15+ 核心公式原子笔记 |
| `40-devices/` | 🟡 建设中 | 15+ 设备类型原子笔记 |
| `30-domains/` | ✅ 完成 | 6个领域深度参考（含片上多光谱） |
| `80-sources/` | 🔴 待建 | 标准、论文、厂商资料索引 |
| `90-maps/` | ✅ 完成 | 知识地图、知识架构、学习路径 |

---

*知识地图是进入 LensFit 光学知识库的最佳入口。建议按学习路线顺序阅读，或在需要时通过概念/公式/设备索引快速定位。*
