"""Microscopy domain module."""

from __future__ import annotations

from typing import Any

from lensfit.domains.base import (
    Constraint,
    DeviceCombo,
    DomainModule,
    ParameterDef,
    ScoringDimension,
)


class MicroscopyModule(DomainModule):
    """显微镜领域模块 — 物镜、相机和照明系统匹配."""

    @property
    def domain_id(self) -> str:
        return "microscope"

    @property
    def domain_name(self) -> str:
        return "显微镜视觉"

    def get_parameters(self) -> list[ParameterDef]:
        return [
            ParameterDef(
                name="microscope_type",
                label="显微镜类型",
                type="enum",
                options=[
                    ("compound", "复式显微镜"),
                    ("stereo", "体视显微镜"),
                ],
                default="compound",
                required=True,
            ),
            ParameterDef(
                name="objective_na",
                label="物镜数值孔径 (NA)",
                type="number",
                unit="",
                default=0.65,
                min_value=0.01,
                max_value=1.45,
                required=True,
            ),
            ParameterDef(
                name="magnification",
                label="目标放大倍率",
                type="number",
                unit="×",
                default=20.0,
                min_value=0.5,
                max_value=150.0,
                required=True,
            ),
            ParameterDef(
                name="wavelength_nm",
                label="照明波长",
                type="number",
                unit="nm",
                default=550.0,
                min_value=300.0,
                max_value=1100.0,
                required=True,
            ),
            ParameterDef(
                name="sensor_format",
                label="传感器尺寸",
                type="enum",
                options=[
                    ("1/3", '1/3"'),
                    ("1/2.5", '1/2.5"'),
                    ("1/2.3", '1/2.3"'),
                    ("1/2", '1/2"'),
                    ("1/1.8", '1/1.8"'),
                    ("2/3", '2/3"'),
                    ("1", '1"'),
                ],
                default="2/3",
                required=True,
            ),
            ParameterDef(
                name="pixel_size_um",
                label="像元尺寸",
                type="number",
                unit="μm",
                default=3.45,
                min_value=1.0,
                max_value=10.0,
                required=True,
            ),
            ParameterDef(
                name="application",
                label="应用场景",
                type="enum",
                options=[
                    ("biology", "生物/生命科学"),
                    ("materials", "材料/金相分析"),
                    ("semiconductor", "半导体检测"),
                    ("fluorescence", "荧光成像"),
                    ("dissection", "解剖/手术"),
                    ("inspection", "工业检测"),
                ],
                default="biology",
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
                name="sensor_coverage",
                check=self._check_sensor_coverage,
                description="传感器尺寸不超过物镜像场",
            ),
            Constraint(
                name="budget",
                check=self._check_budget,
                description="总价不超过预算",
            ),
            Constraint(
                name="na_sufficient",
                check=self._check_na_sufficient,
                description="物镜NA满足分辨率需求",
            ),
        ]

    def get_scoring_dimensions(self) -> list[ScoringDimension]:
        return [
            ScoringDimension(
                name="resolution_match",
                label="分辨率匹配度",
                weight=3.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="nyquist_ratio",
                label="奈奎斯特采样比",
                weight=2.5,
                is_benefit=True,
            ),
            ScoringDimension(
                name="magnification_accuracy",
                label="放大倍率吻合度",
                weight=2.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="fov_coverage",
                label="视场覆盖度",
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
        """计算显微镜领域派生参数 — 支持复式和体视显微镜."""
        lens = combo.lens
        det = combo.detector
        reqs = combo.requirements

        if not reqs or not lens or not det:
            return {}

        params = reqs.params
        wavelength_nm = params.get("wavelength_nm", 550)
        target_mag = params.get("magnification", 20.0)
        scope_type = params.get("microscope_type", "compound")

        # 物镜参数
        obj_na = getattr(lens, "na", None) or 0.1
        obj_mag = getattr(lens, "focal_length_mm", None) or 10.0
        obj_mag_max = getattr(lens, "focal_length_max", None) or obj_mag
        fn = getattr(lens, "image_circle_mm", None) or 22.0
        wd = getattr(lens, "nominal_wd_mm", None) or 0

        # 相机参数
        pixel_um = getattr(det, "pixel_size_um", None) or 3.45
        sensor_w = getattr(det, "sensor_w_mm", None) or 8.44
        sensor_h = getattr(det, "sensor_h_mm", None) or 7.07

        from lensfit.physics import PhysicsConstants

        # 计算总放大倍率
        if scope_type == "stereo":
            # 体视显微镜: 总放大 = 变焦倍率 × 目镜倍率 × 物镜倍率(1x)
            # 使用平均变焦倍率
            zoom_avg = (obj_mag + obj_mag_max) / 2 if obj_mag_max else obj_mag
            total_mag = zoom_avg * PhysicsConstants.STEREO_EYEPIECE_MAG
        else:
            # 复式显微镜: 总放大 = 物镜放大倍率
            total_mag = obj_mag

        # 瑞利分辨率: d = k * λ / NA (单位: nm)
        optical_resolution_nm = PhysicsConstants.RAYLEIGH_COEFFICIENT * wavelength_nm / obj_na
        optical_resolution_um = optical_resolution_nm / 1000.0

        # 数字分辨率: 像素尺寸 / 总放大倍率
        digital_resolution_um = pixel_um / total_mag

        # 实际视场 (mm)
        fov_w = sensor_w / total_mag
        fov_h = sensor_h / total_mag

        # 奈奎斯特采样比
        nyquist_ratio = optical_resolution_um / digital_resolution_um if digital_resolution_um > 0 else 0

        # 覆盖比
        sensor_diag = (sensor_w ** 2 + sensor_h ** 2) ** 0.5
        coverage_ratio = min(sensor_diag / fn, 1.0) if fn > 0 else 0

        # 放大倍率偏差
        mag_error = abs(total_mag - target_mag) / target_mag if target_mag > 0 else 1.0

        result: dict[str, Any] = {
            "optical_resolution_um": round(optical_resolution_um, 4),
            "digital_resolution_um": round(digital_resolution_um, 4),
            "total_magnification": round(total_mag, 2),
            "nyquist_ratio": round(nyquist_ratio, 2),
            "fov_w_mm": round(fov_w, 4),
            "fov_h_mm": round(fov_h, 4),
            "coverage_ratio": round(coverage_ratio, 4),
            "mag_error": round(mag_error, 4),
            "pixel_size_at_sample_um": round(digital_resolution_um, 4),
            "microscope_type": scope_type,
        }

        if scope_type == "stereo":
            result["zoom_range"] = f"{obj_mag}x-{obj_mag_max}x"
            result["working_distance_mm"] = round(wd, 1) if wd else None

        return result

    # --- Private constraint checks ---

    @staticmethod
    def _check_sensor_coverage(combo: DeviceCombo) -> bool:
        lens = combo.lens
        det = combo.detector
        if not lens or not det:
            return True

        fn = getattr(lens, "image_circle_mm", None) or 22.0
        sensor_diag = getattr(det, "sensor_diag_mm", None) or 0
        return sensor_diag <= fn * 1.05  # 允许5%溢出

    @staticmethod
    def _check_budget(combo: DeviceCombo) -> bool:
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

    @staticmethod
    def _check_na_sufficient(combo: DeviceCombo) -> bool:
        lens = combo.lens
        reqs = combo.requirements
        if not reqs or not lens:
            return True

        obj_na = getattr(lens, "na", None) or 0
        target_na = reqs.params.get("objective_na", 0.1)

        if target_na <= 0:
            return True
        return obj_na >= target_na * 0.7  # NA 至少达到目标的70%
