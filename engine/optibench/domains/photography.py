"""Photography domain module."""

from __future__ import annotations

from typing import Any

from optibench.domains.base import (
    Constraint,
    DeviceCombo,
    DomainModule,
    ParameterDef,
    ScoringDimension,
)
from optibench.physics import PhysicsConstants


class PhotographyModule(DomainModule):
    """摄影领域模块 — 镜头与相机机身匹配."""

    # 用途 → 理想焦距区间 (mm)
    PURPOSE_FOCAL_RANGES: dict[str, tuple[float, float]] = {
        "portrait": (50.0, 135.0),
        "landscape": (14.0, 35.0),
        "street": (24.0, 50.0),
        "macro": (50.0, 105.0),
        "sports": (70.0, 600.0),
        "video": (16.0, 85.0),
        "astro": (14.0, 24.0),
    }

    # 画幅 → 像场直径 (mm) — 引用 PhysicsConstants 确保一致性
    FORMAT_CIRCLES: dict[str, float] = {
        "FF": PhysicsConstants.FORMAT_CIRCLE_FF_MM,
        "APS-C": PhysicsConstants.FORMAT_CIRCLE_APSC_MM,
        "M43": PhysicsConstants.FORMAT_CIRCLE_M43_MM,
    }

    @property
    def domain_id(self) -> str:
        return "photography"

    @property
    def domain_name(self) -> str:
        return "摄影"

    def get_parameters(self) -> list[ParameterDef]:
        return [
            ParameterDef(
                name="purpose",
                label="拍摄用途",
                type="enum",
                options=[
                    ("portrait", "人像"),
                    ("landscape", "风景"),
                    ("street", "街拍"),
                    ("macro", "微距"),
                    ("sports", "体育/野生动物"),
                    ("video", "视频"),
                    ("astro", "星空/天文"),
                ],
                default="portrait",
                required=True,
            ),
            ParameterDef(
                name="sensor_format",
                label="相机画幅",
                type="enum",
                options=[
                    ("FF", "全画幅 (FF)"),
                    ("APS-C", "APS-C"),
                    ("M43", "M43"),
                ],
                default="FF",
                required=True,
            ),
            ParameterDef(
                name="lens_type",
                label="镜头类型",
                type="enum",
                options=[
                    ("all", "全部"),
                    ("prime", "定焦"),
                    ("zoom", "变焦"),
                ],
                default="all",
                required=False,
            ),
            ParameterDef(
                name="mount",
                label="镜头卡口",
                type="enum",
                options=[
                    ("all", "全部卡口"),
                    ("RF", "Canon RF"),
                    ("EF", "Canon EF"),
                    ("E-mount", "Sony E"),
                    ("Z-mount", "Nikon Z"),
                    ("X-mount", "Fujifilm X"),
                    ("L-mount", "L-mount"),
                ],
                default="all",
                required=False,
            ),
            ParameterDef(
                name="budget_usd",
                label="预算上限",
                type="number",
                unit="USD",
                default=2000.0,
                min_value=0.0,
                max_value=20000.0,
                required=False,
            ),
            ParameterDef(
                name="max_aperture",
                label="最大光圈要求",
                type="number",
                unit="f/",
                default=2.8,
                min_value=0.95,
                max_value=22.0,
                required=False,
                description="希望的最大光圈值，越小越好（如 f/1.4 比 f/2.8 更大）",
            ),
        ]

    def get_hard_constraints(self) -> list[Constraint]:
        return [
            Constraint(
                name="budget",
                check=self._check_budget,
                description="镜头价格不超过预算",
            ),
            Constraint(
                name="format_coverage",
                check=self._check_format_coverage,
                description="镜头像场覆盖相机画幅",
            ),
            Constraint(
                name="mount_compatibility",
                check=self._check_mount_compatibility,
                description="镜头卡口与机身兼容",
            ),
        ]

    def get_scoring_dimensions(self) -> list[ScoringDimension]:
        return [
            ScoringDimension(
                name="focal_match",
                label="焦距匹配度",
                weight=3.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="coverage_margin",
                label="画幅覆盖裕量",
                weight=2.5,
                is_benefit=True,
            ),
            ScoringDimension(
                name="aperture_value",
                label="光圈价值",
                weight=2.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="cost_efficiency",
                label="成本效益",
                weight=1.5,
                is_benefit=True,
            ),
            ScoringDimension(
                name="brand_match",
                label="品牌偏好",
                weight=1.0,
                is_benefit=True,
            ),
            ScoringDimension(
                name="nyquist_match",
                label="分辨率匹配",
                weight=1.0,
                is_benefit=True,
            ),
        ]

    def calculate_derived(self, combo: DeviceCombo) -> dict[str, Any]:
        """计算摄影领域派生参数."""
        lens = combo.lens
        det = combo.detector
        reqs = combo.requirements

        if not reqs or not lens or not det:
            return {}

        params = reqs.params
        purpose = params.get("purpose", "portrait")
        sensor_format = params.get("sensor_format", "FF")

        # 焦距
        focal = getattr(lens, "focal_length_mm", None) or 50.0
        focal_min = getattr(lens, "focal_length_min", None) or focal
        focal_max = getattr(lens, "focal_length_max", None) or focal
        is_zoom = focal_max > focal_min

        # 用途理想焦距区间
        ideal_min, ideal_max = self.PURPOSE_FOCAL_RANGES.get(purpose, (35.0, 85.0))

        # 焦距匹配分 (0-1)
        if ideal_min <= focal <= ideal_max:
            focal_score = 1.0
        else:
            dist = min(abs(focal - ideal_min), abs(focal - ideal_max))
            focal_score = max(0.0, 1.0 - dist / (ideal_max - ideal_min))

        # 画幅覆盖
        req_circle = self.FORMAT_CIRCLES.get(sensor_format, 43.3)
        lens_circle = getattr(lens, "image_circle_mm", None) or 43.3
        coverage_ratio = lens_circle / req_circle if req_circle > 0 else 1.0
        coverage_margin = (lens_circle - req_circle) / req_circle if req_circle > 0 else 0.0

        # 光圈价值 (越大光圈 = 越小 f 值 = 越高分)
        lens_aperture = getattr(lens, "max_aperture", None) or 2.8
        req_aperture = params.get("max_aperture", 2.8)
        if lens_aperture <= req_aperture:
            aperture_score = 1.0
        else:
            # f/2.8 要求但镜头只有 f/4 → 降分
            aperture_score = max(0.0, 1.0 - (lens_aperture - req_aperture) / req_aperture)

        # 成本
        lens_price = getattr(lens, "price_usd", None) or 0
        budget = params.get("budget_usd")
        if budget and budget > 0:
            if lens_price <= budget:
                cost_efficiency = max(0.0, 1.0 - lens_price / budget)
            else:
                cost_efficiency = max(0.0, 1.0 - (lens_price - budget) / budget)
        else:
            cost_efficiency = 0.5

        # 品牌偏好
        brand = params.get("brand", "all")
        lens_model = getattr(lens, "model", "") or ""
        if brand and brand != "all":
            brand_score = 1.0 if lens_model.lower().startswith(str(brand).lower()) else 0.2
        else:
            brand_score = 0.5

        result: dict[str, Any] = {
            "focal_length_mm": round(focal, 1),
            "focal_range_mm": f"{focal_min}-{focal_max}" if is_zoom else f"{focal}",
            "is_zoom": is_zoom,
            "focal_score": round(focal_score, 4),
            "ideal_focal_range": [ideal_min, ideal_max],
            "coverage_ratio": round(min(coverage_ratio, 1.0), 4),
            "coverage_margin": round(coverage_margin, 4),
            "aperture_score": round(aperture_score, 4),
            "lens_aperture": round(lens_aperture, 2),
            "required_aperture": round(req_aperture, 2),
            "cost_efficiency": round(cost_efficiency, 4),
            "brand_score": round(brand_score, 4),
            "lens_price_usd": round(lens_price, 2),
        }

        # 传感器信息
        if det:
            result["sensor_format"] = sensor_format
            result["sensor_diag_mm"] = round(getattr(det, "sensor_diag_mm", None) or 0, 2)

        return result

    # --- Private constraint checks ---

    @staticmethod
    def _check_budget(combo: DeviceCombo) -> bool:
        lens = combo.lens
        reqs = combo.requirements
        if not reqs or not lens:
            return True

        budget = reqs.params.get("budget_usd")
        if budget is None:
            return True

        lens_price = getattr(lens, "price_usd", None) or 0
        return lens_price <= budget * 1.2  # 允许20%超预算

    @staticmethod
    def _check_format_coverage(combo: DeviceCombo) -> bool:
        lens = combo.lens
        reqs = combo.requirements
        if not reqs or not lens:
            return True

        sensor_format = reqs.params.get("sensor_format", "FF")
        format_circles = {
            "FF": 43.3,
            "APS-C": 28.3,
            "M43": 21.6,
        }
        req_circle = format_circles.get(sensor_format, 43.3)
        lens_circle = getattr(lens, "image_circle_mm", None) or 0

        # 允许轻微裁切（85%覆盖）
        return lens_circle >= req_circle * 0.85

    @staticmethod
    def _check_mount_compatibility(combo: DeviceCombo) -> bool:
        lens = combo.lens
        reqs = combo.requirements
        if not reqs or not lens:
            return True

        req_mount = reqs.params.get("mount", "all")
        if req_mount == "all":
            return True

        lens_mount = getattr(lens, "mount_type", "") or ""
        return lens_mount.lower() == req_mount.lower()
