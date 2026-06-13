"""Matching engine with four-stage pipeline."""

from __future__ import annotations

import threading
import traceback
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from lensfit.core.types import FilterDiagnostic, MatchingTask, MatchResult, PhysicsTrace
from lensfit.core.utils import is_mount_compatible, nyquist_match, sensor_coverage_check
from lensfit.db.catalog import CatalogQuery
from lensfit.db.models import DetectorCatalog, LensCatalog
from lensfit.domains.base import DeviceCombo, DomainModule, Requirements
from lensfit.knowledge.engine import KnowledgeInferenceEngine, OpticalKnowledgeBase
from lensfit.matching.scoring import ScoringEngine, TopsisRanker

# Constants
_MAX_CANDIDATE_COMBOS = 100_000
_MAX_CANDIDATE_LENS = 5_000
_MAX_CANDIDATE_DET = 2_000
_MAX_RETAINED_TASKS = 1_000


class MatchingEngine:
    """通用匹配骨架 — 零领域知识，通过 DomainModule 插件扩展."""

    def __init__(self, session_factory: Callable[[], Session] | None = None):
        self.domains: dict[str, DomainModule] = {}
        self._tasks: dict[str, MatchingTask] = {}
        self._session_factory = session_factory
        self._scoring_engine = ScoringEngine()
        self._ranker = TopsisRanker()
        self._lock = threading.Lock()
        self._last_diagnostics: list[FilterDiagnostic] = []
        self._knowledge_engine = KnowledgeInferenceEngine(OpticalKnowledgeBase())

    def register_domain(self, module: DomainModule) -> None:
        """注册领域模块."""
        self.domains[module.domain_id] = module

    def get_domain(self, domain_id: str) -> DomainModule:
        """获取领域模块."""
        domain = self.domains.get(domain_id)
        if not domain:
            raise ValueError(f"Unknown domain: {domain_id}")
        return domain

    # =====================================================================
    # Stage 1: IndexPreFilter
    # =====================================================================
    def index_pre_filter(
        self,
        requirements: Requirements,
        catalog: CatalogQuery,
        strict: bool = True,
    ) -> list[DeviceCombo]:
        """索引预筛选 — 数据库层过滤，支持多领域.

        Args:
            requirements: 用户需求.
            catalog: 目录查询对象.
            strict: 为 False 时放宽工作距离、接口和传感器格式等条件，
                    用于严格过滤未命中时给出最接近的备选方案.
        """
        params = requirements.params
        domain_id = requirements.domain

        from lensfit.core.sensor import sensor_size_from_format
        from lensfit.core.thin_lens import ThinLensCalculator

        # --- Microscopy domain: filter by magnification and NA ---
        if domain_id == "microscope":
            target_mag = params.get("magnification", 20)
            target_na = params.get("objective_na", 0.1)
            scope_type = params.get("microscope_type", "compound")
            sensor = sensor_size_from_format(params.get("sensor_format", "2/3"))
            sensor_diag = sensor.diag if sensor else 11.0

            if scope_type == "stereo":
                # 体视显微镜: 查询变焦主体，变焦倍率范围匹配目标放大倍率/10(目镜)
                zoom_target = target_mag / 10.0  # 去掉10x目镜
                lenses = catalog.query_lenses(
                    category="microscope_stereo",
                    focal_min=zoom_target * 0.2,
                    focal_max=zoom_target * 2.0,
                    image_circle_min=sensor_diag * 0.3,
                    limit=_MAX_CANDIDATE_LENS,
                )
                # 按变焦范围接近度和NA排序
                lenses = sorted(
                    lenses,
                    key=lambda lens_item: (
                        abs((lens_item.focal_length_mm or 0) - zoom_target)
                        + abs((lens_item.focal_length_max or zoom_target) - zoom_target)
                        + abs((lens_item.na or 0) - target_na) * 5
                    ),
                )
            else:
                # 复式显微镜: 查询物镜
                lenses = catalog.query_lenses(
                    category="microscope",
                    focal_min=target_mag * 0.3,
                    focal_max=target_mag * 2.5,
                    image_circle_min=sensor_diag * 0.5,
                    limit=_MAX_CANDIDATE_LENS,
                )
                # 按NA接近度排序
                lenses = sorted(
                    lenses,
                    key=lambda lens_item: (
                        abs((lens_item.na or 0) - target_na) * 10
                        + abs((lens_item.focal_length_mm or 0) - target_mag)
                    ),
                )

                # 复式显微镜通常使用专用物镜接口，排除 C-mount 工业镜头
                lenses = [
                    lens_item for lens_item in lenses
                    if str(getattr(lens_item, "mount_type", "") or "").lower() != "c-mount"
                ]

            # 查询显微镜相机
            detectors = catalog.query_detectors(
                category="microscope",
                sensor_format=params.get("sensor_format"),
                limit=_MAX_CANDIDATE_DET,
            )

            combos = []
            for lens in lenses:
                for det in detectors:
                    combos.append(DeviceCombo(lens=lens, detector=det, requirements=requirements))
            return combos

        # --- Photography domain ---
        if domain_id == "photography":
            from lensfit.domains.photography import PhotographyModule

            photo = PhotographyModule()
            purpose = params.get("purpose", "portrait")
            ideal_min, ideal_max = photo.PURPOSE_FOCAL_RANGES.get(purpose, (35.0, 85.0))
            lens_type = params.get("lens_type", "all")
            mount = params.get("mount", "all")

            # 查询镜头：焦距在用途理想区间的扩展范围内
            lenses = catalog.query_lenses(
                category="photography" if lens_type == "all" else None,
                mount_type=mount if mount != "all" else None,
                focal_min=ideal_min * 0.3,
                focal_max=ideal_max * 2.5,
                limit=_MAX_CANDIDATE_LENS,
            )

            # 按焦距接近理想区间中心排序
            center = (ideal_min + ideal_max) / 2.0
            lenses = sorted(
                lenses,
                key=lambda lens_item: abs((lens_item.focal_length_mm or 0) - center),
            )

            # 变焦/定焦过滤
            if lens_type == "prime":
                lenses = [
                    lens_item for lens_item in lenses
                    if (lens_item.focal_length_max or lens_item.focal_length_mm)
                    <= lens_item.focal_length_mm * 1.01
                ]
            elif lens_type == "zoom":
                lenses = [
                    lens_item for lens_item in lenses
                    if (lens_item.focal_length_max or lens_item.focal_length_mm)
                    > lens_item.focal_length_mm * 1.01
                ]

            # 品牌过滤
            brand = params.get("brand", "all")
            if brand and brand != "all":
                brand_lower = str(brand).lower()
                lenses = [
                    lens_item for lens_item in lenses
                    if str(getattr(lens_item, "model", "") or "").lower().startswith(brand_lower)
                ]

            # 显式焦距范围过滤
            focal_min = params.get("focal_range_min")
            focal_max = params.get("focal_range_max")
            if focal_min is not None or focal_max is not None:
                focal_min_val = float(focal_min) if focal_min is not None else 0.0
                focal_max_val = float(focal_max) if focal_max is not None else 9999.0
                lenses = [
                    lens_item for lens_item in lenses
                    if focal_min_val <= (lens_item.focal_length_mm or 0) <= focal_max_val
                ]

            # 查询相机机身（探测器）
            sensor_format = params.get("sensor_format", "FF")
            detectors = catalog.query_detectors(
                sensor_format=sensor_format,
                mount_type=mount if mount != "all" else None,
                limit=_MAX_CANDIDATE_DET,
            )

            # 生成组合 — 带上限保护
            total_combos = len(lenses) * len(detectors)
            if total_combos > _MAX_CANDIDATE_COMBOS:
                lenses = lenses[: _MAX_CANDIDATE_COMBOS // max(len(detectors), 1)]

            combos = []
            for lens in lenses:
                for det in detectors:
                    combos.append(DeviceCombo(lens=lens, detector=det, requirements=requirements))
            return combos

        # --- Industrial domain: original logic ---
        calc = ThinLensCalculator()
        sensor = sensor_size_from_format(params.get("sensor_size", "2/3"))
        if not sensor:
            return []

        wd = params.get("working_distance_mm", 200)
        fov_w = params.get("target_width_mm", 50)

        focal_estimate = calc.focal_from_wd_fov(wd, fov_w, sensor.w)
        focal_min = focal_estimate * (0.5 if strict else 0.2)
        focal_max = focal_estimate * (2.0 if strict else 5.0)

        # 查询镜头
        lenses = catalog.query_lenses(
            category=params.get("lens_type", "FA"),
            mount_type=params.get("interface") if strict else None,
            focal_min=focal_min,
            focal_max=focal_max,
            image_circle_min=sensor.diag * (0.8 if strict else 0.5),
            wd_min=wd * (0.5 if strict else 0.2) if strict else None,
            wd_max=wd * (2.0 if strict else 5.0) if strict else None,
            limit=_MAX_CANDIDATE_LENS,
        )

        # 查询探测器
        detectors = catalog.query_detectors(
            sensor_format=params.get("sensor_size") if strict else None,
            mount_type=params.get("interface") if strict else None,
            limit=_MAX_CANDIDATE_DET,
        )

        # 生成组合 — 带上限保护
        total_combos = len(lenses) * len(detectors)
        if total_combos > _MAX_CANDIDATE_COMBOS:
            # 优先保留焦距最接近估计值的镜头
            lenses = sorted(
                lenses,
                key=lambda lens_item: abs((lens_item.focal_length_mm or 0) - focal_estimate),
            )[: _MAX_CANDIDATE_COMBOS // max(len(detectors), 1)]

        combos = []
        for lens in lenses:
            for det in detectors:
                combos.append(DeviceCombo(lens=lens, detector=det, requirements=requirements))
        return combos

    # =====================================================================
    # Stage 2: QuickHardFilter
    # =====================================================================
    def quick_hard_filter(
        self,
        candidates: list[DeviceCombo],
        diagnostics: list[FilterDiagnostic] | None = None,
        strict: bool = True,
    ) -> list[DeviceCombo]:
        """快速硬约束剪枝 — O(1) 检查.

        Args:
            strict: 为 False 时放宽像圆、接口和工作距离要求，用于给出备选方案.
        """
        valid = []
        rejected: dict[str, int] = {
            "image_circle_too_small": 0,
            "mount_incompatible": 0,
            "wd_out_of_range": 0,
        }
        for combo in candidates:
            lens: LensCatalog = combo.lens
            det: DetectorCatalog = combo.detector
            reqs = combo.requirements

            # 2a: 像圆覆盖
            if det.sensor_diag_mm and lens.image_circle_mm:
                margin_factor = 1.05 if strict else 1.20
                if det.sensor_diag_mm > lens.image_circle_mm * margin_factor:
                    rejected["image_circle_too_small"] += 1
                    continue

            # 2b: 接口兼容
            if strict and lens.mount_type and det.mount_type:
                compatible, _ = is_mount_compatible(lens.mount_type, det.mount_type)
                if not compatible:
                    rejected["mount_incompatible"] += 1
                    continue

            # 2c: WD 范围
            if strict and reqs:
                wd = reqs.params.get("working_distance_mm")
                if wd is not None:
                    if lens.min_working_distance_mm and wd < lens.min_working_distance_mm:
                        rejected["wd_out_of_range"] += 1
                        continue
                    if lens.max_working_distance_mm and wd > lens.max_working_distance_mm:
                        rejected["wd_out_of_range"] += 1
                        continue

            valid.append(combo)

        if diagnostics is not None:
            suggestion = self._suggest_from_rejected(rejected)
            diagnostics.append(FilterDiagnostic(
                stage="quick_hard_filter" + ("" if strict else "_fallback"),
                before_count=len(candidates),
                after_count=len(valid),
                rejected_reasons={k: v for k, v in rejected.items() if v > 0},
                suggestion=suggestion,
            ))
        return valid

    @staticmethod
    def _suggest_from_rejected(rejected: dict[str, int]) -> str:
        if not any(rejected.values()):
            return ""
        max_reason = max(rejected, key=rejected.get)
        suggestions = {
            "image_circle_too_small": "建议：增大传感器尺寸或放宽像圆要求",
            "mount_incompatible": "建议：更换接口类型或使用转接环",
            "wd_out_of_range": "建议：调整工作距离范围",
        }
        return suggestions.get(max_reason, "建议：放宽筛选条件")

    # =====================================================================
    # Stage 3: DomainHardFilter
    # =====================================================================
    def apply_domain_constraints(
        self,
        candidates: list[DeviceCombo],
        domain: DomainModule,
        diagnostics: list[FilterDiagnostic] | None = None,
        strict: bool = True,
    ) -> list[DeviceCombo]:
        """应用领域硬约束.

        Args:
            strict: 为 False 时跳过工作距离硬约束并放宽覆盖要求.
        """
        constraints = domain.get_hard_constraints()
        valid = []
        constraint_fails: dict[str, int] = {}
        for combo in candidates:
            try:
                passed = True
                for c in constraints:
                    if c.name == "wd_range" and not strict:
                        continue
                    if c.name == "sensor_coverage" and not strict:
                        # 放宽覆盖要求：允许最多 15% 的渐晕
                        lens = combo.lens
                        det = combo.detector
                        image_circle = getattr(lens, "image_circle_mm", None) or 0
                        sensor_diag = getattr(det, "sensor_diag_mm", None) or 0
                        if (
                            sensor_diag > 0
                            and image_circle > 0
                            and image_circle < sensor_diag * 0.85
                        ):
                            constraint_fails[c.name] = constraint_fails.get(c.name, 0) + 1
                            passed = False
                            break
                        continue
                    if not c.check(combo):
                        constraint_fails[c.name] = constraint_fails.get(c.name, 0) + 1
                        passed = False
                        break
                if passed:
                    valid.append(combo)
            except Exception:
                # 单个候选异常不中断整批
                continue

        if diagnostics is not None:
            suggestion = ""
            if constraint_fails:
                top_fail = max(constraint_fails, key=constraint_fails.get)
                suggestion = f"建议：检查领域约束「{top_fail}」是否过于严格"
            diagnostics.append(FilterDiagnostic(
                stage="domain_constraints" + ("" if strict else "_fallback"),
                before_count=len(candidates),
                after_count=len(valid),
                rejected_reasons=constraint_fails,
                suggestion=suggestion,
            ))
        return valid

    # =====================================================================
    # Stage 4: FullScoring
    # =====================================================================
    def score_candidates(
        self, candidates: list[DeviceCombo], domain: DomainModule
    ) -> list[MatchResult]:
        """全量评分."""
        scoring_dims = domain.get_scoring_dimensions()
        results = []

        for combo in candidates:
            try:
                # 计算派生参数
                combo.derived = domain.calculate_derived(combo)

                # 通用物理计算
                det: DetectorCatalog = combo.detector
                lens: LensCatalog = combo.lens

                trace_chain: list[PhysicsTrace] = []

                # Trace 1: derived params
                if combo.derived:
                    for key, val in combo.derived.items():
                        if isinstance(val, (int, float)) and key not in ("coverage", "nyquist"):
                            trace_chain.append(PhysicsTrace(
                                step=f"derived:{key}",
                                formula=key.replace("_", " "),
                                inputs={"lens": lens.model, "detector": det.model},
                                output=float(val),
                                unit="",
                                assumption="domain derived parameter",
                                principle="光学薄透镜近似与几何成像关系",
                            ))

                # Trace 2: coverage check
                coverage = sensor_coverage_check(
                    det.sensor_w_mm or 0, det.sensor_h_mm or 0, lens.image_circle_mm or 0
                )
                trace_chain.append(PhysicsTrace(
                    step="coverage",
                    formula="sensor coverage check",
                    inputs={
                        "sensor_w_mm": det.sensor_w_mm or 0,
                        "sensor_h_mm": det.sensor_h_mm or 0,
                        "image_circle_mm": lens.image_circle_mm or 0,
                    },
                    output=coverage.get("coverage_ratio", 1.0),
                    unit="ratio",
                    assumption="image circle must cover sensor diagonal",
                    principle="几何光学：像圆直径 ≥ 传感器对角线",
                ))

                # Trace 3: nyquist
                nyquist = None
                if det.pixel_size_um and det.pixel_size_um > 0:
                    try:
                        nyquist = nyquist_match(
                            det.pixel_size_um,
                            lens_mtf50_lpmm=lens.mtf50_lpmm,
                        )
                        trace_chain.append(PhysicsTrace(
                            step="nyquist",
                            formula="nyquist frequency",
                            inputs={
                                "pixel_size_um": det.pixel_size_um,
                                "mtf50_lpmm": lens.mtf50_lpmm or 0,
                            },
                            output=(
                                nyquist.get("sensor_nyquist_lpmm", 0)
                                if isinstance(nyquist, dict) else 0
                            ),
                            unit="lp/mm",
                            assumption="sampling theorem",
                            principle="采样定理：光学分辨率需高于奈奎斯特频率以避免混叠",
                        ))
                    except ValueError:
                        pass

                # 评分 — 由领域维度 + 通用维度共同构成
                score_vector = self._scoring_engine.score(combo, scoring_dims)

                # 通用评分维度：补充领域未覆盖的物理指标
                score_vector["coverage_margin"] = self._score_coverage(
                    lens.image_circle_mm, det.sensor_diag_mm
                )
                score_vector["nyquist_match"] = self._score_nyquist(nyquist)
                score_vector["wd_match"] = self._score_wd(
                    getattr(lens, "min_working_distance_mm", None),
                    getattr(lens, "max_working_distance_mm", None),
                    (
                        combo.requirements.params.get("working_distance_mm")
                        if combo.requirements
                        else None
                    ),
                )

                # Trace 4: composite score
                trace_chain.append(PhysicsTrace(
                    step="composite",
                    formula="composite score",
                    inputs={k: round(v, 3) for k, v in score_vector.items()},
                    output=sum(score_vector.values()) / max(len(score_vector), 1),
                    unit="score",
                    assumption="weighted average of scoring dimensions",
                    principle="多目标决策：加权综合评分排序",
                ))

                result = MatchResult(
                    lens_id=lens.id,
                    detector_id=det.id,
                    lens_model=getattr(lens, "model", ""),
                    detector_model=getattr(det, "model", ""),
                    score_vector=score_vector,
                    derived={
                        **(combo.derived or {}),
                        "coverage": coverage,
                        "nyquist": nyquist,
                    },
                    coverage_ratio=coverage.get("coverage_ratio", 1.0),
                    vignetting=coverage.get("vignetting", False),
                    derivation_chain=trace_chain,
                )
                result.reason = self._generate_reason(result)
                results.append(result)
            except Exception:
                # 单个候选异常不中断整批
                continue

        return results

    @staticmethod
    def _generate_reason(result: MatchResult) -> str:
        """根据评分向量和派生参数生成一句话匹配理由."""
        reasons: list[str] = []

        # Coverage / vignetting
        if result.vignetting:
            reasons.append("⚠ 像圆不足，存在渐晕风险")
        elif result.coverage_ratio >= 0.95:
            reasons.append("✓ 像圆完全覆盖传感器")
        elif result.coverage_ratio >= 0.8:
            reasons.append("∼ 像圆基本覆盖传感器")
        else:
            reasons.append("⚠ 像圆覆盖不足")

        # Score vector analysis
        sv = result.score_vector
        if sv:
            sorted_dims = sorted(sv.items(), key=lambda kv: kv[1], reverse=True)
            top_dim, top_score = sorted_dims[0]
            dim_label_map = {
                "fov_accuracy": "视场精度",
                "coverage_margin": "覆盖裕量",
                "nyquist_match": "奈奎斯特匹配",
                "direct_mount": "接口兼容性",
                "cost_efficiency": "性价比",
                "focal_match": "焦距匹配度",
                "aperture_value": "光圈值",
                "resolution_match": "分辨率匹配",
                "magnification_accuracy": "放大倍率精度",
                "fov_match": "视场匹配",
                "spatial_resolution": "空间分辨率",
                "band_match": "波段匹配",
                "ifov": "瞬时视场",
            }
            label = dim_label_map.get(top_dim, top_dim)
            if top_score >= 0.9:
                reasons.append(f"✓ {label}表现优异")
            elif top_score >= 0.7:
                reasons.append(f"∼ {label}良好")
            elif top_score < 0.5:
                reasons.append(f"⚠ {label}偏低")

        # Derived params
        d = result.derived
        focal = d.get("focal_length") if isinstance(d, dict) else None
        if isinstance(focal, (int, float)):
            reasons.append(f"估算焦距 {focal:.1f}mm")

        mag = d.get("magnification") if isinstance(d, dict) else None
        if isinstance(mag, (int, float)):
            reasons.append(f"放大倍率 {mag:.2f}x")

        # Pixel accuracy
        acc = d.get("pixel_accuracy_mm") if isinstance(d, dict) else None
        if isinstance(acc, (int, float)):
            reasons.append(f"像素精度 {acc:.3f}mm/px")

        # Compose — keep it under 60 chars
        text = "；".join(reasons[:2])
        if len(text) > 60:
            text = text[:57] + "..."
        return text

    @staticmethod
    def _score_coverage(image_circle: float | None, sensor_diag: float | None) -> float:
        """传感器覆盖裕量评分 (0-1)."""
        ic = image_circle or 0
        sd = sensor_diag or 0
        if ic <= 0 or sd <= 0:
            return 0.0
        margin = (ic - sd) / ic
        if margin < 0:
            return 0.0
        if 0.05 <= margin <= 0.20:
            return 1.0
        if margin > 0.30:
            return max(0.0, 1.0 - (margin - 0.20) * 3)
        return max(0.0, 1.0 - abs(margin - 0.10) * 5)

    @staticmethod
    def _score_nyquist(nyquist: dict[str, Any] | None) -> float:
        """奈奎斯特采样匹配评分 (0-1)."""
        if not nyquist:
            return 0.5
        if nyquist["matched"]:
            return 1.0
        ratio = nyquist.get("oversampling_ratio", 0)
        if ratio < 0.3:
            return 0.2
        if ratio > 1.5:
            return 0.3
        return 0.6

    @staticmethod
    def _score_wd(
        min_wd: float | None,
        max_wd: float | None,
        target_wd: float | None,
    ) -> float:
        """工作距离匹配评分 (0-1)."""
        if target_wd is None:
            return 0.5
        if min_wd is None and max_wd is None:
            return 0.5
        if min_wd is not None and max_wd is not None and min_wd <= target_wd <= max_wd:
            return 1.0
        # Penalize distance outside the declared range
        if max_wd is not None and target_wd > max_wd and max_wd > 0:
            return max(0.0, 1.0 - (target_wd - max_wd) / max_wd)
        if min_wd is not None and target_wd < min_wd and min_wd > 0:
            return max(0.0, 1.0 - (min_wd - target_wd) / min_wd)
        return 0.5

    def explain_result(self, result: MatchResult) -> dict[str, Any]:
        """使用知识库为匹配结果生成结构化解释."""
        return self._knowledge_engine.explain_result(result).to_dict()

    # =====================================================================
    # Stage 5: Ranking
    # =====================================================================
    def rank_results(
        self,
        results: list[MatchResult],
        domain: DomainModule,
        weights: dict[str, float] | None = None,
    ) -> list[MatchResult]:
        """排序结果."""
        if not weights:
            # 使用领域定义的显式权重，而非平均权重
            weights = {d.name: d.weight for d in domain.get_scoring_dimensions()}
            # 为通用维度补充默认权重
            weights.setdefault("coverage_margin", 1.5)
            weights.setdefault("nyquist_match", 1.5)
            weights.setdefault("wd_match", 1.5)

        dims = domain.get_scoring_dimensions()
        # 将通用维度也加入排序维度列表
        from lensfit.domains.base import ScoringDimension
        all_dims = list(dims)
        all_dims.append(
            ScoringDimension(
                name="coverage_margin",
                label="覆盖裕量",
                weight=weights.get("coverage_margin", 1.5),
                is_benefit=True,
            )
        )
        all_dims.append(
            ScoringDimension(
                name="nyquist_match",
                label="奈奎斯特匹配",
                weight=weights.get("nyquist_match", 1.5),
                is_benefit=True,
            )
        )
        all_dims.append(
            ScoringDimension(
                name="wd_match",
                label="工作距离匹配",
                weight=weights.get("wd_match", 1.5),
                is_benefit=True,
            )
        )

        return self._ranker.rank(results, all_dims, weights)

    # =====================================================================
    # Progressive Matching (SSE)
    # =====================================================================
    def match_progressive(
        self,
        requirements: Requirements,
        top_k: int = 20,
        weights: dict[str, float] | None = None,
    ):
        """渐进式匹配生成器 — 流式推送各阶段结果."""
        if not self._session_factory:
            raise RuntimeError("Database session factory required for progressive matching")

        diagnostics: list[FilterDiagnostic] = []

        with self._session_factory() as session:
            domain = self.get_domain(requirements.domain)
            catalog = CatalogQuery(session)

            # Stage 1-5: strict
            ranked = self._match_one_pass(
                requirements, catalog, domain, top_k, weights, diagnostics, strict=True
            )

            # Fallback to relaxed matching if strict mode yields nothing
            if not ranked:
                ranked = self._match_one_pass(
                    requirements, catalog, domain, top_k, weights, diagnostics, strict=False
                )
                if ranked and diagnostics:
                    diagnostics.append(FilterDiagnostic(
                        stage="fallback",
                        before_count=0,
                        after_count=len(ranked),
                        rejected_reasons={},
                        suggestion="已自动放宽工作距离/接口/覆盖要求，展示最接近的备选方案",
                    ))

            if not ranked and diagnostics:
                # No candidates even in fallback mode
                last = diagnostics[-1]
                if last.stage.startswith("index_pre_filter"):
                    yield {
                        "stage": "completed",
                        "progress": 1.0,
                        "results": [],
                        "diagnostics": [d.to_dict() for d in diagnostics],
                    }
                    return

            yield {
                "stage": "completed",
                "progress": 1.0,
                "results": [r.to_dict() for r in ranked[:top_k]],
                "diagnostics": [d.to_dict() for d in diagnostics],
            }

    # =====================================================================
    # Public API
    # =====================================================================
    def _match_one_pass(
        self,
        requirements: Requirements,
        catalog: CatalogQuery,
        domain: DomainModule,
        top_k: int,
        weights: dict[str, float] | None,
        diagnostics: list[FilterDiagnostic],
        strict: bool = True,
    ) -> list[MatchResult]:
        """执行一次完整匹配流程（严格或宽松模式）."""
        candidates = self.index_pre_filter(requirements, catalog, strict=strict)
        if len(candidates) == 0:
            if strict:
                diagnostics.append(FilterDiagnostic(
                    stage="index_pre_filter",
                    before_count=0,
                    after_count=0,
                    rejected_reasons={},
                    suggestion="建议：放宽焦距或视场范围，或检查数据库是否已导入",
                ))
            return []

        candidates = self.quick_hard_filter(candidates, diagnostics, strict=strict)
        candidates = self.apply_domain_constraints(candidates, domain, diagnostics, strict=strict)
        results = self.score_candidates(candidates, domain)
        ranked = self.rank_results(results, domain, weights)
        return ranked[:top_k]

    def match_sync(
        self,
        requirements: Requirements,
        top_k: int = 20,
        weights: dict[str, float] | None = None,
    ) -> list[MatchResult]:
        """同步匹配 — 小数据集场景."""
        if not self._session_factory:
            raise RuntimeError("Database session factory required for sync matching")

        diagnostics: list[FilterDiagnostic] = []

        with self._session_factory() as session:
            domain = self.get_domain(requirements.domain)
            catalog = CatalogQuery(session)

            ranked = self._match_one_pass(
                requirements, catalog, domain, top_k, weights, diagnostics, strict=True
            )

            # 严格模式无结果时，使用宽松模式给出最接近的备选方案
            if not ranked:
                ranked = self._match_one_pass(
                    requirements, catalog, domain, top_k, weights, diagnostics, strict=False
                )
                if ranked and diagnostics:
                    diagnostics.append(FilterDiagnostic(
                        stage="fallback",
                        before_count=0,
                        after_count=len(ranked),
                        rejected_reasons={},
                        suggestion="已自动放宽工作距离/接口/覆盖要求，展示最接近的备选方案",
                    ))

            self._last_diagnostics = diagnostics
            return ranked

    def match_async(self, requirements: Requirements) -> MatchingTask:
        """异步匹配 — 返回任务ID，前端轮询进度."""
        task_id = str(uuid.uuid4())
        task = MatchingTask(task_id=task_id, status="pending")

        with self._lock:
            self._tasks[task_id] = task

        self._evict_old_tasks()

        thread = threading.Thread(
            target=self._run_match_task,
            args=(task_id, requirements),
            daemon=True,
        )
        thread.start()

        return task

    def _run_match_task(self, task_id: str, requirements: Requirements) -> None:
        """在后台线程中执行匹配任务."""
        task = self._tasks.get(task_id)
        if not task:
            return

        diagnostics: list[FilterDiagnostic] = []

        def _update(**kwargs) -> bool:
            """更新任务状态，返回 False 表示已取消应中止."""
            with self._lock:
                if task.status == "cancelled":
                    return False
                for k, v in kwargs.items():
                    setattr(task, k, v)
            return True

        if not _update(status="running", stage="index_filter"):
            return

        try:
            if not self._session_factory:
                raise RuntimeError("Database session factory required")

            with self._session_factory() as session:
                domain = self.get_domain(requirements.domain)
                catalog = CatalogQuery(session)

                # Stage 1-5 (strict)
                ranked = self._match_one_pass(
                    requirements, catalog, domain, 20, None, diagnostics, strict=True
                )
                if not _update(
                    total_candidates=sum(
                        1 for d in diagnostics if d.stage == "index_pre_filter"
                    ),
                    progress=0.1 if ranked else 0.05,
                    stage="quick_filter" if ranked else "fallback",
                ):
                    return

                # Fallback to relaxed matching if strict mode yields nothing
                if not ranked:
                    ranked = self._match_one_pass(
                        requirements, catalog, domain, 20, None, diagnostics, strict=False
                    )
                    if ranked and diagnostics:
                        diagnostics.append(FilterDiagnostic(
                            stage="fallback",
                            before_count=0,
                            after_count=len(ranked),
                            rejected_reasons={},
                            suggestion="已自动放宽工作距离/接口/覆盖要求，展示最接近的备选方案",
                        ))
                    if not _update(
                        total_candidates=sum(
                            1 for d in diagnostics if "pre_filter" in d.stage
                        ),
                        progress=0.1,
                        stage="quick_filter",
                    ):
                        return

                _update(
                    result=ranked,
                    progress=1.0,
                    status="completed",
                    completed_at=datetime.now(UTC),
                    diagnostics=diagnostics,
                )

        except Exception as e:
            _update(
                status="failed",
                error=f"{e}\n{traceback.format_exc()}",
                completed_at=datetime.now(UTC),
            )

    def get_task(self, task_id: str) -> MatchingTask | None:
        """获取任务状态."""
        with self._lock:
            return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status in ("pending", "running"):
                task.status = "cancelled"
                return True
            return False

    def _evict_old_tasks(self) -> None:
        """淘汰过期任务 — 优先清理 completed/failed 的过时任务，保留 running 任务."""
        now = datetime.now(UTC)
        ttl_completed = timedelta(hours=1)
        ttl_running = timedelta(hours=24)

        with self._lock:
            # Phase 1: 清理已超时的 completed/failed 任务 (1小时 TTL)
            expired = [
                tid
                for tid, task in self._tasks.items()
                if task.status in ("completed", "failed", "cancelled")
                and task.completed_at
                and (now - task.completed_at) > ttl_completed
            ]
            for tid in expired:
                self._tasks.pop(tid, None)

            # Phase 2: 清理超时的 running 任务 (24小时 TTL)
            expired_running = [
                tid
                for tid, task in self._tasks.items()
                if task.status == "running"
                and (now - task.created_at) > ttl_running
            ]
            for tid in expired_running:
                self._tasks.pop(tid, None)

            # Phase 3: 如果仍然超过上限，淘汰最旧的 completed/failed 任务
            if len(self._tasks) > _MAX_RETAINED_TASKS:
                finished = sorted(
                    [
                        (tid, t)
                        for tid, t in self._tasks.items()
                        if t.status in ("completed", "failed", "cancelled")
                    ],
                    key=lambda kv: kv[1].completed_at or kv[1].created_at,
                )
                to_evict = len(self._tasks) - _MAX_RETAINED_TASKS
                for tid, _ in finished[:to_evict]:
                    self._tasks.pop(tid, None)

            # Phase 4: 极端情况 — 仍然超过上限时淘汰最旧的 pending 任务
            if len(self._tasks) > _MAX_RETAINED_TASKS:
                pending = sorted(
                    [(tid, t) for tid, t in self._tasks.items()],
                    key=lambda kv: kv[1].created_at,
                )
                to_evict = len(self._tasks) - _MAX_RETAINED_TASKS
                for tid, _ in pending[:to_evict]:
                    self._tasks.pop(tid, None)
