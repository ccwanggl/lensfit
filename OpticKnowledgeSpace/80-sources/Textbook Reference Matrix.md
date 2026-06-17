---

id: sources.textbook-reference-matrix
title: 教材页码索引矩阵
type: source-index
status: reviewed
source_type: textbook-reference-matrix
aliases:
  - Textbook Reference Matrix
  - 教材页码矩阵---

# 教材页码索引矩阵

本矩阵用于把知识库里的关键知识点索引到优秀教材。当前尚未接入本地教材文件，因此页码列默认 `待核验`。拿到实体书、合法电子书或出版社预览后，再把页码填实。

## 页码状态

| 状态 | 含义 |
|---|---|
| `verified` | 已核对指定版本的页码 |
| `chapter-verified` | 已核对章节/目录，但未核对页码 |
| `unverified` | 基于教材定位经验，尚未核对章节或页码 |
| `needs-source` | 需要补充更合适的专门来源 |

## 基础光学

| 知识点 | 知识库笔记 | 首选教材 | 对应章节/主题 | 页码 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| 光的本质 | [[../50-learning/01-light-and-waves|光与波]] | Hecht, *Optics*, 5th ed. | The Nature of Light / Wave Motion / Electromagnetic Theory | 待核验 | chapter-verified | Hecht 更适合建立物理直觉 |
| 折射率 | [[../10-concepts/refractive-index|折射率]] | Hecht, *Optics*, 5th ed. | Geometrical Optics / Propagation of Light | 待核验 | unverified | 后续可补材料色散表来源 |
| 色散 | [[../10-concepts/dispersion|色散]] | Hecht, *Optics*, 5th ed. | Geometrical Optics / Dispersion | 待核验 | unverified | 与阿贝数、色差联动 |
| 薄透镜公式 | [[../20-formulas/thin-lens-gauss|薄透镜高斯公式]] | Hecht, *Optics*, 5th ed. | Geometrical Optics | 待核验 | unverified | 工程侧可补 Smith |
| 焦距 | [[../10-concepts/focal-length|焦距]] | Hecht, *Optics*, 5th ed. | Geometrical Optics | 待核验 | unverified | Smith 用于工程系统设计 |

## 镜头、成像与像质

| 知识点 | 知识库笔记 | 首选教材 | 对应章节/主题 | 页码 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| F 值 | [[../10-concepts/f-number|F值]] | Smith, *Modern Optical Engineering*, 4th ed. | Optical system layout / aperture / stops | 待核验 | unverified | 更偏工程参数 |
| 景深 | [[../10-concepts/depth-of-field|景深]] | Smith, *Modern Optical Engineering*, 4th ed. | Image formation / depth of field | 待核验 | unverified | 可辅以摄影教材 |
| 像圈 | [[../10-concepts/image-circle|像圈]] | Smith, *Modern Optical Engineering*, 4th ed. | Optical system design / image format | 待核验 | unverified | 厂商手册也很重要 |
| 色差 | [[../10-concepts/chromatic-aberration|色差]] | Hecht, *Optics*, 5th ed. + Smith | Aberrations / chromatic aberration | 待核验 | unverified | Hecht 讲成因，Smith 讲工程校正 |
| 艾里斑 | [[../10-concepts/airy-disk|艾里斑]] | Hecht, *Optics*, 5th ed. | Diffraction | 待核验 | unverified | 与瑞利判据、衍射极限联动 |
| 瑞利判据 | [[../20-formulas/rayleigh-criterion|瑞利判据]] | Hecht, *Optics*, 5th ed. | Diffraction / resolution | 待核验 | unverified | 显微镜路线需补专门来源 |
| MTF/OTF | [[../50-learning/12-otf-and-image-quality|光学传递函数与图像质量]] | Goodman, *Introduction to Fourier Optics*, 4th ed. | Fourier optics / imaging systems | 待核验 | chapter-verified | Goodman 是主线来源，Smith 做工程补充 |

## 传感器、采样与探测

| 知识点 | 知识库笔记 | 首选教材 | 对应章节/主题 | 页码 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| 像元 | [[../10-concepts/pixel|像元]] | Saleh & Teich, *Fundamentals of Photonics*, 3rd ed. | Photodetectors | 待核验 | chapter-verified | 还需补传感器厂商应用手册 |
| 奈奎斯特频率 | [[../10-concepts/nyquist-frequency|奈奎斯特频率]] | Goodman, *Introduction to Fourier Optics*, 4th ed. | Sampling / spatial frequency | 待核验 | unverified | 成像采样更适合 Goodman |
| 混叠 | [[../10-concepts/aliasing|混叠]] | Goodman, *Introduction to Fourier Optics*, 4th ed. | Sampling / Fourier imaging | 待核验 | unverified | 可补数字图像处理教材 |
| 过采样率 | [[../20-formulas/oversampling-ratio|过采样率]] | Goodman + 厂商手册 | Sampling / MTF matching | 待核验 | needs-source | 更偏工程派生指标 |

