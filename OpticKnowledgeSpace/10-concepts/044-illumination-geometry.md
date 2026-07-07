---
id: concept.illumination-geometry
title: Illumination Geometry
type: concept
domains:
  - machine-vision
  - inspection
status: reviewed
aliases:
  - illumination geometry
  - illumination types
  - 照明几何
  - 照明方式
---

# Illumination Geometry

Illumination geometry describes the spatial arrangement of light sources relative to the object and camera. The choice of geometry determines which surface features (diffuse, specular, scratches, edges, transparency) are emphasized or suppressed.

## Common machine-vision geometries

- **Bright-field**: light source near the camera optical axis. Diffuse surfaces appear bright; specular reflections may glare.
- **Dark-field**: light enters at a grazing angle to the surface. Smooth areas appear dark; scratches, dust, and raised features scatter light into the camera.
- **Coaxial**: light travels through the same optical path as the camera, often via a beamsplitter. Strong for specular surfaces and avoiding shadows.
- **Diffuse backlight**: uniform light behind the object. Best for silhouette, edge, and transparency measurements.
- **Low-angle**: light nearly parallel to the surface. Enhances small height variations and surface texture.

## Key trade-offs

- **Specular vs. diffuse**: specular surfaces need coaxial or structured lighting; diffuse surfaces work with bright-field.
- **Shadow suppression**: coaxial and diffuse dome lighting reduce shadows.
- **Contrast source**: dark-field and low-angle create contrast from surface topology rather than material reflectivity.

## Related concepts

- [[10-concepts/047-低角度照明|低角度照明]]
- [[10-concepts/046-同轴照明|同轴照明]]
- [[10-concepts/048-远心照明|远心照明]]
- [[10-concepts/052-漫射|漫射照明]]
- [[10-concepts/053-镜面反射|镜面反射]]

## See also

- [[10-concepts/045-照明方式|照明方式 (中文)]]
- [[50-learning/013-illumination-design|照明设计]]

## 教材参考

- [[../80-sources/005-smith-modern-optical-engineering-4e|Smith, *Modern Optical Engineering*, 4th ed.]]：适合核对镜头系统、孔径光阑、像差、像质评价和工程约束。
- [[../80-sources/002-hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/001-Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 关联实验

- [[90-maps/007-Optics Lab#照明方式几何实验|照明方式几何实验]] — 切换明场、暗场、同轴、漫射背光、低角度等照明方式，观察表面特征如何被凸显。
