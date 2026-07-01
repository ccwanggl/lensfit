---
id: device.mct-detector
title: MCT 探测器
type: device
domains: [spectroscopy, on-chip-multispectral, infrared-imaging]
status: reviewed
aliases:
  - mct-detector
  - MCT 探测器
  - 碲镉汞探测器
  - HgCdTe detector
  - mercury-cadmium-telluride
---

# MCT 探测器

## 定义/概述

MCT 探测器（Mercury Cadmium Telluride Detector，HgCdTe）是以**碲镉汞（HgCdTe）**为光敏材料的半导体红外探测器。通过调节 Cd 组分 $x$，可以连续调控禁带宽度，从而覆盖从 **SWIR 到 LWIR** 的宽广红外波段。MCT 是目前高性能 MWIR（3–5 μm）和 LWIR（8–14 μm）探测器的首选材料之一。

在片上多光谱领域，MCT 常与像素级滤光片阵列、超表面或 FP 微腔集成，实现 MWIR/LWIR 的多光谱/高光谱成像。

---

## 工作原理

HgCdTe 的禁带宽度 $E_g$ 与 Cd 组分 $x$ 相关：

$$
E_g(x, T) \approx -0.295 + 1.87x + 0.28x^2 - (6.0 \times 10^{-4}) T \quad [\text{eV}]
$$

- **$x$** —— Cd 组分（0–1）
- **$T$** —— 温度（K）

截止波长：

$$
\lambda_c = \frac{1.24}{E_g} \quad [\mu\text{m}]
$$

- $x \approx 0.3$：LWIR（8–14 μm）
- $x \approx 0.3–0.4$：MWIR（3–5 μm）
- $x \approx 0.5$：SWIR（1–2.5 μm）

---

## 关键参数

| 参数 | 符号 | 典型范围 | 说明 |
| --- | --- | --- | --- |
| 响应波段 | λ | 1–14 μm（可调） | 由 Cd 组分和制冷温度决定 |
| 工作温度 | $T$ | 77 K（液氮）~ 200 K | 通常需制冷以降低暗电流 |
| 量子效率 | QE | 60% ~ 90% | 高端器件接近 90% |
| 暗电流 | $I_d$ | 极低（制冷后） | 优于多数红外探测器 |
| 探测率 | $D^*$ | $10^{10} \sim 10^{12}$ Jones | 高性能 MWIR/LWIR 指标 |
| 阵列规模 | — | 128×128 ~ 4K×4K | 军用/航天级大面阵 |
| 帧率 | fps | 30 ~ 1000+ | 取决于读出电路 |

---

## 类型对比

| 类型 | 波段 | 工作温度 | 优点 | 缺点 |
| --- | --- | --- | --- | --- |
| **PV-MCT（光伏型）** | MWIR/LWIR | 77 K | 响应快、探测率高 | 工艺复杂、成本高 |
| **PC-MCT（光导型）** | MWIR/LWIR | 77 K | 结构简单 | 需偏置、噪声较大 |
| **HDVIP** | MWIR/LWIR | 77–100 K | 高填充因子、低串扰 | 工艺专有加法 |
| **MWIR MCT FPA** | 3–5 μm | 80–110 K | 高温目标、气体检测 | 需制冷 |
| **LWIR MCT FPA** | 8–14 μm | 77 K | 热成像、远距离探测 | 成本高、低温制冷 |

---

## 选型要点

1. **波段与 Cd 组分**：明确目标波段后选择对应的 MCT 组分，不能通过软件改变。
2. **制冷方式**：
   - 液氮杜瓦：实验室、低成本；
   - 斯特林制冷机：便携式、军品；
   - 热电制冷：仅适用于 SWIR 或高温工作 MCT。
3. **暗电流与探测率**：弱光或长距离探测需选高 $D^*$、低暗电流器件。
4. **读出电路集成**：FPA 需配套 ROIC，评估时应同时考虑探测器+ROIC 性能。
5. **片上多光谱集成**：MWIR/LWIR 多光谱常采用像素级 FP 微腔或超表面与 MCT FPA 集成，需确认工艺兼容性。
6. **成本与维护**：MCT 比 InSb、InGaAs、微测辐射热计成本高，制冷系统需定期维护。

---

## 常见型号/品牌

| 品牌 | 国家 | 代表产品 | 特点 |
| --- | --- | --- | --- |
| **Teledyne FLIR / Indigo** | 美国 | SCD / HOT MCT | 高性能、军品级 |
| **Lynred（前 Sofradir）** | 法国 | DAPHNIS / NEPTUNE | 欧洲主流 MCT |
| **AIM Infrarot-Module** | 德国 | IR 系列 | 德制高端 MCT |
| **Selex / Leonardo** | 意大利 | HgCdTe FPA | 航天/军用 |
| **昆明物理研究所** | 中国 | MCT 焦平面 | 国产替代 |
| **上海技物所** | 中国 | HgCdTe 探测器 | 航天遥感应用 |

---

## 关键关系

- 相关概念：[[../10-concepts/multispectral-imaging|多光谱成像]]
- 相关概念：[[../10-concepts/hyperspectral-imaging|高光谱成像]]
- 相关概念：[[../10-concepts/fabry-perot-microcavity|Fabry–Pérot 微腔]]
- 相关概念：[[../10-concepts/metasurface|超表面]]
- 相关设备：[[./on-chip-spectral-sensor|片上光谱传感器]]
- 相关设备：[[./ingaas-focal-plane-array|InGaAs 焦平面阵列]]（SWIR 替代方案）
- 相关设备：[[./ir-thermal-detector|红外热像仪探测器]]（含微测辐射热计，LWIR 替代方案）
- 相关领域：[[../30-domains/on-chip-multispectral|片上多光谱成像]]
- 相关领域：[[../30-domains/infrared-imaging|红外成像]]
- 相关文献：[[../80-sources/on-chip-multispectral-literature|片上多光谱/高光谱文献与学习路线]]

---

## 常见误区

1. **MCT 是单一材料**：HgCdTe 是三元化合物，性能强烈依赖 Cd 组分 $x$ 和生长质量。
2. **MCT 可室温工作**：标准高性能 MCT 必须制冷到 77–110 K；只有特殊高温 MCT 可在较高温度工作。
3. **MCT 比微测辐射热计更好**：微测辐射热计成本低、无需制冷，适合一般热成像；MCT 在灵敏度、响应速度上更优，但系统复杂。
4. **波段调节像 InGaAs 一样简单**：InGaAs 通过组分微调可扩展波段；MCT 组分改变影响更大，通常按目标波段专门生长。
5. **MCT 只用于军用**：虽然军用量大，但在气体检测、天文、医疗光谱、工业高温监测中也很重要。

---

## 来源

- Rogalski, *Infrared Detectors* (2nd ed.)
- Teledyne FLIR / Lynred / AIM 产品手册
- 片上多光谱/高光谱文献清单中的 MWIR/LWIR 探测器论文
