---
id: map.formulas
title: 公式
type: map
status: maintained
---

# 公式

存放光学、验光和尺寸换算公式。公式笔记应包含变量定义、单位、适用条件、示例和来源。

## 使用约定

公式页必须先写清符号约定，再给计算形式。涉及物距、像距、焦距、孔径和波长时，默认使用同一长度单位；工程规格中的工作距离、机械后焦、传感器尺寸不能在未换算时直接代入。

## 已收录公式

| 公式 | 文件 | 核心表达式 | 用途 |
|------|------|----------|------|
| **薄透镜高斯公式** | [[000-thin-lens-gauss|thin-lens-gauss.md]] | $1/f = 1/u + 1/v$ | 物距、像距、焦距关系 |
| **横向放大倍率** | [[001-lateral-magnification|lateral-magnification.md]] | $\beta = v/u = s/FOV$ | 像与物的大小比 |
| **视角公式** | [[003-angle-of-view|angle-of-view.md]] | $AFOV = (360/\pi) \arctan(s/2f)$ | 计算视场角度 |
| **焦距反推公式** | [[002-focal-length-from-wd|focal-length-from-wd.md]] | $f = WD \cdot s / (FOV + s)$ | 已知WD/FOV/s求焦距 |
| **艾里斑直径** | [[008-airy-disk-diameter|airy-disk-diameter.md]] | $d = 2.44 \lambda F\#$ | 估算衍射极限 |
| **奈奎斯特频率** | [[006-nyquist-frequency|nyquist-frequency.md]] | $f_N = 1000/(2p)$ | 传感器分辨极限 |
| **像素精度** | [[005-pixel-precision|pixel-precision.md]] | $Precision = p/(1000 \cdot \beta)$ | 每个像素对应的物理尺寸 |
| **像圈覆盖比** | [[004-coverage-ratio|coverage-ratio.md]] | $Coverage = (IC/D_{sensor})^2$ | 检查像圈是否覆盖传感器 |
| **过采样率** | [[007-oversampling-ratio|oversampling-ratio.md]] | $OS = f_{lens}/f_{Nyquist}$ | 镜头与传感器分辨率匹配 |
| **瑞利判据** | [[009-rayleigh-criterion|rayleigh-criterion.md]] | $d = 0.61 \lambda / NA$ | 显微镜分辨率极限 |

### 光谱与色彩公式

| 公式 | 文件 | 核心表达式 | 用途 |
|------|------|----------|------|
| **光栅方程** | [[012-grating-equation|grating-equation.md]] | $d(\sin\theta_i + \sin\theta_m) = m\lambda$ | 衍射光栅分光 |
| **光栅光谱分辨率** | [[013-grating-resolving-power|grating-resolving-power.md]] | $R = mN$ | 光栅能分辨的最小波长差 |
| **棱镜色散率** | [[014-prism-dispersion|prism-dispersion.md]] | $R = t \cdot |dn/d\lambda|$ | 棱镜分光能力 |
| **Delta E色差** | [[016-delta-e|delta-e.md]] | $\Delta E = \sqrt{(\Delta L)^2 + (\Delta a)^2 + (\Delta b)^2}$ | 颜色差异量化 |
| **普朗克黑体辐射** | [[015-planck-blackbody|planck-blackbody.md]] | $\lambda_{max} = b/T$ | 色温与峰值波长关系 |
| **双缝条纹间距** | [[011-double-slit-fringe-spacing|double-slit-fringe-spacing.md]] | $\Delta y = \lambda L / d$ | 双缝干涉条纹间距估算 |

## 与学习路径的关系

- 初学者先学 [[./000-thin-lens-gauss|薄透镜高斯公式]]、[[./002-focal-length-from-wd|焦距反推公式]]、[[./004-coverage-ratio|像圈覆盖比]]。
- 进入像质后再学 [[./008-airy-disk-diameter|艾里斑直径]]、[[./009-rayleigh-criterion|瑞利判据]]、[[./006-nyquist-frequency|奈奎斯特频率]]。
- 光谱专项集中学习 [[./012-grating-equation|光栅方程]]、[[./013-grating-resolving-power|光栅光谱分辨率]]、[[./014-prism-dispersion|棱镜色散率]]、[[./015-planck-blackbody|普朗克黑体辐射公式]]、[[./016-delta-e|Delta E 色差]]。

## 待补公式

- CIE XYZ 三刺激值积分
- 相关色温 CCT 的近似计算或查表流程
- 光谱采样间隔与光谱分辨率的关系
- 推扫式高光谱相机的线速、曝光、空间分辨率换算
- 红外热成像中目标辐射、发射率和背景反射的简化模型
