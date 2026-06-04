"""Utility functions for optical calculations."""

from __future__ import annotations

import math


def sensor_coverage_check(sensor_w: float, sensor_h: float, image_circle: float) -> dict:
    """检查传感器是否被镜头像圆完全覆盖.

    Returns:
        {
            'fully_covered': bool,
            'coverage_ratio': float,
            'vignetting': bool,
            'vignetting_corners': bool,
            'max_safe_sensor_diag': float,
            'margin': float
        }
    """
    sensor_diag = (sensor_w**2 + sensor_h**2) ** 0.5
    fully_covered = sensor_diag <= image_circle
    coverage_ratio = min(1.0, (image_circle / sensor_diag) ** 2) if sensor_diag > 0 else 0

    corner_distance_sq = (sensor_w / 2) ** 2 + (sensor_h / 2) ** 2
    vignetting_corners = corner_distance_sq > (image_circle / 2) ** 2

    return {
        'fully_covered': fully_covered,
        'coverage_ratio': coverage_ratio,
        'vignetting': not fully_covered,
        'vignetting_corners': vignetting_corners,
        'max_safe_sensor_diag': image_circle,
        'margin': (image_circle - sensor_diag) / image_circle if image_circle > 0 else -1,
    }


def nyquist_match(pixel_size_um: float, lens_mtf50_lpmm: float | None = None, na: float | None = None, wavelength_um: float = 0.55) -> dict:
    """奈奎斯特采样匹配分析.

    Returns:
        {
            'sensor_nyquist_lpmm': float,
            'optical_limit_lpmm': float,
            'matched': bool,
            'oversampling_ratio': float,
            'recommendation': str
        }
    """
    sensor_nyquist = 1000 / (2 * pixel_size_um)

    if na is not None:
        optical_limit = na / (0.61 * wavelength_um)
        desc = f"衍射极限 (NA={na})"
    elif lens_mtf50_lpmm is not None:
        optical_limit = lens_mtf50_lpmm
        desc = f"MTF50={lens_mtf50_lpmm} lp/mm"
    else:
        raise ValueError("必须提供NA或lens_mtf50_lpmm之一")

    oversampling = optical_limit / sensor_nyquist if sensor_nyquist > 0 else 0
    matched = 0.5 <= oversampling <= 1.2

    if oversampling > 1.2:
        rec = "镜头分辨率高于传感器，建议选用更小像元或更低倍率"
    elif oversampling < 0.5:
        rec = "传感器过采样，镜头光学分辨率不足，建议选用更高NA/MTF镜头"
    else:
        rec = "镜头与传感器匹配良好"

    return {
        'sensor_nyquist_lpmm': round(sensor_nyquist, 1),
        'optical_limit_lpmm': round(optical_limit, 1),
        'optical_limit_description': desc,
        'matched': matched,
        'oversampling_ratio': round(oversampling, 2),
        'recommendation': rec,
    }


def is_mount_compatible(lens_mount: str, det_mount: str) -> tuple[bool, str | None]:
    """检查接口兼容性.

    Returns:
        (is_compatible, adapter_needed)
    """
    if lens_mount == det_mount:
        return True, None

    # CS-mount 镜头 + C-mount 相机: 直接兼容（加5mm垫片）
    if lens_mount == "CS-mount" and det_mount == "C-mount":
        return True, "CS→C 5mm垫片"

    # C-mount 镜头 + CS-mount 相机: 不兼容（法兰距不够）
    if lens_mount == "C-mount" and det_mount == "CS-mount":
        return False, None

    # Microscope objectives (RMS, M25, M26, M27) + C-mount camera: compatible via tube lens
    microscope_objective_mounts = {"RMS", "M25", "M26", "M27"}
    if lens_mount in microscope_objective_mounts and det_mount == "C-mount":
        return True, "显微镜管镜适配"
    if lens_mount in microscope_objective_mounts and det_mount == "CS-mount":
        return True, "显微镜管镜适配"

    # F-mount 与其他: 需要转接环
    known_adapters = {
        ("C-mount", "F-mount"): "C→F 转接环",
        ("F-mount", "C-mount"): "F→C 转接环",
        ("M42", "C-mount"): "M42→C 转接环",
    }

    adapter = known_adapters.get((lens_mount, det_mount))
    return adapter is not None, adapter
