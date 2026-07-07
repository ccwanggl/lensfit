---
id: source.on-chip-multispectral-literature
title: 片上多光谱/高光谱文献雷达
type: source
domains: [spectroscopy, on-chip-multispectral]
status: reviewed
aliases:
  - 片上多光谱文献
  - 片上高光谱文献
  - on-chip-multispectral-literature
  - integrated spectral imaging literature
---

# 片上多光谱/高光谱文献雷达

> 跟踪范围：片上多光谱、片上高光谱、微型/集成光谱成像、重构型光谱仪、MSFA、Fabry-Perot 微腔阵列、超表面光谱成像、红外焦平面多谱段探测。
> 更新状态：2026-07-02。
> 使用方式：本页是来源雷达，不直接替代 [[../30-domains/005-on-chip-multispectral|片上多光谱成像]] 的系统判断。

## 阅读顺序

| 顺序 | 读什么 | 目的 |
| --- | --- | --- |
| 1 | 2025 综述：Compact Spectral Imaging；Reconstructive spectrometers；novel on-chip multispectral photodetectors | 先建立微型化、重构和探测器三条主线 |
| 2 | 2024 Nature 宽带高时空分辨率高光谱图像传感器 | 看片上调制材料、快照/视频和宽谱覆盖如何组合 |
| 3 | 2023 Nature Photonics 随机 Fabry-Perot 滤波阵列 | 看 CMOS 兼容滤波阵列和压缩感知的工程形态 |
| 4 | 2022-2025 超表面光谱成像论文 | 看纳米结构编码、角度鲁棒性和端到端联合设计 |
| 5 | SWIR/MWIR/LWIR 论文 | 看不同红外波段如何改变探测器、制冷和滤波路线 |
| 6 | 算法与重建论文 | 看响应矩阵、正则化、深度学习和任务驱动输出 |

## 技术路线索引

| 路线 | 代表来源 | 适合提炼到知识库的内容 |
| --- | --- | --- |
| MSFA / 像素级滤波阵列 | Shinoda 2018；Yako 2023；Lin 2025 | 快照采样、空间-光谱权衡、去马赛克、压缩感知 |
| Fabry-Perot 微腔 | Yako 2023；Xuan 2022；红外焦平面论文 | 腔长控制、入射角敏感、窄带通道、焦平面集成 |
| 超表面光谱成像 | Xiong 2022；Yang 2022/2024；Shao 2024；Wang 2025 | 谱编码、角度鲁棒性、拓扑优化、LWIR 计算重建 |
| 宽带/视频级片上高光谱 | Bian 2024；Lin 2025 | 高时空分辨率、可调滤波、动态场景、重建网络 |
| 重构型微型光谱仪 | Tian 2024；Zhang 2023；eLight 2025 | 响应矩阵、硬件小型化、鲁棒性和分辨率边界 |
| 新型探测器材料 | IRL 2025；vdW tunnel diode 2024；量子点/二维材料相关论文 | 宽谱响应、无滤片探测、工艺稳定性和封装 |

## 代表论文与综述

| 年份 | 题名 | 来源 | 价值 |
| --- | --- | --- | --- |
| 2025 | Compact Spectral Imaging: A Review of Miniaturized and Integrated Systems | Laser & Photonics Reviews | 微型/集成光谱成像总入口 |
| 2025 | Reconstructive spectrometers: hardware miniaturization and computational reconstruction | eLight | 重构型光谱仪综述，适合理解硬件编码和计算重建 |
| 2025 | Research progress of novel on-chip multispectral photodetectors | Infrared and Laser Engineering | 中文综述，聚焦片上多光谱探测器路线 |
| 2024 | A broadband hyperspectral image sensor with high spatio-temporal resolution | Nature | 宽带、高时空分辨率和片上调制材料的代表工作 |
| 2023 | Video-rate hyperspectral camera based on a CMOS-compatible random array of Fabry-Perot filters | Nature Photonics | CMOS 兼容随机滤波阵列和视频级高光谱 |
| 2025 | A Spatiotemporal Tunable Filter Array Chip for Video-Rate Hyperspectral Imaging | Advanced Science | 时空可调滤波阵列，连接硬件调制和视频级重建 |
| 2022 | Dynamic brain spectrum acquired by a real-time ultraspectral imaging chip with reconfigurable metasurfaces | Optica | 可重构超表面和生物成像演示 |
| 2022 | Ultraspectral Imaging Based on Metasurfaces with Freeform Shaped Meta-Atoms | Laser & Photonics Reviews | 自由形状 meta-atom 谱编码 |
| 2024 | Angle-Insensitive Spectral Imaging Based on Topology-Optimized Plasmonic Metasurfaces | Laser & Photonics Reviews | 角度不敏感是超表面落地的重要问题 |
| 2024 | Multispectral imaging through metasurface with quasi-bound states in the continuum | Optics Express | quasi-BIC 窄带调制路线 |
| 2022 | On-chip short-wave infrared multispectral detector based on integrated Fabry-Perot microcavities array | Chinese Optics Letters | SWIR InGaAs + FP 微腔阵列 |
| 2023 | Longwave infrared multispectral image sensor system using aluminum-germanium plasmonic filter arrays | Nano Research | LWIR 非制冷/热探测方向 |
| 2025 | Long-wave infrared computational multispectral metasurface and spectral reconstruction method | Scientific Reports | LWIR 超表面 + 计算重建 |
| 2025 | Gas detection based on a mid-infrared super-pixel multi-spectral imaging device | Applied Optics | MIR 多谱段气体检测应用 |

