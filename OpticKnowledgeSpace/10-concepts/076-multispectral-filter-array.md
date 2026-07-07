---
id: concept.multispectral-filter-array
title: 多光谱滤光片阵列
type: concept
domains: [spectroscopy, on-chip-multispectral]
status: reviewed
aliases:
  - multispectral-filter-array
  - MSFA
  - 多光谱滤光片阵列
  - 马赛克式多光谱滤波
---

# 多光谱滤光片阵列

## 定义

多光谱滤光片阵列（Multispectral Filter Array, MSFA）是一种在图像传感器像素面上周期性或非周期性排布的**多种窄带滤光片**结构。它把传统相机的 Bayer 彩色滤光阵列（RGB）扩展到更多谱段，使每个像素只采集一个特定波段，从而在一次曝光中获取多光谱信息。

MSFA 是实现**快照式多光谱成像**最成熟的片上方案之一。

---

## 直观理解

![[attachments/visuals/multispectral-filter-array.svg]]

普通彩色相机使用 Bayer 阵列：

```text
G R G R
B G B G
G R G R
```

每个像素上方只有红、绿或蓝一种滤光片，后续通过去马赛克恢复每个像素的全彩色。

MSFA 把这一思想扩展到 4–16 个甚至更多波段：

```text
λ1 λ2 λ3 λ4
λ3 λ4 λ1 λ2
λ2 λ1 λ4 λ3
λ4 λ3 λ2 λ1
```

每个像素只测一个波段，通过**空域插值 + 光谱重建**恢复每个像素的多光谱立方体。

---

## 关键参数

| 参数 | 含义 | 典型值 |
| --- | --- | --- |
| 通道数 | 同时成像的波段数量 | 4–16（工业），可达 25+（科研） |
| 中心波长 | 每个滤光片的峰值透过波长 | 可见、NIR、SWIR、MWIR、LWIR 均可 |
| 半高全宽 FWHM | 滤光片带宽 | 10–100 nm |
| 峰值透过率 | 中心波长处透过比例 | 50–90% |
| 串扰 | 相邻像素/通道的光谱泄漏 | < 5%（优良），< 10%（可接受） |
| 图案周期 | 一个完整滤波单元重复的像素数 | 与通道数相关，如 4×4 对应 16 通道 |

---

## 与 Bayer 阵列的对比

| 维度 | Bayer 彩色滤光阵列 | MSFA |
| --- | --- | --- |
| 通道数 | 3（R/G/B） | 4–16+ |
| 带宽 | 宽（数十 nm） | 窄（10–100 nm） |
| 去马赛克 | 恢复 RGB | 恢复多光谱立方体 |
| 信息量 | 颜色感知 | 物质识别、成分反演 |
| 工艺成熟度 | 极高 | 中高，取决于通道数和波段 |

---

## 适用场景

- **精准农业**：NDVI、NDRE 等植被指数计算。
- **食品检测**：成熟度、损伤、异物识别。
- **工业分选**：塑料、矿物、药片按材质分类。
- **医学成像**：组织氧合、血氧、病变边界。
- **遥感**：轻小型多光谱相机。
- **片上系统集成**：与 CMOS、InGaAs、MCT 焦平面直接集成。

---

## 关键关系

- 相关概念：[[./072-multispectral-imaging|多光谱成像]]
- 相关概念：[[./075-snapshot-spectral-imaging|快照式光谱成像]]
- 相关概念：[[./079-spectral-reconstruction|光谱重建]]
- 相关概念：[[./077-fabry-perot-microcavity|Fabry–Pérot 微腔]]（MSFA 的滤波单元实现方式之一）
- 相关领域：[[../30-domains/005-on-chip-multispectral|片上多光谱成像]]
- 相关文献：[[../80-sources/009-on-chip-multispectral-literature|片上多光谱/高光谱文献雷达]]

---

## 常见误区

1. **MSFA 直接输出每个像素的光谱曲线**：实际上每个像素只测一个波段，必须通过去马赛克和光谱重建恢复完整光谱。
2. **通道越多越好**：通道数增加会降低每个波段的空间采样率，增加数据量和重建难度。
3. **滤光片越窄越好**：窄带滤光片光通量低、信噪差，且对工艺偏差更敏感。
4. **MSFA 图案必须周期性**：随机或伪随机 MSFA 有时能改善重建条件，但去马赛克更复杂。
5. **不同通道之间完全独立**：实际中存在光谱串扰和空间串扰，必须在重建模型中考虑。

---

## 教材参考

- [[../80-sources/002-hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/003-saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]]：适合核对探测器、光与物质相互作用、光子学器件和现代光学系统。
- [[../80-sources/009-on-chip-multispectral-literature|片上多光谱/高光谱文献雷达]]：适合核对超表面、滤波阵列、快照式光谱成像和光谱重建等前沿主题。
- [[../80-sources/001-Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 来源

- M. Yamaguchi et al., "Multispectral Filter Array for Spectral Imaging", *Optics Express*, 2010s
- Silios / Ximea 等多光谱传感器厂商技术文档
- 片上多光谱/高光谱文献清单中的 MSFA 相关论文
