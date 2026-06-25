---
id: map.concepts
title: 概念
type: map
status: maintained
---

# 概念

存放稳定、可复用的领域概念。每个概念应尽量说明定义、适用范围、边界条件和关联概念。

## 命名与入口

概念文件优先使用英文 slug 作为稳定链接目标，例如 `focal-length.md`、`diffraction-limit.md`。中文检索需要保留时，可以维护同名中文镜像页，但镜像页应指向稳定 slug，避免两份内容长期分叉。

## 已收录概念

| 概念 | 文件 | 核心定义 |
|------|------|---------|
| **折射率** | [[refractive-index|refractive-index.md]] | 光在介质中速度的比值 |
| **艾里斑** | [[airy-disk|airy-disk.md]] | 圆孔衍射的极限光斑 |
| **衍射极限** | [[diffraction-limit|diffraction-limit.md]] | 理想系统仍受波动衍射限制的分辨率上限 |
| **焦距** | [[focal-length|focal-length.md]] | 平行光汇聚点到透镜中心的距离 |
| **F值** | [[f-number|f-number.md]] | F# = f/D，无量纲光圈值 |
| **景深** | [[depth-of-field|depth-of-field.md]] | 图像保持可接受清晰的范围 |
| **像圈** | [[image-circle|image-circle.md]] | 镜头能均匀成像的圆形区域 |
| **奈奎斯特频率** | [[nyquist-frequency|nyquist-frequency.md]] | 传感器能分辨的最高空间频率 |
| **像元** | [[pixel|pixel.md]] | 传感器的最小光敏单元 |
| **混叠** | [[aliasing|aliasing.md]] | 采样频率不足导致的虚假信号 |
| **色差** | [[chromatic-aberration|chromatic-aberration.md]] | 不同波长光聚焦位置不同 |
| **偏振** | [[polarization|polarization.md]] | 光波电场矢量振动方向的状态 |
| **干涉** | [[interference|interference.md]] | 多束相干光叠加形成强弱分布 |
| **衍射光栅** | [[diffraction-grating|diffraction-grating.md]] | 利用周期结构让不同波长按角度分离 |

### 光谱与色彩概念

| 概念 | 文件 | 核心定义 |
|------|------|---------|
| **光谱分辨率** | [[spectral-resolution|spectral-resolution.md]] | 能区分两条相邻谱线的最小波长间隔 |
| **色散** | [[dispersion|dispersion.md]] | 不同波长光折射/衍射角度不同的现象 |
| **色度图** | [[chromaticity-diagram|chromaticity-diagram.md]] | 用二维坐标表示颜色的图表 |
| **色温** | [[color-temperature|color-temperature.md]] | 黑体辐射光谱与光源最接近时的温度 |
| **荧光** | [[fluorescence|fluorescence.md]] | 物质吸收光后发射较长波长光 |
| **拉曼散射** | [[raman-scattering|raman-scattering.md]] | 非弹性散射，光子与分子交换能量 |
| **多光谱成像** | [[multispectral-imaging|multispectral-imaging.md]] | 使用少数离散波段获取图像 |
| **高光谱成像** | [[hyperspectral-imaging|hyperspectral-imaging.md]] | 连续窄波段成像，形成数据立方体 |
| **光谱分布函数** | [[spectral-power-distribution|spectral-power-distribution.md]] | 光源在各波长上的功率分布 |
| **阿贝数** | [[abbe-number|abbe-number.md]] | 衡量材料色散程度的无量纲数 |

## 与学习路径的关系

- 初学者先按 [[../90-maps/Learning Path|从零到深入学习路径]] 阅读主线章节，再回到本目录查术语。
- 光谱专项优先掌握：[[dispersion|色散]]、[[spectral-power-distribution|光谱分布函数]]、[[spectral-resolution|光谱分辨率]]、[[chromaticity-diagram|色度图]]、[[color-temperature|色温]]。
- 需要系统结构时，参考 [[../90-maps/Knowledge Architecture|知识库架构]]。

## 待补概念

以下概念在设备或公式笔记中已经被反复提到，但尚未拆成独立原子笔记。后续应按使用频率逐步补齐：

- 将已有中文 stub 中的内容补到稳定 slug 页：工作距离、视场、视角、放大倍率、数值孔径、瑞利判据。
- 为照明相关概念建立稳定 slug：照明方式、同轴照明、低角度照明、镜面反射、漫射。
- 为传感器与红外概念补充来源和边界：动态范围、NETD、发射率、微测辐射热计。
