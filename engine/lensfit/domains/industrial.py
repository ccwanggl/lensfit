"""Industrial vision domain module."""

from __future__ import annotations

from typing import Any

from lensfit.domains.base import (
    Constraint,
    DeviceCombo,
    DomainModule,
    ParameterDef,
    ScoringDimension,
)


class IndustrialVisionModule(DomainModule):
    """工业视觉领域模块 — FA镜头、远心镜头、线扫镜头、变焦镜头."""

    @property
    def domain_id(self) -> str:
        return "industrial"

    @property
    def domain_name(self) -> str:
        return "工业视觉"

    def get_parameters(self) -> list[ParameterDef]:
        return [
            ParameterDef(
                name="sensor_size",
                label="传感器尺寸",
                type="enum",
                options=[
                    ("1/4", '1/4"'),
                    ("1/3", '1/3"'),
                    ("1/2", '1/2"'),
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
                name="target_width_mm",
                label="目标宽度",
                type="number",
                unit="mm",
                default=50,
                required=True,
            ),
            ParameterDef(
                name="target_height_mm",
                label="目标高度",
                type="number",
                unit="mm",
                default=40,
                required=True,
            ),
            ParameterDef(
                name="working_distance_mm",
                label="工作距离",
                type="number",
                unit="mm",
                default=200,
                required=True,
            ),
            ParameterDef(
                name="lens_type",
                label="镜头类型",
                type="enum",
                options=[
                    ("FA", "FA定焦镜头"),
                    ("telecentric", "远心镜头"),
                    ("linescan", "线扫镜头"),
                    ("zoom", "变焦镜头"),
                ],
                default="FA",
                required=True,
            ),
            ParameterDef(
                name="interface",
                label="接口类型",
                type="enum",
                options=[
                    ("C-mount", "C-mount"),
                    ("CS-mount", "CS-mount"),
                    ("F-mount", "F-mount"),
                ],
                default="C-mount",
                required=True,
            ),
        ]

    def get_hard_constraints(self) -> list[Constraint]:
        return [
            Constraint(
                name="sensor_coverage",
                check=self._check_sensor_coverage,
                description="传感器覆盖≥像面尺寸",
            ),
            Constraint(
                name="wd_range",
                check=self._check_wd_range,
                description="工作距离在镜头标称范围内",
            ),
            Constraint(
                name="distortion_limit",
                check=self._check_distortion,
                description="畸变上限约束",
            ),
        ]

    def get_scoring_dimensions(self) -> list[ScoringDimension]:
        return [
            ScoringDimension(
                name="fov_accuracy",
                label="FOV吻合度",
                weight=3.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="coverage_margin",
                label="覆盖裕量",
                weight=2.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="nyquist_match",
                label="奈奎斯特匹配",
                weight=2.5,
                is_benefit=True,
            ),
            ScoringDimension(
                name="direct_mount",
                label="接口直接兼容",
                weight=1.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="cost_efficiency",
                label="成本效益",
                weight=1.5,
                is_benefit=True,
            ),
        ]

    def calculate_derived(self, combo: DeviceCombo) -> dict[str, Any]:
        """计算工业视觉领域的派生参数."""
        lens = combo.lens
        det = combo.detector
        reqs = combo.requirements

        if not reqs:
            return {}

        params = reqs.params
        from lensfit.core.thin_lens import ThinLensCalculator
        from lensfit.core.sensor import sensor_size_from_format

        calc = ThinLensCalculator()
        sensor = sensor_size_from_format(params.get("sensor_size", "2/3"))

        if not sensor:
            return {}

        wd = params.get("working_distance_mm", 200)
        fov_w = params.get("target_width_mm", 50)

        focal = calc.focal_from_wd_fov(wd, fov_w, sensor.w)
        afov = calc.afov_from_sensor_focal(sensor.w, focal)
        mag = calc.magnification_from_focal_wd(focal, wd)

        return {
            "focal_length": round(focal, 2),
            "afov_h": round(afov, 2),
            "magnification": round(mag, 4),
            "pixel_accuracy_mm": round(
                params.get("pixel_size_um", 3.45) / 1000 / mag, 4
            ),
        }

    # --- Private constraint checks ---

    @staticmethod
    def _check_sensor_coverage(combo: DeviceCombo) -> bool:
        lens = combo.lens
        det = combo.detector
        image_circle = getattr(lens, "image_circle_mm", None) or 0
        sensor_diag = getattr(det, "sensor_diag_mm", None) or 0
        return image_circle >= sensor_diag * 0.95

    @staticmethod
    def _check_wd_range(combo: DeviceCombo) -> bool:
        lens = combo.lens
        reqs = combo.requirements
        if not reqs:
            return True

        wd = reqs.params.get("working_distance_mm")
        if wd is None:
            return True

        min_wd = getattr(lens, "min_working_distance_mm", None)
        max_wd = getattr(lens, "max_working_distance_mm", None)

        if min_wd is not None and wd < min_wd:
            return False
        if max_wd is not None and wd > max_wd:
            return False
        return True

    @staticmethod
    def _check_distortion(combo: DeviceCombo) -> bool:
        lens = combo.lens
        distortion = getattr(lens, "distortion_percent", None)
        if distortion is None:
            return True  # 无畸变数据时放行
        return distortion <= 2.0  # 默认畸变上限 2%
