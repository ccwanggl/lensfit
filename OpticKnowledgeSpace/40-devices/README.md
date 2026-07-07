---
id: map.devices
title: 设备与测量
type: map
status: maintained
---

# 设备与测量

存放设备能力、测量方法、误差来源和校准要求，避免将特定设备约束混入通用领域知识。

## 已收录设备

| 设备 | 文件 | 类型 | 关键参数 |
|------|------|------|---------|
| **C-mount镜头** | [[000-c-mount-lens|c-mount-lens.md]] | 工业镜头 | 法兰距17.526mm，像圈8-16mm |
| **远心镜头** | [[001-telecentric-lens|telecentric-lens.md]] | 工业镜头 | 消除透视畸变，WD固定 |
| **显微镜物镜** | [[002-microscope-objective|microscope-objective.md]] | 显微光学 | 倍率、NA、WD、像差等级 |
| **全局快门CMOS** | [[003-global-shutter-cmos|global-shutter-cmos.md]] | 传感器 | 无果冻效应，适合高速运动 |
| **卷帘快门CMOS** | [[004-rolling-shutter-cmos|rolling-shutter-cmos.md]] | 传感器 | 成本低，适合静态场景 |
| **红外热像仪探测器** | [[015-ir-thermal-detector|ir-thermal-detector.md]] | 探测器 | VOx/MCT，NETD、波段 |
| **LED环形光源** | [[006-led-ring-light|led-ring-light.md]] | 照明 | 环光，表面缺陷检测 |
| **同轴照明** | [[007-coaxial-illumination|coaxial-illumination.md]] | 照明 | 镜面物体，无阴影 |
| **背光板** | [[005-backlight|backlight.md]] | 照明 | 轮廓检测，均匀面光源 |
| **远心照明** | [[008-telecentric-illumination|telecentric-illumination.md]] | 照明 | 与双远心镜头配合，消除半影 |

### 光谱设备

| 设备 | 文件 | 类型 | 关键参数 |
|------|------|------|---------|
| **光谱仪** | [[011-spectrometer|spectrometer.md]] | 光谱设备 | 波长范围、分辨率、信噪比 |
| **高光谱相机** | [[012-hyperspectral-camera|hyperspectral-camera.md]] | 光谱相机 | 波段数、光谱/空间分辨率、帧率 |
| **衍射光栅** | [[010-diffraction-grating|diffraction-grating.md]] | 分光元件 | 刻线密度、闪耀角、效率曲线 |
| **窄带滤光片** | [[009-bandpass-filter|bandpass-filter.md]] | 滤光元件 | 中心波长、FWHM、透过率 |
| **积分球** | [[014-integrating-sphere|integrating-sphere.md]] | 测量设备 | 直径、涂层反射率、开口比 |

## 与学习路径的关系

- 基础选型先看 [[000-c-mount-lens|C-mount镜头]]、[[003-global-shutter-cmos|全局快门CMOS]]、[[004-rolling-shutter-cmos|卷帘快门CMOS]]。
- 工业测量重点看 [[001-telecentric-lens|远心镜头]]、[[008-telecentric-illumination|远心照明]]、[[005-backlight|背光板]]。
- 光谱专项重点看 [[011-spectrometer|光谱仪]]、[[012-hyperspectral-camera|高光谱相机]]、[[010-diffraction-grating|衍射光栅]]、[[009-bandpass-filter|窄带滤光片]]、[[014-integrating-sphere|积分球]]。

## 待补设备

- 线扫相机与推扫式高光谱平台
- InGaAs SWIR 相机
- 卤素线光源、SWIR LED 光源
- 荧光滤光片组和二向色镜
- 标准白板、暗场校正工具、波长校准灯
