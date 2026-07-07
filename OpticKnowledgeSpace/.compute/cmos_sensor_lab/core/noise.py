# CMOS Sensor 噪声模型
# 对应笔记章节：3.3 噪声、3.4 信噪比

import numpy as np


def shot_noise(electrons):
    """
    散粒噪声（光子统计噪声）。

    光信号的统计涨落符合泊松分布，其标准差为：
    σ_S = √S
    其中 S 是电子数。

    Parameters
    ----------
    electrons : float or np.ndarray
        光生电子数。

    Returns
    -------
    float or np.ndarray
        散粒噪声的标准差（单位：e-）。
    """
    return np.sqrt(np.maximum(electrons, 0))


def dark_current_noise(dark_current_electrons):
    """
    暗电流噪声。

    暗电流本身也符合泊松统计，其噪声为：
    σ_D = √D
    其中 D 是暗电流电子数。

    Parameters
    ----------
    dark_current_electrons : float or np.ndarray
        暗电流产生的电子数。

    Returns
    -------
    float or np.ndarray
        暗电流噪声的标准差（单位：e-）。
    """
    return np.sqrt(np.maximum(dark_current_electrons, 0))


def read_noise(sigma_r):
    """
    读出噪声。

    读出电路引入的噪声，通常近似为高斯分布：
    σ_R = 固定值（由电路设计决定）

    Parameters
    ----------
    sigma_r : float
        读出噪声的标准差（单位：e-）。

    Returns
    -------
    float
        读出噪声值。
    """
    return sigma_r


def ktc_noise(temperature_c=25, capacitance_f=1e-15):
    """
    kTC 噪声（复位噪声）。

    由电子热运动引起的噪声，经 PN 结电容滤波后：
    σ_kTC = √(kT / C)
    其中 k = 1.38×10⁻²³ J/K，T 为绝对温度，C 为结电容。

    Parameters
    ----------
    temperature_c : float, optional
        温度（°C），默认 25。
    capacitance_f : float, optional
        结电容（F），默认 1e-15。

    Returns
    -------
    float
        kTC 噪声的标准差（单位：e-）。
    """
    k = 1.38e-23  # 玻尔兹曼常数，单位 J/K
    t = temperature_c + 273.15  # 转换为开尔文
    if capacitance_f <= 0:
        return np.inf
    return np.sqrt(k * t / capacitance_f)


def total_noise(electrons, dark_current_electrons=0, sigma_r=2.0):
    """
    总有效噪声。

    各噪声源相互独立，按平方和叠加：
    σ_eff = √(σ_S² + σ_D² + σ_R²)

    Parameters
    ----------
    electrons : float or np.ndarray
        光生电子数。
    dark_current_electrons : float, optional
        暗电流电子数，默认 0。
    sigma_r : float, optional
        读出噪声标准差，默认 2.0 e-。

    Returns
    -------
    float or np.ndarray
        总噪声的标准差（单位：e-）。
    """
    s = shot_noise(electrons)
    d = dark_current_noise(dark_current_electrons)
    r = read_noise(sigma_r)
    return np.sqrt(s**2 + d**2 + r**2)


def snr(signal_electrons, total_noise_electrons):
    """
    信噪比（线性形式）。

    SNR = S / σ_eff

    Parameters
    ----------
    signal_electrons : float or np.ndarray
        信号电子数。
    total_noise_electrons : float or np.ndarray
        总噪声电子数。

    Returns
    -------
    float or np.ndarray
        线性 SNR。
    """
    return signal_electrons / np.maximum(total_noise_electrons, 1e-10)


def snr_db(signal_electrons, total_noise_electrons):
    """
    信噪比（dB 形式）。

    SNR_dB = 20 · log₁₀(S / σ_eff)

    Parameters
    ----------
    signal_electrons : float or np.ndarray
        信号电子数。
    total_noise_electrons : float or np.ndarray
        总噪声电子数。

    Returns
    -------
    float or np.ndarray
        SNR（dB）。
    """
    ratio = snr(signal_electrons, total_noise_electrons)
    return 20 * np.log10(np.maximum(ratio, 1e-10))


def generate_snr_curve(photon_range, qe=0.5, dark_current_electrons=0, sigma_r=2.0):
    """
    生成 SNR 随光子数变化的曲线数据。

    Parameters
    ----------
    photon_range : np.ndarray
        光子数范围（数组）。
    qe : float, optional
        量子效率，默认 0.5。
    dark_current_electrons : float, optional
        暗电流电子数，默认 0。
    sigma_r : float, optional
        读出噪声，默认 2.0 e-。

    Returns
    -------
    np.ndarray
        对应光子数下的 SNR（dB）数组。
    """
    electrons = photon_range * qe
    noise = total_noise(electrons, dark_current_electrons, sigma_r)
    return snr_db(electrons, noise)


def add_noise_to_image(image, qe=0.5, dark_current_electrons=0, sigma_r=2.0, fwc=10000):
    """
    给图像添加噪声，模拟真实 sensor 拍摄。

    噪声添加流程：
    1. 光生电子：泊松分布（信号电子数）
    2. 暗电流电子：泊松分布（暗电流电子数）
    3. 读出噪声：高斯分布（σ_R）
    4. 总电子 = 光生电子 + 暗电流电子 + 读出噪声
    5. 饱和截断到 [0, FWC]

    Parameters
    ----------
    image : np.ndarray
        输入光子数图像。
    qe : float, optional
        量子效率，默认 0.5。
    dark_current_electrons : float, optional
        暗电流电子数，默认 0。
    sigma_r : float, optional
        读出噪声，默认 2.0 e-。
    fwc : int, optional
        势阱容量，默认 10000 e-。

    Returns
    -------
    np.ndarray
        含噪声的电子数图像。
    """
    # 1. 光生电子（泊松分布）
    electrons = image * qe
    # np.random.poisson 需要非负整数，先取整
    shot = np.random.poisson(np.maximum(electrons, 0).astype(int)).astype(float)
    # 2. 暗电流电子（泊松分布）
    dark = np.random.poisson(max(int(dark_current_electrons), 0)).astype(float)
    if image.ndim == 2:
        dark = np.full_like(image, dark, dtype=float)
    # 3. 读出噪声（高斯分布）
    read = np.random.normal(0, sigma_r, image.shape)
    # 4. 总电子
    total_e = shot + dark + read
    # 5. 饱和截断
    total_e = np.clip(total_e, 0, fwc)
    return total_e


def generate_noise_decomposition(signal_electrons, dark_current_electrons=0, sigma_r=2.0):
    """
    生成噪声分解数据，用于饼图展示。

    Parameters
    ----------
    signal_electrons : float
        信号电子数。
    dark_current_electrons : float, optional
        暗电流电子数，默认 0。
    sigma_r : float, optional
        读出噪声，默认 2.0。

    Returns
    -------
    dict
        各噪声分量的方差（σ²）。
    """
    s = shot_noise(signal_electrons) ** 2
    d = dark_current_noise(dark_current_electrons) ** 2
    r = read_noise(sigma_r) ** 2
    return {
        '散粒噪声': s,
        '暗电流噪声': d,
        '读出噪声': r
    }
