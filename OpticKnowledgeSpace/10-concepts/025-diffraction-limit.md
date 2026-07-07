---
id: concept.diffraction-limit
title: 衍射极限
type: concept
status: reviewed
domains:
  - foundational
aliases:
  - Diffraction Limit
  - diffraction limit
---

# 衍射极限

衍射极限是由光的波动性质决定的分辨率上限。即使镜头没有像差、没有失焦，点光源经过有限孔径后也会形成有限大小的点扩散函数，圆孔成像中最典型的形态是 [[10-concepts/027-airy-disk|艾里斑]]。

这个概念用于判断光学系统的物理上限：当像差、采样、运动和照明问题都被压低后，细节还能不能继续提高，主要看波长和有效孔径。

## 基本关系

圆孔第一暗环的角半径近似为：

$$
\theta \approx 1.22 \frac{\lambda}{D}
$$

其中 $\lambda$ 是波长，$D$ 是有效孔径直径。孔径越小或波长越长，衍射斑越大，系统能分开的最小角距离也越大。

用 F 值表达时，像面上的艾里斑直径常写成：

$$
d \approx 2.44 \lambda F\#
$$

这个关系把衍射和镜头光圈直接连起来：收小光圈会提高景深，但也会增大衍射斑。

## 需要区分的限制

- **衍射限制**来自波动传播，是理想系统也绕不开的边界。
- **像差限制**来自镜头设计、加工或装调，通常会让实际表现低于衍射极限。
- **采样限制**来自传感器像元大小和采样频率，常用 [[10-concepts/038-nyquist-frequency|奈奎斯特频率]] 判断。
- **系统限制**还包括运动模糊、照明对比度、噪声和算法处理。

## 工程意义

- 显微镜和长焦小孔径系统经常先碰到衍射限制。
- 工业视觉选型中，不能只靠减小像元追求更高精度，还要检查镜头 F 值和工作波长对应的衍射斑。
- 在摄影中，F8 到 F11 常被视作很多镜头的清晰范围之一，继续缩小光圈可能增加景深但降低细节。

## 参见

- [[10-concepts/026-衍射极限|衍射极限中文镜像]]
- [[10-concepts/027-airy-disk|艾里斑]]
- [[20-formulas/009-rayleigh-criterion|瑞利判据]]
- [[20-formulas/008-airy-disk-diameter|艾里斑直径]]

## 教材参考

- [[../80-sources/002-hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/004-goodman-introduction-fourier-optics-4e|Goodman, *Introduction to Fourier Optics*, 4th ed.]]：适合核对傅里叶光学、空间频率、PSF/OTF/MTF、采样和衍射成像。
- [[../80-sources/001-Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 关联实验

- [[90-maps/007-Optics Lab#双缝干涉实验|双缝干涉实验]] — 改变缝宽、缝间距和波长，观察双缝干涉条纹及其被单缝包络调制的现象。
- [[90-maps/007-Optics Lab#单缝衍射实验|单缝衍射实验]] — 改变缝宽和波长，观察夫琅禾费单缝衍射的强度分布和第一极小位置。
