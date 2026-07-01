---
id: device.ingaas-focal-plane-array
title: InGaAs 焦平面阵列
type: device
domains: [spectroscopy, on-chip-multispectral, infrared-imaging]
status: reviewed
aliases:
  - ingaas-focal-plane-array
  - InGaAs FPA
  - 铟镓砷焦平面阵列
  - 短波红外探测器
---

# InGaAs 焦平面阵列

## 定义/概述

InGaAs 焦平面阵列（Indium Gallium Arsenide Focal Plane Array, InGaAs FPA）是以**铟镓砷（InGaAs）**为光吸收层的二维光电探测器阵列。由于 InGaAs 的禁带宽度可通过 In/Ga 组分调节，其响应波长通常覆盖 **0.9–1.7 μm**（短波红外，SWIR），是 SWIR 波段最成熟、最常用的成像探测器。

InGaAs FPA 是多光谱/高光谱成像、激光雷达、光通信、半导体检测、水分检测等领域的核心器件。

---

## 工作原理

InGaAs 属于 III-V 族化合物半导体。光子能量大于其禁带宽度时，价带电子跃迁至导带，产生电子-空穴对；在外加偏压下形成光电流，经读出电路（ROIC）积分并转换为数字信号。

通过调节 In 组分 $x$：

$$
\text{In}_{x}\text{Ga}_{1-x}\text{As}
$$

- $x \approx 0.53$：晶格与 InP 衬底匹配，截止波长约 1.7 μm；
- $x > 0.53$：扩展 InGaAs，截止波长可达 2.5 μm，但晶格失配导致暗电流增加。

---

## 关键参数

| 参数 | 符号 | 典型范围 | 说明 |
| --- | --- | --- | --- |
| 响应波段 | λ | 0.9–1.7 μm（标准）<br>0.9–2.5 μm（扩展） | SWIR 主覆盖范围 |
| 峰值量子效率 | QE | 70% ~ 90% | 1.0–1.6 μm 区间 |
| 暗电流 | $I_d$ | 1–1000 nA/cm² | 温度越低越小，高端器件需热电制冷 |
| 读出噪声 | $e_{read}$ | 50–500 e⁻ | 取决于 ROIC 设计 |
| 像元尺寸 | — | 5–30 μm | 小像元提高空间分辨率，但降低阱深 |
| 阵列规模 | — | 320×256 ~ 1280×1024 | 科研/工业级 |
| 帧率 | fps | 30 ~ 1000+ | 窗口模式可达更高帧率 |
| 制冷 | — | 非制冷 / TE 制冷 | 高端科研常用 TE 或斯特林制冷 |

---

## 类型对比

| 类型 | 响应波段 | 暗电流 | 成本 | 典型应用 |
| --- | --- | --- | --- | --- |
| **标准 InGaAs** | 0.9–1.7 μm | 低 | 中 | 工业检测、光通信、农业 |
| **扩展 InGaAs** | 0.9–2.5 μm | 较高 | 高 | 气体检测、矿物识别、特殊光谱 |
| **InGaAs PIN 线阵** | 0.9–1.7 μm | 低 | 中 | 光谱仪、推扫式高光谱 |
| **InGaAs FPA 面阵** | 0.9–1.7 μm | 低 | 中高 | 成像、快照式多光谱 |

---

## 选型要点

1. **波段匹配**：标准 1.7 μm 足以覆盖水分、塑料、硅片等常见 SWIR 应用；气体检测可能需要扩展 2.5 μm。
2. **制冷需求**：
   - 非制冷：成本低、启动快，适合工业在线；
   - TE 制冷：降低暗电流，提高信噪比，适合弱光或长曝光。
3. **像元尺寸与镜头**：小像元需要更高分辨率镜头，但进光量下降；需按物距和 GSD 匹配。
4. **读出模式**：全局快门适合动态目标，卷帘快门成本低但存在果冻效应。
5. **接口与数据率**：高帧率大面阵需要 Camera Link、GigE Vision 10GigE 或 CoaXPress。
6. **与滤光片集成**：多光谱应用需确认是否支持背照式 FP 微腔/滤光片集成工艺。

---

## 常见型号/品牌

| 品牌 | 国家 | 代表系列 | 特点 |
| --- | --- | --- | --- |
| **Sensors Unlimited（Collins）** | 美国 | GA/GT 系列 | 高可靠性、军工级 |
| **Teledyne FLIR** | 美国 / 瑞典 | BOSON / Neutrino（部分 SWIR） | 集成度高 |
| **Hamamatsu** | 日本 | G16100 / C12741 等 | 科研级、线阵/面阵 |
| **Xenics** | 比利时 | Bobcat / Cheetah / Wildcat | 工业/科研兼顾 |
| **长光辰芯** | 中国 | InGaAs 系列 | 国产替代、面阵 |
| **海谱纳米** | 中国 | 高光谱相机模组 | 国产 InGaAs 高光谱方案 |

---

## 关键关系

- 相关概念：[[../10-concepts/multispectral-imaging|多光谱成像]]
- 相关概念：[[../10-concepts/hyperspectral-imaging|高光谱成像]]
- 相关概念：[[../10-concepts/fabry-perot-microcavity|Fabry–Pérot 微腔]]（常与 InGaAs 集成做 SWIR 多光谱）
- 相关设备：[[./on-chip-spectral-sensor|片上光谱传感器]]
- 相关设备：[[./hyperspectral-camera|高光谱相机]]
- 相关设备：[[./bandpass-filter|窄带滤光片]]
- 相关领域：[[../30-domains/on-chip-multispectral|片上多光谱成像]]
- 相关领域：[[../30-domains/infrared-imaging|红外成像]]
- 相关文献：[[../80-sources/on-chip-multispectral-literature|片上多光谱/高光谱文献与学习路线]]

---

## 常见误区

1. **InGaAs 能看到热量**：InGaAs 主要响应 SWIR 反射光，不是热辐射成像（热辐射在 LWIR）。
2. **所有 SWIR 相机都用 InGaAs**：SWIR 也可用量子点、扩展硅、Ge 等，但 InGaAs 最成熟。
3. **响应到 1.7 μm 就停止**：实际响应是逐渐下降的，截止波长通常指 QE 降至 50% 的点。
4. **扩展 InGaAs 只是软件设置**：需要改变材料组分，是硬件差异，成本和暗电流显著不同。
5. **InGaAs FPA 不需要制冷**：长曝光或弱光下暗电流会显著影响信噪比，TE 制冷很常见。

---

## 来源

- Sensors Unlimited / Teledyne FLIR / Hamamatsu 产品手册
- 红外探测器教材（Rogalski, *Infrared Detectors*）
- 片上多光谱/高光谱文献清单中的 SWIR 探测器论文
