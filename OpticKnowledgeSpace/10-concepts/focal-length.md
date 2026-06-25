---

id: concept.focal-length
title: 焦距
type: concept
domains: [general]
status: reviewed
source_ids: []
reviewed_at:
owners: []
aliases: [focal length, 焦距 f, 焦长]---

# 焦距

## 定义
焦距（Focal Length）是平行光线经过透镜后汇聚到焦点，焦点到透镜中心（主点）的距离。它是透镜的固有光学属性，单位为毫米（mm）。

对薄透镜，焦距由透镜材料的折射率和曲率半径决定（磨镜者公式）。

## 直观理解
小时候用放大镜把阳光聚焦在纸上烧出一个小黑点——那个小黑点就是焦点。放大镜到纸面的距离，就是放大镜的焦距。焦距越短，汇聚能力越强，视野越宽；焦距越长，看得越远，视野越窄。

## 关键参数/公式

**薄透镜高斯公式**：

$$
\frac{1}{f} = \frac{1}{u} + \frac{1}{v}
$$

- $f$ —— 焦距（mm）
- $u$ —— 物距（mm）
- $v$ —— 像距（mm）

**放大倍率**：

$$
\beta = \frac{v}{u} = \frac{s}{FOV}
$$

- $s$ —— 传感器宽度
- $FOV$ —— 视场宽度

**视角公式**：

$$
AFOV = \frac{360}{\pi} \cdot \arctan\left(\frac{s}{2f}\right) \quad [°]
$$

## 适用场景
- 镜头选型的首要参数：根据工作距离和视场计算所需焦距
- 视角设计：广角（短焦距）vs 长焦（长焦距）vs 标准（约等于传感器对角线）
- 工业视觉：根据 $f = \frac{WD \cdot s}{FOV + s}$ 反推焦距
- 显微镜：焦距与物镜放大倍率直接相关

## 关键关系
- 相关概念：[[../10-concepts/f-number|F值]]（F# = f/D，焦距是分子）、[[../10-concepts/depth-of-field|景深]]（焦距越长景深越浅）
- 相关公式：薄透镜公式、视角公式
- 相关教程：[[../50-learning/02-geometric-optics|第2章 几何光学]]（薄透镜公式、放大倍率、视角）、[[../50-learning/03-lens-parameters|第3章 镜头参数]]（镜头参数速查表）

## 常见误区
- **错误**：认为焦距直接决定「放大倍数」。
- **事实**：焦距本身不决定放大倍率。**放大倍率 = 像距 / 物距**。200mm 镜头在远距离拍摄时，像可能比 50mm 镜头还小。只有在**相同拍摄距离**下比较，焦距长的才会放大更多。
- **错误**：把「焦距」和「对焦距离」混为一谈。
- **事实**：焦距是镜头的固定光学属性（变焦镜头除外）；对焦距离是镜头能清晰成像的物距范围，两者完全不同。
- **错误**：说「50mm 镜头的视角是 40°」。
- **事实**：视角同时取决于焦距 **和** 传感器尺寸。50mm 配全画幅 = 40°；配 APS-C = 约 27°；配 M4/3 = 约 20°。

## 可视化辅助

![[attachments/visuals/thin-lens-geometry.svg]]
*图：Thin Lens Geometry*

![[attachments/visuals/angle-of-view.svg]]
*图：Angle Of View*

## 来源
- [[../50-learning/02-geometric-optics|第2章 几何光学]] §2.2 薄透镜成像模型
- [[../50-learning/03-lens-parameters|第3章 镜头参数]] §3.1 焦距

## 关联实验

- [[90-maps/Optics Lab#thin-lens|薄透镜成像实验]] — 改变焦距和物距，观察像距、放大倍率和光路图的变化。