## 最近检索补充

2026-07-02 使用 arXiv 检索补充了以下候选。它们不都属于片上成像硬件，但能补充重建、压缩感知和微型光谱仪方向。

| arXiv | 年份 | 题名 | 用途 |
| --- | --- | --- | --- |
| [2303.09773](https://arxiv.org/abs/2303.09773) | 2023 | Progressive Content-aware Coded Hyperspectral Compressive Imaging | 压缩高光谱重建算法参考 |
| [2210.07684](https://arxiv.org/abs/2210.07684) | 2022 | End-to-end joint optimization of metasurface and image processing for compact snapshot hyperspectral imaging | 超表面和后端处理联合优化 |
| [2402.18935](https://arxiv.org/abs/2402.18935) | 2024 | Miniaturized on-chip spectrometer enabled by electrochromic modulation | 电致变色调制微型光谱仪 |
| [2308.07764](https://arxiv.org/abs/2308.07764) | 2023 | Miniaturized Computational Photonic Molecule Spectrometer | 计算型光子分子光谱仪 |
| [2401.01196](https://arxiv.org/abs/2401.01196) | 2024 | Broadband miniaturized spectrometers with a van der Waals tunnel diode | 范德华隧穿二极管宽带微型光谱仪 |
| [2508.12077](https://arxiv.org/abs/2508.12077) | 2025 | Reconfigurable miniaturized computational spectrometer enabled by photoelastic effect | 可重构计算光谱仪候选，需后续核验 |
| [2508.20566](https://arxiv.org/abs/2508.20566) | 2025 | Physics-informed neural network enhanced multispectral single-pixel imaging with a chip spectral sensor | 芯片光谱传感器 + PINN 单像素成像候选，需后续核验 |

## 本地 PDF 副本

已保存的开放论文副本位于 `80-sources/papers/`。本页只列索引，具体文件维护见 [[./papers/README|本地论文副本目录]]。

| 论文 | 本地状态 |
| --- | --- |
| Bian et al., Nature 2024 | `2024_Bian_Nature_Broadband_Hyperspectral_Image_Sensor.pdf` |
| Xiong et al., Optica 2022 | `2022_Xiong_Optica_Ultraspectral_Imaging_Chip.pdf` |
| Yang et al., LPR 2024 | `2024_Yang_LPR_Angle_Insensitive_Spectral_Imaging.pdf` |
| Shao et al., Optics Express 2024 | `2024_Shao_OE_Multispectral_Metasurface_QBIC.pdf` |
| Chip / arXiv 2023 | `2023_Chip_Deep_Learning_On_Chip_Rapid_Spectral_Imaging.pdf` |
| Shaik et al., Nano Research 2023 | `2023_Shaik_NanoResearch_LWIR_Multispectral_AlGe_Plasmons.pdf` |
| Wang et al., Scientific Reports 2025 | `2025_Wang_SciRep_LWIR_Computational_Multispectral_Metasurface.pdf` |
| eLight 2025 综述 | `2025_eLight_Reconstructive_Spectrometers_Review.pdf` |
| IRL 2025 中文综述 | `2025_IRL_Novel_On_Chip_Multispectral_Photodetectors_Review.pdf` |

## 跟踪字段

新增论文进入知识库前，至少记录这些字段：

- 波段：VIS-NIR、SWIR、MWIR、LWIR 或宽带。
- 结构：MSFA、FP 微腔、超表面、波导、可调材料、新型探测器。
- 是否快照：单帧、多帧、扫描或可调。
- 谱通道数和有效分辨率。
- 空间分辨率、帧率和样机面积。
- 是否需要制冷。
- 重建方法：线性反演、正则化、压缩感知、深度学习、物理约束网络。
- 标定条件：角度、温度、偏振、批次漂移。
- 验证场景：标准光源、自然场景、生物样本、工业样品、气体、热目标。
- 可落地风险：工艺一致性、光通量、信噪比、算法泛化、封装和成本。

## 检索关键词

```text
on-chip multispectral imaging
on-chip hyperspectral imaging
integrated spectral imaging sensor
CMOS-compatible hyperspectral camera
multispectral filter array CMOS image sensor
pixel-level spectral filter array
snapshot hyperspectral imaging chip
metasurface spectral imaging
computational spectral imaging sensor
reconstructive spectrometer
miniaturized integrated spectrometer
on-chip multispectral photodetector
SWIR multispectral detector chip
MWIR multispectral filter array
LWIR multispectral metasurface
```

```text
片上多光谱成像
片上高光谱成像
片上光谱成像芯片
多光谱滤波阵列
像素级光谱滤波阵列
超表面光谱成像
计算光谱成像
重构型光谱仪
多光谱光电探测器
短波红外多光谱探测器
中波红外多光谱成像
长波红外多光谱超表面
```

## 维护节奏

- 每季度检索一次 arXiv、Optica、Nature Portfolio、Wiley、Springer、IEEE 和中文红外/光学期刊。
- 优先补综述，其次补能改变技术路线判断的系统论文。
- 普通算法论文只有在影响片上系统建模、标定或重建边界时才进入本页。
- 每次更新都要同步检查 [[../30-domains/005-on-chip-multispectral|专题主入口]]、[[../40-devices/013-on-chip-spectral-sensor|片上光谱传感器]] 和相关概念页是否需要调整。
