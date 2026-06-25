---
id: concept.mtf
title: Modulation Transfer Function (MTF)
type: concept
domains:
  - foundational
  - image-quality
status: reviewed
aliases:
  - MTF
  - modulation transfer function
  - 调制传递函数
---

# Modulation Transfer Function (MTF)

The Modulation Transfer Function (MTF) measures how well an optical system preserves contrast as a function of spatial frequency. It is the magnitude of the Optical Transfer Function (OTF) and describes the system's ability to reproduce sinusoidal intensity patterns of increasing fineness.

## Definition

For a sinusoidal object with spatial frequency \(f\) and modulation \(M_0\), the image modulation \(M_i\) is reduced by the MTF:

\[
\text{MTF}(f) = \frac{M_i(f)}{M_0(f)}
\]

where modulation is \(M = (I_{\max} - I_{\min}) / (I_{\max} + I_{\min})\).

## Key values

- **MTF at zero frequency**: 1.0 (normalized).
- **MTF50**: spatial frequency where MTF drops to 50 %; a common image-sharpness metric.
- **MTF30 / MTF10**: alternative contrast thresholds used in some standards.
- **Diffraction-limited MTF**: the theoretical upper bound for a given aperture and wavelength.

## Related concepts

- [[10-concepts/otf|Optical Transfer Function (OTF)]]
- [[10-concepts/psf|Point Spread Function (PSF)]]
- [[10-concepts/airy-disk|Airy disk]]

## See also

- [[10-concepts/调制传递函数|调制传递函数 (中文)]]

## 关联实验

- [[90-maps/Optics Lab#mtf-explorer|MTF/OTF 探索实验]] — 合成衍射极限 MTF、离焦模糊 MTF 与总 MTF，并观察对应的 PSF。
