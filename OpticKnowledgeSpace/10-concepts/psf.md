---
id: concept.psf
title: Point Spread Function (PSF)
type: concept
domains:
  - foundational
  - image-quality
status: reviewed
aliases:
  - PSF
  - point spread function
  - 点扩散函数
---

# Point Spread Function (PSF)

The Point Spread Function (PSF) describes the image of an ideal point source formed by an optical system. It is the spatial-domain counterpart of the Optical Transfer Function (OTF) and represents the blurring kernel of the system.

## Key properties

- For a diffraction-limited circular aperture the PSF is the Airy pattern.
- For a defocused or aberrated system the PSF broadens and becomes asymmetric.
- The PSF of cascaded linear systems is approximately the convolution of their individual PSFs.

## Relationship to MTF

\[
\text{OTF} = \mathcal{F}\{\text{PSF}\}, \quad \text{MTF} = |\text{OTF}|
\]

## Related concepts

- [[10-concepts/airy-disk|Airy disk]]
- [[10-concepts/mtf|Modulation Transfer Function (MTF)]]
- [[10-concepts/otf|Optical Transfer Function (OTF)]]

## See also

- [[10-concepts/点扩散函数|点扩散函数 (中文)]]

## 关联实验

- [[90-maps/Optics Lab#mtf-explorer|MTF/OTF 探索实验]] — 合成衍射极限 MTF、离焦模糊 MTF 与总 MTF，并观察对应的 PSF。
