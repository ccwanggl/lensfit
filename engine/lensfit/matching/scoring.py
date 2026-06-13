"""Scoring and ranking algorithms."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from lensfit.core.types import MatchResult
from lensfit.domains.base import ScoringDimension


class ScoringEngine:
    """评分引擎 — 根据领域评分维度计算综合得分."""

    def __init__(self):
        self._registry: dict[str, Callable[[Any], float]] = {
            "fov_accuracy": self._score_fov_accuracy,
            "coverage_margin": self._score_coverage_margin,
            "nyquist_match": self._score_nyquist_match,
            "direct_mount": self._score_direct_mount,
            "cost_efficiency": self._score_cost_efficiency,
            # Photography domain scorers
            "focal_match": self._score_focal_match,
            "aperture_value": self._score_aperture_value,
            # Microscope / Infrared domain scorers
            "resolution_match": self._score_resolution_match,
            "magnification_accuracy": self._score_magnification_accuracy,
            "fov_match": self._score_fov_match,
            "spatial_resolution": self._score_spatial_resolution,
            "band_match": self._score_band_match,
            "ifov": self._score_ifov,
        }

    def score(
        self,
        candidate: Any,
        dimensions: list[ScoringDimension],
    ) -> dict[str, float]:
        """计算单个候选的评分向量."""
        scores = {}
        for dim in dimensions:
            scorer = self._registry.get(dim.name)
            if scorer:
                scores[dim.name] = scorer(candidate)
            else:
                scores[dim.name] = 0.5
        return scores

    def register_scorer(self, name: str, scorer: Callable[[Any], float]) -> None:
        """注册自定义评分器."""
        self._registry[name] = scorer

    @staticmethod
    def _score_fov_accuracy(candidate: Any) -> float:
        """FOV吻合度评分.

        根据镜头实际焦距与理想焦距的偏差评分.
        """
        derived = getattr(candidate, "derived", {}) or {}
        lens = candidate.lens

        actual_focal = getattr(lens, "focal_length_mm", None)
        ideal_focal = derived.get("focal_length")

        if actual_focal is None or ideal_focal is None or ideal_focal <= 0:
            return 0.5

        error_ratio = abs(actual_focal - ideal_focal) / ideal_focal
        if error_ratio <= 0.05:
            return 1.0
        if error_ratio <= 0.15:
            return 1.0 - (error_ratio - 0.05) * 5
        if error_ratio <= 0.30:
            return 0.5 - (error_ratio - 0.15) * 2
        return 0.0

    @staticmethod
    def _score_coverage_margin(candidate: Any) -> float:
        """传感器覆盖裕量评分."""
        lens = candidate.lens
        det = candidate.detector
        image_circle = getattr(lens, "image_circle_mm", 0) or 0
        sensor_diag = getattr(det, "sensor_diag_mm", 0) or 0
        if sensor_diag <= 0:
            return 0.0
        margin = (image_circle - sensor_diag) / image_circle if image_circle > 0 else 0
        if 0.05 <= margin <= 0.20:
            return 1.0
        elif margin < 0:
            return 0.0
        else:
            return max(0, 1.0 - abs(margin - 0.10) * 5)

    @staticmethod
    def _score_nyquist_match(candidate: Any) -> float:
        """奈奎斯特采样匹配评分."""
        lens = candidate.lens
        det = candidate.detector
        pixel_size = getattr(det, "pixel_size_um", 0) or 0
        mtf50 = getattr(lens, "mtf50_lpmm", 0) or 0
        if pixel_size <= 0:
            return 0.0
        sensor_nyquist = 1000 / (2 * pixel_size)
        if mtf50 <= 0:
            return 0.5
        oversampling = mtf50 / sensor_nyquist
        # 理想过采样率 0.5-1.2，超出后线性衰减
        if 0.5 <= oversampling <= 1.2:
            return 1.0
        elif oversampling < 0.3:
            return 0.2
        else:
            # 连续评分，避免在边界处断崖
            dist = min(abs(oversampling - 0.5), abs(oversampling - 1.2))
            return max(0.2, 1.0 - dist * 1.5)

    @staticmethod
    def _score_direct_mount(candidate: Any) -> float:
        """接口直接兼容评分."""
        lens = candidate.lens
        det = candidate.detector
        lens_mount = getattr(lens, "mount_type", "")
        det_mount = getattr(det, "mount_type", "")
        if lens_mount and det_mount and lens_mount == det_mount:
            return 1.0
        return 0.5

    @staticmethod
    def _score_cost_efficiency(candidate: Any) -> float:
        """成本效益评分."""
        lens = candidate.lens
        det = candidate.detector
        lens_price = getattr(lens, "price_usd", 0) or 0
        det_price = getattr(det, "price_usd", 0) or 0
        total = lens_price + det_price
        if total <= 0:
            return 0.5
        if total <= 400:
            return 1.0
        elif total >= 2000:
            return 0.2
        else:
            return 1.0 - (total - 400) / 1600

    # ── Photography domain scorers ──

    @staticmethod
    def _score_focal_match(candidate: Any) -> float:
        """摄影焦距匹配评分 — 直接使用 calculate_derived 中计算的 focal_score."""
        derived = getattr(candidate, "derived", {}) or {}
        return derived.get("focal_score", 0.5)

    @staticmethod
    def _score_aperture_value(candidate: Any) -> float:
        """摄影光圈价值评分 — 直接使用 calculate_derived 中计算的 aperture_score."""
        derived = getattr(candidate, "derived", {}) or {}
        return derived.get("aperture_score", 0.5)

    # ── Microscope domain scorers ──

    @staticmethod
    def _score_resolution_match(candidate: Any) -> float:
        """显微镜分辨率匹配评分 — 基于 NA 达标程度."""
        reqs = getattr(candidate, "requirements", None)
        lens = candidate.lens

        obj_na = getattr(lens, "na", None) or 0.1
        target_na = reqs.params.get("objective_na", 0.1) if reqs else 0.1

        if target_na <= 0:
            return 0.5
        ratio = obj_na / target_na
        if ratio >= 1.0:
            return 1.0
        if ratio >= 0.7:
            return 0.7 + (ratio - 0.7)  # 0.7 → 1.0 线性
        return max(0.0, ratio / 0.7 * 0.7)

    @staticmethod
    def _score_magnification_accuracy(candidate: Any) -> float:
        """显微镜放大倍率吻合度."""
        derived = getattr(candidate, "derived", {}) or {}
        mag_error = derived.get("mag_error", 0.0)
        return max(0.0, 1.0 - mag_error)

    # ── Infrared domain scorers ──

    @staticmethod
    def _score_fov_match(candidate: Any) -> float:
        """红外视场匹配评分."""
        derived = getattr(candidate, "derived", {}) or {}
        return derived.get("fov_match", 0.5)

    @staticmethod
    def _score_spatial_resolution(candidate: Any) -> float:
        """红外空间分辨率匹配评分."""
        derived = getattr(candidate, "derived", {}) or {}
        return derived.get("res_match", 0.5)

    @staticmethod
    def _score_band_match(candidate: Any) -> float:
        """红外波段匹配评分."""
        derived = getattr(candidate, "derived", {}) or {}
        overlap = derived.get("band_overlap_ratio", 0.0)
        if overlap >= 0.9:
            return 1.0
        if overlap >= 0.7:
            return 0.75
        return max(0.0, overlap)

    @staticmethod
    def _score_ifov(candidate: Any) -> float:
        """红外瞬时视场角评分 — 越小 IFOV 越好."""
        derived = getattr(candidate, "derived", {}) or {}
        ifov = derived.get("ifov_mrad", 0.0)
        # IFOV < 0.5 mrad 为优秀，> 5 mrad 为较差
        if ifov <= 0:
            return 0.5
        return min(1.0, max(0.0, 1.0 - ifov / 5.0))


class TopsisRanker:
    """TOPSIS 多属性决策排序."""

    def rank(
        self,
        results: list[MatchResult],
        dimensions: list[ScoringDimension],
        weights: dict[str, float],
    ) -> list[MatchResult]:
        """TOPSIS 排序."""
        if not results:
            return []

        dim_names = [d.name for d in dimensions]
        benefit_flags = [d.is_benefit for d in dimensions]

        matrix = []
        for r in results:
            row = [r.score_vector.get(name, 0) for name in dim_names]
            matrix.append(row)

        x = np.array(matrix, dtype=float)

        # 向量归一化
        norm = np.sqrt((x**2).sum(axis=0))
        norm = np.where(norm == 0, 1, norm)
        x_norm = x / norm

        # 加权
        weights_array = np.array(
            [weights.get(name, 1.0 / len(dim_names)) for name in dim_names]
        )
        x_weighted = x_norm * weights_array

        # 确定正理想解和负理想解
        ideal_best = np.zeros(len(dim_names))
        ideal_worst = np.zeros(len(dim_names))

        for j, is_benefit in enumerate(benefit_flags):
            if is_benefit:
                ideal_best[j] = x_weighted[:, j].max()
                ideal_worst[j] = x_weighted[:, j].min()
            else:
                ideal_best[j] = x_weighted[:, j].min()
                ideal_worst[j] = x_weighted[:, j].max()

        # 计算欧氏距离
        d_best = np.sqrt(((x_weighted - ideal_best) ** 2).sum(axis=1))
        d_worst = np.sqrt(((x_weighted - ideal_worst) ** 2).sum(axis=1))

        # 相对贴近度 — 避免除零
        denominator = d_best + d_worst
        closeness = np.where(
            denominator == 0,
            0.5,
            d_worst / denominator,
        )

        for i, r in enumerate(results):
            r.score = float(closeness[i])

        return sorted(results, key=lambda x: x.score, reverse=True)