## 傅里叶光学与计算成像

| 知识点 | 知识库笔记 | 首选教材 | 对应章节/主题 | 页码 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| 衍射 | [[../50-learning/10-physical-optics-advanced|物理光学深入]] | Hecht, *Optics*, 5th ed. | Diffraction | 待核验 | chapter-verified | 入门先读 Hecht |
| 傅里叶光学 | [[../50-learning/10-physical-optics-advanced|物理光学深入]] | Goodman, *Introduction to Fourier Optics*, 4th ed. | Fourier analysis in optics | 待核验 | chapter-verified | 进阶主教材 |
| 计算光学 | [[../50-learning/14-computational-optics|计算光学与计算成像]] | Goodman + 专门论文/教材 | Optical information processing / computational imaging | 待核验 | needs-source | 需要补现代计算成像来源 |

## 光谱与色彩

| 知识点 | 知识库笔记 | 首选教材 | 对应章节/主题 | 页码 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| 光谱分布函数 | [[../10-concepts/spectral-power-distribution|光谱分布函数]] | Hecht + Saleh & Teich | Radiation / light sources | 待核验 | unverified | 光源 SPD 还需照明/色彩来源 |
| 光谱分辨率 | [[../10-concepts/spectral-resolution|光谱分辨率]] | Hecht, *Optics*, 5th ed. | Diffraction grating / resolving power | 待核验 | unverified | 光谱仪厂商手册更适合工程指标 |
| 光栅方程 | [[../20-formulas/grating-equation|光栅方程]] | Hecht, *Optics*, 5th ed. | Diffraction grating | 待核验 | unverified | 后续补光栅厂商资料 |
| 光栅分辨本领 | [[../20-formulas/grating-resolving-power|光栅光谱分辨率]] | Hecht + Goodman | Diffraction / resolving power | 待核验 | unverified | 需要核对具体符号定义 |
| 黑体辐射 | [[../20-formulas/planck-blackbody|普朗克黑体辐射公式]] | Saleh & Teich, *Fundamentals of Photonics*, 3rd ed. | Light and matter / thermal radiation | 待核验 | unverified | 红外章节也依赖它 |
| 色度图 | [[../10-concepts/chromaticity-diagram|色度图]] | CIE/色彩科学专门教材 | Colorimetry | 待核验 | needs-source | 需补 Wyszecki & Stiles 或 CIE |
| 色温 | [[../10-concepts/color-temperature|色温]] | CIE/照明教材 | Color temperature / CCT | 待核验 | needs-source | 工程上要补照明标准 |
| Delta E | [[../20-formulas/delta-e|Delta E 色差]] | CIE/色彩科学专门教材 | Color difference | 待核验 | needs-source | CIE76/CIEDE2000 需区分 |
| 荧光 | [[../10-concepts/fluorescence|荧光]] | Saleh & Teich | Light-matter interaction | 待核验 | unverified | 显微荧光需补专门来源 |
| 拉曼散射 | [[../10-concepts/raman-scattering|拉曼散射]] | Saleh & Teich + 光谱教材 | Inelastic scattering / spectroscopy | 待核验 | needs-source | 需补拉曼光谱教材 |

## 设备与工程实践

| 知识点 | 知识库笔记 | 首选教材 | 对应章节/主题 | 页码 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| C-mount 镜头 | [[../40-devices/c-mount-lens|C-mount镜头]] | Smith + 厂商手册 | Optical system layout | 待核验 | needs-source | 接口尺寸优先查标准/厂商 |
| 远心镜头 | [[../40-devices/telecentric-lens|远心镜头]] | Smith + 厂商手册 | Optical system design | 待核验 | needs-source | 厂商应用手册更有用 |
| 显微镜物镜 | [[../40-devices/microscope-objective|显微镜物镜]] | Hecht + 显微镜专门教材 | Microscopy / resolution | 待核验 | needs-source | NA、WD、盖玻片校正需专门来源 |
| 光谱仪 | [[../40-devices/spectrometer|光谱仪]] | Hecht + 光谱仪器手册 | Diffraction grating / spectrometer | 待核验 | needs-source | 实际选型以厂商参数为主 |
| 高光谱相机 | [[../40-devices/hyperspectral-camera|高光谱相机]] | 光谱成像专门资料 | Hyperspectral imaging | 待核验 | needs-source | 需补 Specim/Headwall/Resonon 等手册 |

## 下一步核验计划

1. 先核验第1-6章涉及的 Hecht 页码。
2. 再核验 Goodman 中 Fourier optics、sampling、OTF/MTF 的页码。
3. 然后核验 Smith 中镜头工程、像差、像质评价的页码。
4. 最后补色彩科学、光谱仪器、红外成像的专门教材和厂商资料。
