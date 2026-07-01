---
id: device.on-chip-spectral-sensor
title: 片上光谱传感器
type: device
domains: [spectroscopy, on-chip-multispectral]
status: reviewed
aliases:
  - on-chip-spectral-sensor
  - 片上光谱传感器
  - 芯片级光谱传感器
  - 集成光谱传感器
---

# 片上光谱传感器

## 定义/概述

片上光谱传感器（On-chip Spectral Sensor）是把**光谱分光/编码功能与光电探测功能集成在同一芯片或同一封装内**的微型光谱器件。它不再需要传统光谱仪中的入射狭缝、光栅、棱镜、扫描机构等分立元件，目标是在芯片尺度上完成“光 → 光谱编码 → 电信号 → 光谱重建”的完整链路。

典型形态包括：

- 多光谱滤光片阵列（MSFA）+ CMOS/InGaAs 焦平面；
- Fabry–Pérot 微腔阵列 + 探测器焦平面；
- 超表面/纳米结构编码层 + 单像素或阵列探测器；
- 硅光子/波导型片上光谱仪；
- 量子点、纳米线、二维材料等新型光谱敏感结构。

---

## 关键参数

| 参数 | 符号 | 典型范围 | 说明 |
| --- | --- | --- | --- |
| 光谱通道数 | $M$ | 4 ~ 256 | 片上可分辨或重建的谱段数量 |
| 光谱分辨率 | Δλ | 1 ~ 100 nm | 相邻通道可分辨的最小波长间隔 |
| 光谱范围 | λ | 可见 ~ LWIR | 取决于探测器材料和编码结构 |
| 空间分辨率 | — | 与探测器像素数相关 | MSFA 方案会因通道数下降 |
| 帧率 | fps | 30 ~ 1000+ | 快照式通常高于扫描式 |
| 尺寸 | — | mm² 级 | 芯片或模组级集成 |
| 功耗 | — | mW ~ W 级 | 制冷型 MWIR/LWIR 功耗较高 |
| 信噪比 | SNR | 30 ~ 60 dB | 受光通量、探测器噪声限制 |

---

## 主流技术路线

| 路线 | 核心结构 | 波段 | 优点 | 缺点 |
| --- | --- | --- | --- | --- |
| **MSFA + 焦平面** | 马赛克式滤光片阵列 | VIS–SWIR | 工艺成熟、快照式 | 空间分辨率下降 |
| **FP 微腔阵列** | 不同腔厚的 Fabry–Pérot 腔 | VIS–LWIR | 窄带、集成度高 | 入射角敏感、工艺难 |
| **超表面编码** | 纳米结构阵列 | VIS–LWIR | 极薄、设计自由 | 标定复杂、角度敏感 |
| **波导/硅光子** | AWG、微环、光栅 | VIS–NIR | 分辨率高、CMOS 兼容 | 与二维成像结合难 |
| **新型材料** | 量子点、纳米线、2D 材料 | 可调 | 体积小、可溶液加工 | 稳定性、一致性待提升 |

---

## 选型要点

1. **波段决定探测器材料**：
   - VIS–NIR：硅 CMOS/CCD
   - SWIR：InGaAs
   - MWIR：InSb、MCT（通常需制冷）
   - LWIR：微测辐射热计、MCT、QWIP

2. **光谱分辨率需求**：
   - 粗略分类：MSFA 4–16 通道足够；
   - 精细识别：需要 FP 微腔或超表面 + 重建算法。

3. **动态 vs 静态场景**：
   - 动态目标优先快照式（MSFA、超表面）；
   - 静态/高精度优先扫描或可调谐方案。

4. **算法平台**：
   - 计算型传感器需要配套标定和重建算法；
   - 评估方案时必须把算法开发和算力成本计入。

5. **标定与稳定性**：
   - 超表面、FP 微腔对入射角、温度、工艺偏差敏感；
   - 量产前必须建立标定流程和补偿模型。

---

## 常见型号/平台（按路线）

| 厂商/机构 | 代表产品/工作 | 路线 | 波段 |
| --- | --- | --- | --- |
| **imec** | SNAPSCAN / MSFA 传感器 | MSFA | VIS–NIR |
| **Silios** | 多光谱滤光片阵列 | MSFA | VIS–NIR |
| **长光辰芯** | InGaAs 高光谱传感器 | MSFA / 线扫 | SWIR |
| **海谱纳米** | 国产高光谱相机/芯片 | 多种 | VIS–SWIR |
| **Bian et al., Nature 2024** | 96 通道超表面高光谱传感器 | 超表面编码 | VIS–NIR |
| **Xiong et al., Optica 2022** | 可重构超表面超光谱芯片 | 超表面 | VIS–NIR |
| **Xuan et al., COL 2022** | FP 微腔 + InGaAs FPA | FP 微腔 | SWIR |
| **Shaik et al., Nano Research 2023** | Al-Ge 等离激元滤波阵列 + 热探测器 | 等离激元 | LWIR |

---

## 关键关系

- 相关概念：[[../10-concepts/multispectral-imaging|多光谱成像]]
- 相关概念：[[../10-concepts/hyperspectral-imaging|高光谱成像]]
- 相关概念：[[../10-concepts/snapshot-spectral-imaging|快照式光谱成像]]
- 相关概念：[[../10-concepts/multispectral-filter-array|多光谱滤光片阵列]]
- 相关概念：[[../10-concepts/fabry-perot-microcavity|Fabry–Pérot 微腔]]
- 相关概念：[[../10-concepts/metasurface|超表面]]
- 相关概念：[[../10-concepts/spectral-reconstruction|光谱重建]]
- 相关设备：[[./ingaas-focal-plane-array|InGaAs 焦平面阵列]]
- 相关设备：[[./mct-detector|MCT 探测器]]
- 相关设备：[[./ir-thermal-detector|红外热像仪探测器]]（含微测辐射热计）
- 相关设备：[[./hyperspectral-camera|高光谱相机]]
- 相关设备：[[./bandpass-filter|窄带滤光片]]
- 相关领域：[[../30-domains/on-chip-multispectral|片上多光谱成像]]
- 相关文献：[[../80-sources/on-chip-multispectral-literature|片上多光谱/高光谱文献与学习路线]]

---

## 常见误区

1. **片上 = 性能一定差**：片上化牺牲的是通用性，但特定应用下的光谱分辨率、速度和集成度可以优于传统光谱仪。
2. **所有片上传感器都快照式**：部分方案仍需要时序调制或多帧合成。
3. **探测器材料可任意扩展**：硅基到 SWIR/MWIR/LWIR 需要完全不同的材料和工艺。
4. **只买硬件就够了**：计算型片上传感器必须配套标定矩阵和重建算法，软件成本不可忽视。
5. **实验室性能 = 量产性能**：纳米结构和微腔的一致性、温漂、老化会显著影响批次间差异。

---

## 来源

- 片上多光谱/高光谱文献与学习路线
- imec / Silios / 长光辰芯 / 海谱纳米 技术白皮书
- IEEE / Optica / Nature Photonics 片上光谱成像论文
