---
id: concept.diffraction-grating
title: Diffraction Grating
type: concept
domains:
  - foundational
  - spectroscopy
status: reviewed
aliases:
  - diffraction grating
  - 衍射光栅
---

# Diffraction Grating

A diffraction grating is an optical component with a periodic structure of closely spaced lines (grooves or slits) that splits incident light into multiple beams traveling in different directions. The angles of the diffracted orders are governed by the grating equation.

## Grating equation

For a grating with groove spacing \(d\), incident angle \(\theta_i\), and diffracted angle \(\theta_m\) for order \(m\):

$$
d($$in\theta_i + $$in\theta_m) = m\lambda
$$

where \(\lambda\) is the wavelength and \(m\) is an integer (the diffraction order). The equation assumes the angles are measured from the grating normal and lie in the plane perpendicular to the grooves.

## Key properties

- **Higher groove density** \(g = 1/d\) produces larger diffraction angles for the same order and wavelength.
- **Zero-order** (\(m = 0\)) is undeviated and does not depend on wavelength, so it cannot be used for dispersion.
- **Angular dispersion** \(d\theta/d\lambda = m / (d \cos\theta_m)\) increases with order and groove density.
- **Resolving power** is approximately \(R = mN\), where \(N\) is the total number of illuminated grooves.

## See also

- [[10-concepts/衍射光栅|衍射光栅 (中文)]]

## 教材参考

- [[../80-sources/hecht-optics-5e|Hecht, *Optics*, 5th ed.]]：适合核对光线模型、波动模型、干涉、衍射和偏振的基础定义。
- [[../80-sources/saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]]：适合核对探测器、光与物质相互作用、光子学器件和现代光学系统。
- [[../80-sources/Textbook Reference Matrix|教材页码索引矩阵]]：本页引用先保持章节级定位，精确页码待后续核验后回填。

## 关联实验

- [[90-maps/Optics Lab#光栅方程与光谱级次实验|光栅方程与光谱级次实验]] — 改变光栅刻线密度、波长和入射角，观察哪些衍射级次可以被接收到。
