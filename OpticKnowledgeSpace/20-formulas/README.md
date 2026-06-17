---
id: map.formulas
title: 公式
type: map
status: maintained
---

# 公式

存放光学、验光和尺寸换算公式。公式笔记应包含变量定义、单位、适用条件、示例和来源。

## 已收录公式

| 公式 | 文件 | 核心表达式 | 用途 |
|------|------|----------|------|
| **薄透镜高斯公式** | [[thin-lens-gauss|thin-lens-gauss.md]] | $1/f = 1/u + 1/v$ | 物距、像距、焦距关系 |
| **横向放大倍率** | [[lateral-magnification|lateral-magnification.md]] | $\beta = v/u = s/FOV$ | 像与物的大小比 |
| **视角公式** | [[angle-of-view|angle-of-view.md]] | $AFOV = (360/\pi) \arctan(s/2f)$ | 计算视场角度 |
| **焦距反推公式** | [[focal-length-from-wd|focal-length-from-wd.md]] | $f = WD \cdot s / (FOV + s)$ | 已知WD/FOV/s求焦距 |
| **艾里斑直径** | [[airy-disk-diameter|airy-disk-diameter.md]] | $d = 2.44 \lambda F\#$ | 估算衍射极限 |
| **奈奎斯特频率** | [[nyquist-frequency|nyquist-frequency.md]] | $f_N = 1000/(2p)$ | 传感器分辨极限 |
| **像素精度** | [[pixel-precision|pixel-precision.md]] | $Precision = p/(1000 \cdot \beta)$ | 每个像素对应的物理尺寸 |
| **像圈覆盖比** | [[coverage-ratio|coverage-ratio.md]] | $Coverage = (IC/D_{sensor})^2$ | 检查像圈是否覆盖传感器 |
| **过采样率** | [[oversampling-ratio|oversampling-ratio.md]] | $OS = f_{lens}/f_{Nyquist}$ | 镜头与传感器分辨率匹配 |
| **瑞利判据** | [[rayleigh-criterion|rayleigh-criterion.md]] | $d = 0.61 \lambda / NA$ | 显微镜分辨率极限 |

### 光谱与色彩公式

| 公式 | 文件 | 核心表达式 | 用途 |
|------|------|----------|------|
| **光栅方程** | [[grating-equation|grating-equation.md]] | $d(\sin\theta_i + \sin\theta_m) = m\lambda$ | 衍射光栅分光 |
| **光栅光谱分辨率** | [[grating-resolving-power|grating-resolving-power.md]] | $R = mN$ | 光栅能分辨的最小波长差 |
| **棱镜色散率** | [[prism-dispersion|prism-dispersion.md]] | $R = t \cdot |dn/d\lambda|$ | 棱镜分光能力 |
| **Delta E色差** | [[delta-e|delta-e.md]] | $\Delta E = \sqrt{(\Delta L)^2 + (\Delta a)^2 + (\Delta b)^2}$ | 颜色差异量化 |
| **普朗克黑体辐射** | [[planck-blackbody|planck-blackbody.md]] | $\lambda_{max} = b/T$ | 色温与峰值波长关系 |

## 与学习路径的关系

- 初学者先学 [[../20-formulas/thin-lens-gauss|薄透镜高斯公式]]、[[../20-formulas/focal-length-from-wd|焦距反推公式]]、[[../20-formulas/coverage-ratio|像圈覆盖比]]。
- 进入像质后再学 [[../20-formulas/airy-disk-diameter|艾里斑直径]]、[[../20-formulas/rayleigh-criterion|瑞利判据]]、[[../20-formulas/nyquist-frequency|奈奎斯特频率]]。
- 光谱专项集中学习 [[../20-formulas/grating-equation|光栅方程]]、[[../20-formulas/grating-resolving-power|光栅光谱分辨率]]、[[../20-formulas/prism-dispersion|棱镜色散率]]、[[../20-formulas/planck-blackbody|普朗克黑体辐射公式]]、[[../20-formulas/delta-e|Delta E 色差]]。

## 待补公式

- CIE XYZ 三刺激值积分
- 相关色温 CCT 的近似计算或查表流程
- 光谱采样间隔与光谱分辨率的关系
- 推扫式高光谱相机的线速、曝光、空间分辨率换算
- 红外热成像中目标辐射、发射率和背景反射的简化模型
