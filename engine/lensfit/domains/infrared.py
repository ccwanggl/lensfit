"""Infrared imaging domain module."""

from __future__ import annotations

import math
from typing import Any

from lensfit.domains.base import (
    Constraint,
    DeviceCombo,
    DomainModule,
    ParameterDef,
    ScoringDimension,
)


class InfraredModule(DomainModule):
    """红外成像领域模块 — 红外镜头、探测器匹配."""

    @property
    def domain_id(self) -> str:
        return "infrared"

    @property
    def domain_name(self) -> str:
        return "红外成像"

    def get_parameters(self) -> list[ParameterDef]:
        return [
            ParameterDef(
                name="band",
                label="工作波段",
                type="enum",
                options=[
                    ("swir", "短波红外 (SWIR 0.9-2.5μm)"),
                    ("mwir", "中波红外 (MWIR 3-5μm)"),
                    ("lwir", "长波红外 (LWIR 8-14μm)"),
                    ("any", "任意波段"),
                ],
                default="lwir",
                required=True,
            ),
            ParameterDef(
                name="wavelength_um",
                label="目标波长",
                type="number",
                unit="μm",
                default=10.0,
                min_value=0.5,
                max_value=20.0,
                required=True,
            ),
            ParameterDef(
                name="fov_deg",
                label="目标视场角",
                type="number",
                unit="°",
                default=24.0,
                min_value=1.0,
                max_value=120.0,
                required=True,
            ),
            ParameterDef(
                name="working_distance_m",
                label="工作距离",
                type="number",
                unit="m",
                default=10.0,
                min_value=0.1,
                max_value=5000.0,
                required=True,
            ),
            ParameterDef(
                name="target_resolution_m",
                label="目标空间分辨率",
                type="number",
                unit="m",
                default=0.5,
                min_value=0.001,
                max_value=100.0,
                required=False,
            ),
            ParameterDef(
                name="sensor_format",
                label="传感器尺寸",
                type="enum",
                options=[
                    ("1/4", '1/4"'),
                    ("1/3", '1/3"'),
                    ("1/2", '1/2"'),
                    ("2/3", '2/3"'),
                    ("1", '1"'),
                    ("custom", "自定义"),
                ],
                default="1/2",
                required=True,
            ),
            ParameterDef(
                name="pixel_size_um",
                label="像元尺寸",
                type="number",
                unit="μm",
                default=12.0,
                min_value=1.0,
                max_value=50.0,
                required=True,
            ),
            ParameterDef(
                name="budget_usd",
                label="预算上限",
                type="number",
                unit="USD",
                default=5000.0,
                min_value=100.0,
                max_value=50000.0,
                required=False,
            ),
        ]

    def get_hard_constraints(self) -> list[Constraint]:
        return [
            Constraint(
                name="wavelength_coverage",
                check=self._check_wavelength_coverage,
                description="镜头波段覆盖目标波长",
            ),
            Constraint(
                name="sensor_coverage",
                check=self._check_sensor_coverage,
                description="镜头像面覆盖探测器传感器",
            ),
            Constraint(
                name="mount_compatibility",
                check=self._check_mount_compatibility,
                description="镜头与探测器接口兼容",
            ),
            Constraint(
                name="budget",
                check=self._check_budget,
                description="总价不超过预算",
            ),
        ]

    def get_scoring_dimensions(self) -> list[ScoringDimension]:
        return [
            ScoringDimension(
                name="fov_match",
                label="视场匹配度",
                weight=3.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="spatial_resolution",
                label="空间分辨率匹配度",
                weight=2.5,
                is_benefit=True,
            ),
            ScoringDimension(
                name="band_match",
                label="波段匹配度",
                weight=2.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="ifov",
                label="瞬时视场角(IFOV)",
                weight=1.5,
                is_benefit=True,
            ),
            ScoringDimension(
                name="cost_efficiency",
                label="成本效益",
                weight=1.0,
                is_benefit=True,
            ),
        ]

    def calculate_derived(self, combo: DeviceCombo) -> dict[str, Any]:
        """计算红外成像派生参数."""
        lens = combo.lens
        det = combo.detector
        reqs = combo.requirements

        if not reqs or not lens or not det:
            return {}

        params = reqs.params
        target_fov_deg = params.get("fov_deg", 24.0)
        working_distance_m = params.get("working_distance_m", 10.0)
        target_res_m = params.get("target_resolution_m")

        # 镜头参数
        focal = getattr(lens, "focal_length_mm", None) or 25.0
        focal_max = getattr(lens, "focal_length_max", None)
        fn = getattr(lens, "max_aperture", None) or 1.0
        ic = getattr(lens, "image_circle_mm", None) or 21.0
        wl_min = getattr(lens, "wavelength_min_nm", None) or 8000
        wl_max = getattr(lens, "wavelength_max_nm", None) or 14000

        # 探测器参数
        pixel_um = getattr(det, "pixel_size_um", None) or 12.0
        sensor_w = getattr(det, "sensor_w_mm", None) or 7.68
        sensor_h = getattr(det, "sensor_h_mm", None) or 6.14
        netd = getattr(det, "netd_mk", None) or 50.0
        det_wl_min = getattr(det, "spectral_range_min_um", None) or 8.0
        det_wl_max = getattr(det, "spectral_range_max_um", None) or 14.0

        # IFOV = pixel_size / focal_length (mrad)
        ifov_mrad = (pixel_um / focal) if focal > 0 else 0

        # 实际空间分辨率 @ 工作距离 (m)
        spatial_resolution_m = ifov_mrad * working_distance_m / 1000.0

        # FOV = 2 * arctan(sensor_size / (2 * focal))
        fov_w_deg = 2.0 * math.degrees(math.atan(sensor_w / (2.0 * focal))) if focal > 0 else 0
        fov_h_deg = 2.0 * math.degrees(math.atan(sensor_h / (2.0 * focal))) if focal > 0 else 0
        fov_diag_deg = 2.0 * math.degrees(math.atan(math.sqrt(sensor_w**2 + sensor_h**2) / (2.0 * focal))) if focal > 0 else 0

        # 波段中心匹配度
        lens_center_um = (wl_min + wl_max) / 2000.0  # nm -> um
        det_center_um = (det_wl_min + det_wl_max) / 2.0
        band_center_diff = abs(lens_center_um - det_center_um)

        from lensfit.physics import PhysicsConstants

        # NETD评分（越低越好）
        netd_score = max(0, 1.0 - (netd / PhysicsConstants.NETD_BASELINE_MK))

        # 视场偏差
        fov_error = abs(fov_diag_deg - target_fov_deg) / target_fov_deg if target_fov_deg > 0 else 1.0
        fov_match = max(0, 1.0 - fov_error)

        # 分辨率偏差
        if target_res_m and target_res_m > 0 and spatial_resolution_m > 0:
            res_error = abs(spatial_resolution_m - target_res_m) / target_res_m
            res_match = max(0, 1.0 - res_error)
        else:
            res_match = 0.5  # 无目标时给中性分

        # 成本效益
        lens_price = getattr(lens, "price_usd", None) or 0
        det_price = getattr(det, "price_usd", None) or 0
        total_price = lens_price + det_price
        cost_efficiency = 1.0 / (1.0 + total_price / 2000.0) if total_price > 0 else 0.5

        # 波段匹配度
        lens_min_um = wl_min / 1000.0
        lens_max_um = wl_max / 1000.0
        overlap_min = max(lens_min_um, det_wl_min)
        overlap_max = min(lens_max_um, det_wl_max)
        overlap = max(0, overlap_max - overlap_min)
        union = max(lens_max_um, det_wl_max) - min(lens_min_um, det_wl_min)
        band_overlap_ratio = overlap / union if union > 0 else 0

        result: dict[str, Any] = {
            "ifov_mrad": round(ifov_mrad, 4),
            "spatial_resolution_m": round(spatial_resolution_m, 4),
            "fov_w_deg": round(fov_w_deg, 2),
            "fov_h_deg": round(fov_h_deg, 2),
            "fov_diag_deg": round(fov_diag_deg, 2),
            "band_overlap_ratio": round(band_overlap_ratio, 4),
            "band_center_diff_um": round(band_center_diff, 2),
            "netd_mk": round(netd, 1),
            "netd_score": round(netd_score, 4),
            "f_number": round(fn, 2),
            "total_price_usd": round(total_price, 2),
            "pixel_size_um": round(pixel_um, 2),
            "sensor_size_mm": f"{round(sensor_w, 2)}×{round(sensor_h, 2)}",
        }

        # 变焦镜头
        if focal_max and focal_max > focal:
            fov_w_max = 2.0 * math.degrees(math.atan(sensor_w / (2.0 * focal_max))) if focal_max > 0 else 0
            fov_w_min = fov_w_deg
            result["zoom_range"] = f"{round(fov_w_max, 1)}°-{round(fov_w_min, 1)}°"
            result["focal_range"] = f"{focal}-{focal_max}mm"

        return result

    # --- Private constraint checks ---

    @staticmethod
    def _check_wavelength_coverage(combo: DeviceCombo) -> bool:
        """镜头波段覆盖目标波长."""
        lens = combo.lens
        det = combo.detector
        reqs = combo.requirements
        if not reqs or not lens or not det:
            return True

        wl_min = getattr(lens, "wavelength_min_nm", None) or 0
        wl_max = getattr(lens, "wavelength_max_nm", None) or 0
        target_wl_um = reqs.params.get("wavelength_um", 10.0)
        target_wl_nm = target_wl_um * 1000.0

        # 检查探测器波段
        det_wl_min = getattr(det, "spectral_range_min_um", None) or 0
        det_wl_max = getattr(det, "spectral_range_max_um", None) or 0

        # 镜头必须覆盖目标波长，且与探测器波段有重叠
        lens_covers = wl_min <= target_wl_nm <= wl_max
        overlap = max(0, min(wl_max / 1000.0, det_wl_max) - max(wl_min / 1000.0, det_wl_min))
        return lens_covers and overlap > 0

    @staticmethod
    def _check_sensor_coverage(combo: DeviceCombo) -> bool:
        """镜头像面覆盖探测器传感器."""
        lens = combo.lens
        det = combo.detector
        if not lens or not det:
            return True

        ic = getattr(lens, "image_circle_mm", None) or 21.0
        sensor_diag = getattr(det, "sensor_diag_mm", None) or 0
        return sensor_diag <= ic * 1.05  # 允许5%溢出

    @staticmethod
    def _check_mount_compatibility(combo: DeviceCombo) -> bool:
        """检查接口兼容性."""
        lens = combo.lens
        det = combo.detector
        if not lens or not det:
            return True

        lens_mount = getattr(lens, "mount_type", "") or ""
        det_mount = getattr(det, "mount_type", "") or ""

        # 相同接口直接兼容
        if lens_mount and det_mount and lens_mount.lower() == det_mount.lower():
            return True

        # C-mount 和 M34x0.5 可通过适配器转换
        compatible_mounts = {
            "c-mount": {"c-mount", "cs-mount", "m34x0.5"},
            "cs-mount": {"c-mount", "cs-mount", "m34x0.5"},
            "m34x0.5": {"m34x0.5", "c-mount"},
        }

        lm = lens_mount.lower().replace(" ", "")
        dm = det_mount.lower().replace(" ", "")

        if lm in compatible_mounts and dm in compatible_mounts.get(lm, set()):
            return True

        # 宽松匹配：只要有适配器可能即可
        return True

    @staticmethod
    def _check_budget(combo: DeviceCombo) -> bool:
        """总价不超过预算."""
        lens = combo.lens
        det = combo.detector
        reqs = combo.requirements
        if not reqs or not lens or not det:
            return True

        budget = reqs.params.get("budget_usd")
        if budget is None:
            return True

        lens_price = getattr(lens, "price_usd", None) or 0
        det_price = getattr(det, "price_usd", None) or 0
        return (lens_price + det_price) <= budget * 1.1  # 允许10%超预算
