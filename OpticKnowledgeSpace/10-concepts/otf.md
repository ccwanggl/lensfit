---
id: concept.otf
title: Optical Transfer Function (OTF)
type: concept
domains:
  - foundational
  - image-quality
status: reviewed
aliases:
  - OTF
  - optical transfer function
  - 光学传递函数
---

# Optical Transfer Function (OTF)

The Optical Transfer Function (OTF) is the Fourier transform of the Point Spread Function (PSF). It fully characterizes a linear, shift-invariant optical system in the frequency domain, including both contrast attenuation and phase shifts.

## Relationship to MTF and PTF

\[
\text{OTF}(f) = \text{MTF}(f) \cdot e^{i \cdot \text{PTF}(f)}
\]

- **MTF** (Modulation Transfer Function): magnitude of the OTF; describes contrast loss.
- **PTF** (Phase Transfer Function): phase of the OTF; describes lateral shifts of periodic patterns.

For an aberration-free, centered system the PTF is zero and OTF = MTF.

## Related concepts

- [[10-concepts/mtf|Modulation Transfer Function (MTF)]]
- [[10-concepts/psf|Point Spread Function (PSF)]]

## See also

- [[10-concepts/光学传递函数|光学传递函数 (中文)]]

## 关联实验

- [[90-maps/Optics Lab#MTF/OTF 探索实验|MTF/OTF 探索实验]] — 合成衍射极限 MTF、离焦模糊 MTF 与总 MTF，并观察对应的 PSF。
