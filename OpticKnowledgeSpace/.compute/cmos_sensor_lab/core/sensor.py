# CMOS Sensor 光电转换模型
# 对应笔记章节：1.2 光电转换、1.3 像点微观结构、3.6 灵敏度

import numpy as np


def photon_to_electron(photons, qe=0.5):
    """
    光子到电子的转换。

    根据笔记公式，传感器产生的电子数 S 与入射光子数 N 的关系为：
    S = QE · N
    其中 QE 是量子效率（Quantum Efficiency），表示每个光子能产生多少电子。

    Parameters
    ----------
    photons : float or np.ndarray
        入射光子数（可以是单值或数组）。
    qe : float, optional
        量子效率，范围 0.0~1.0，默认 0.5。

    Returns
    -------
    float or np.ndarray
        转换后的电子数。
    """
    photons = np.maximum(photons, 0)  # 光子数不能为负
    return photons * qe


def electron_to_dn(electrons, gain=1.0, adc_bits=12, fwc=10000):
    """
    电子到数字值（DN）的转换，包含增益放大和 ADC 量化。

    转换流程：
    1. 势阱饱和截断：电子数不能超过 FWC（Full Well Capacity）
    2. 增益放大：DN_raw = g · electrons
    3. ADC 量化：DN = round(DN_raw)，限制在 [0, 2^adc_bits - 1]

    Parameters
    ----------
    electrons : float or np.ndarray
        光生电子数。
    gain : float, optional
        增益系数（g），默认 1.0。
    adc_bits : int, optional
        ADC 位数，默认 12。
    fwc : int, optional
        势阱容量（Full Well Capacity），单位 e-，默认 10000。

    Returns
    -------
    int or np.ndarray
        量化后的 DN 值。
    """
    # 1. 饱和截断：电子数不能超过势阱容量
    electrons = np.clip(electrons, 0, fwc)
    # 2. 增益放大
    dn_raw = electrons * gain
    # 3. ADC 量化：限制在 [0, 2^adc_bits - 1]
    max_dn = 2**adc_bits - 1
    dn = np.clip(dn_raw, 0, max_dn)
    # 4. 离散化（整数量化）
    dn = np.round(dn).astype(int)
    return dn


def photon_to_dn_full(photons, qe=0.5, gain=1.0, adc_bits=12, fwc=10000, exposure_time=1.0):
    """
    完整光电转换链路：光子 → 电子 → DN。

    考虑曝光时间的影响：
    在曝光时间 t 内收集的光子数 = N · t，
    因此电子数 = QE · N · t。

    Parameters
    ----------
    photons : float or np.ndarray
        单位时间入射光子数（photons/s）。
    qe : float, optional
        量子效率，默认 0.5。
    gain : float, optional
        增益系数，默认 1.0。
    adc_bits : int, optional
        ADC 位数，默认 12。
    fwc : int, optional
        势阱容量，默认 10000 e-。
    exposure_time : float, optional
        曝光时间（s），默认 1.0。

    Returns
    -------
    int or np.ndarray
        量化后的 DN 值。
    """
    total_photons = photons * exposure_time
    electrons = photon_to_electron(total_photons, qe)
    dn = electron_to_dn(electrons, gain, adc_bits, fwc)
    return dn


def generate_response_curve(photons_range, qe=0.5, gain=1.0, adc_bits=12, fwc=10000):
    """
    生成传感器的输入-输出响应曲线。

    响应曲线分为三个区域：
    - 线性区：DN 与光子数成正比
    - 饱和区：光子数超过 FWC，DN 不再增加
    - 截止区：光子数极低，可能被读出噪声淹没

    Parameters
    ----------
    photons_range : np.ndarray
        入射光子数范围（数组）。
    qe, gain, adc_bits, fwc : 同 photon_to_dn_full。

    Returns
    -------
    np.ndarray
        对应的 DN 值数组。
    """
    return photon_to_dn_full(photons_range, qe, gain, adc_bits, fwc)


def get_saturation_photons(qe=0.5, fwc=10000):
    """
    计算使势阱饱和所需的光子数。

    饱和条件：QE · N_sat = FWC
    → N_sat = FWC / QE

    Parameters
    ----------
    qe : float, optional
        量子效率，默认 0.5。
    fwc : int, optional
        势阱容量，默认 10000 e-。

    Returns
    -------
    float
        饱和光子数。
    """
    if qe <= 0:
        return np.inf
    return fwc / qe


def get_quantization_step(gain=1.0):
    """
    计算一个 DN 对应的电子数。

    关系：DN = g · electrons
    → 1 DN = 1/g electrons

    Parameters
    ----------
    gain : float, optional
        增益系数，默认 1.0。

    Returns
    -------
    float
        1 DN 对应的电子数。
    """
    if gain <= 0:
        return np.inf
    return 1.0 / gain


def generate_photon_image(size=(256, 256), center_value=1000, gradient=True):
    """
    生成一个模拟的光子数图像，用于测试光电转换。

    Parameters
    ----------
    size : tuple, optional
        图像尺寸 (h, w)，默认 (256, 256)。
    center_value : float, optional
        中心区域的光子数，默认 1000。
    gradient : bool, optional
        是否使用渐变，默认 True。

    Returns
    -------
    np.ndarray
        二维光子数图像。
    """
    h, w = size
    y, x = np.ogrid[:h, :w]
    cy, cx = h / 2, w / 2

    if gradient:
        # 径向渐变：中心亮，边缘暗
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        max_dist = np.sqrt(cx**2 + cy**2)
        image = center_value * (1 - 0.8 * dist / max_dist)
    else:
        # 均匀图像
        image = np.full(size, center_value, dtype=float)

    return np.clip(image, 0, None)
