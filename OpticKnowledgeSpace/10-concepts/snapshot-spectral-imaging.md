---
id: concept.snapshot-spectral-imaging
title: 快照式光谱成像
type: concept
domains: [spectroscopy, on-chip-multispectral]
status: reviewed
aliases:
  - snapshot-spectral-imaging
  - 快照式光谱成像
  - 单次曝光光谱成像
---

# 快照式光谱成像

## 定义

快照式光谱成像（Snapshot Spectral Imaging）是指通过**单次曝光**同时获取场景二维空间信息和一维光谱信息的技术。与传统扫描式（点扫描、线扫描、波长扫描）不同，它不需要机械运动或时间扫描，就能在一次拍摄中得到完整或压缩后的三维数据立方体 $I(x, y, \lambda)$。

快照式是片上多光谱/高光谱系统最偏爱的采集方式，因为它与实时成像、动态目标和便携设备高度兼容。

---

## 直观理解

传统推扫式高光谱相机像一台“光谱扫描仪”：你需要让相机或目标移动，逐行扫描才能拼出完整的数据立方体。

快照式则像一台“光谱快照相机”：按一次快门，就同时拿到空间和光谱信息。代价是每个像素或每次测量只能获得部分光谱信息，需要后续算法重建完整立方体。

---

## 主要技术路线

| 技术 | 原理 | 优点 | 缺点 |
| --- | --- | --- | --- |
| **MSFA** | 每个像素上方覆盖不同窄带滤光片 | 与 CMOS 工艺兼容、结构简单 | 空间分辨率下降、需去马赛克 |
| **计算层析光谱成像（CTIS）** | 用衍射光栅产生多个级次投影 | 单次曝光、无滤光片 | 重建复杂、光通量分配 |
| **编码孔径快照光谱成像（CASSI）** | 用编码模板和色散元件压缩采样 | 压缩感知框架成熟 | 需要标定和重建算法 |
| **光场光谱成像** | 同时记录空间角度和光谱 | 可后期重聚焦 | 数据量大、分辨率权衡 |
| **超表面/计算光谱成像** | 纳米结构编码 + 算法重建 | 极薄、集成度高 | 标定要求高、角度敏感 |
| **可调谐滤波器 + 少帧成像** | 液晶/MEMS 快速切换滤波状态 | 分辨率高、动态可控 | 严格说不是单帧，但接近快照体验 |

---

## 关键权衡

快照式光谱成像面临一个基本约束：

$$
\text{空间分辨率} \times \text{光谱分辨率} \times \text{时间分辨率} \leq \text{常数}
$$

- 要提高光谱分辨率，通常会牺牲空间分辨率或光通量；
- 要提高空间分辨率，通常需要减少通道数或增加传感器像素；
- 要提高帧率，需要缩短曝光时间，从而降低信噪比。

片上系统设计就是在这个约束下寻找最佳平衡点。

---

## 适用场景

- **工业在线检测**：传送带高速运动目标，无法扫描。
- **无人机/卫星遥感**：平台运动导致推扫几何复杂，快照更稳定。
- **生物医学**：活体组织、血流、荧光动态过程。
- **机器视觉**：机器人实时材质识别与分选。
- **军事/安防**：高速目标跟踪、伪装识别。
- **消费级设备**：手机/便携多光谱模组。

---

## 关键关系

- 相关概念：[[./multispectral-imaging|多光谱成像]]
- 相关概念：[[./hyperspectral-imaging|高光谱成像]]
- 相关概念：[[./multispectral-filter-array|多光谱滤光片阵列]]
- 相关概念：[[./spectral-reconstruction|光谱重建]]
- 相关概念：[[./metasurface|超表面]]
- 相关概念：[[./fabry-perot-microcavity|Fabry–Pérot 微腔]]
- 相关领域：[[../30-domains/on-chip-multispectral|片上多光谱成像]]
- 相关文献：[[../80-sources/on-chip-multispectral-literature|片上多光谱/高光谱文献与学习路线]]

---

## 常见误区

1. **快照式 = 直接输出完整数据立方体**：多数快照式系统只采集压缩或欠采样数据，仍需重建。
2. **快照式一定比推扫式好**：推扫式在光谱精度、信噪比、系统简单性上仍有优势，实验室和静态场景常用。
3. **所有快照式都无运动部件**：部分“快照”方案使用液晶/MEMS 快速调制，本质上仍有动态元件。
4. **空间分辨率不会损失**：MSFA 等方案每个像素只采一个波段，空间分辨率必然下降或需插值。
5. **快照式不需要标定**：恰恰相反，重建算法严重依赖精确的系统响应标定。

---

## 教材参考

- [[../80-sources/hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]]：适合核对探测器、光与物质相互作用、光子学器件和现代光学系统。
- [[../80-sources/on-chip-multispectral-literature|片上多光谱/高光谱文献与学习路线]]：适合核对超表面、滤波阵列、快照式光谱成像和光谱重建等前沿主题。
- [[../80-sources/Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 来源

- Wagadarikar et al., "Video Rate Spectral Imaging Using a Coded Aperture Snapshot Spectral Imager", *Optics Express*, 2009
- Lin et al., "Low-cost, high-speed multispectral imager via spatiotemporal modulation", *Optics Express*, 2023
- 片上多光谱/高光谱文献清单中的快照/视频级光谱成像论文
