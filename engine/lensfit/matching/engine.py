"""Matching engine with four-stage pipeline."""

from __future__ import annotations

import threading
import traceback
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from lensfit.core.types import MatchResult, MatchingTask
from lensfit.core.utils import is_mount_compatible, nyquist_match, sensor_coverage_check
from lensfit.db.catalog import CatalogQuery
from lensfit.db.models import DetectorCatalog, LensCatalog
from lensfit.domains.base import DeviceCombo, DomainModule, Requirements
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
        self, requirements: Requirements, catalog: CatalogQuery
    ) -> list[DeviceCombo]:
        """索引预筛选 — 数据库层过滤，支持多领域."""
        params = requirements.params
        domain_id = requirements.domain

        from lensfit.core.thin_lens import ThinLensCalculator
        from lensfit.core.sensor import sensor_size_from_format

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
                    key=lambda l: abs((l.focal_length_mm or 0) - zoom_target) + abs((l.focal_length_max or zoom_target) - zoom_target) + abs((l.na or 0) - target_na) * 5,
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
                    key=lambda l: abs((l.na or 0) - target_na) * 10 + abs((l.focal_length_mm or 0) - target_mag),
                )

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
                key=lambda l: abs((l.focal_length_mm or 0) - center),
            )

            # 变焦/定焦过滤
            if lens_type == "prime":
                lenses = [l for l in lenses if (l.focal_length_max or l.focal_length_mm) <= l.focal_length_mm * 1.01]
            elif lens_type == "zoom":
                lenses = [l for l in lenses if (l.focal_length_max or l.focal_length_mm) > l.focal_length_mm * 1.01]

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
        focal_min = focal_estimate * 0.5
        focal_max = focal_estimate * 2.0

        # 查询镜头
        lenses = catalog.query_lenses(
            category=params.get("lens_type", "FA"),
            mount_type=params.get("interface"),
            focal_min=focal_min,
            focal_max=focal_max,
            image_circle_min=sensor.diag * 0.8,
            wd_min=wd * 0.5,
            wd_max=wd * 2.0,
            limit=_MAX_CANDIDATE_LENS,
        )

        # 查询探测器
        detectors = catalog.query_detectors(
            sensor_format=params.get("sensor_size"),
            mount_type=params.get("interface"),
            limit=_MAX_CANDIDATE_DET,
        )

        # 生成组合 — 带上限保护
        total_combos = len(lenses) * len(detectors)
        if total_combos > _MAX_CANDIDATE_COMBOS:
            # 优先保留焦距最接近估计值的镜头
            lenses = sorted(
                lenses,
                key=lambda l: abs((l.focal_length_mm or 0) - focal_estimate),
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
        self, candidates: list[DeviceCombo]
    ) -> list[DeviceCombo]:
        """快速硬约束剪枝 — O(1) 检查."""
        valid = []
        for combo in candidates:
            lens: LensCatalog = combo.lens
            det: DetectorCatalog = combo.detector
            reqs = combo.requirements

            # 2a: 像圆覆盖
            if det.sensor_diag_mm and lens.image_circle_mm:
                if det.sensor_diag_mm > lens.image_circle_mm * 1.05:
                    continue

            # 2b: 接口兼容
            if lens.mount_type and det.mount_type:
                compatible, _ = is_mount_compatible(lens.mount_type, det.mount_type)
                if not compatible:
                    continue

            # 2c: WD 范围
            if reqs:
                wd = reqs.params.get("working_distance_mm")
                if wd is not None:
                    if lens.min_working_distance_mm and wd < lens.min_working_distance_mm:
                        continue
                    if lens.max_working_distance_mm and wd > lens.max_working_distance_mm:
                        continue

            valid.append(combo)
        return valid

    # =====================================================================
    # Stage 3: DomainHardFilter
    # =====================================================================
    def apply_domain_constraints(
        self, candidates: list[DeviceCombo], domain: DomainModule
    ) -> list[DeviceCombo]:
        """应用领域硬约束."""
        constraints = domain.get_hard_constraints()
        valid = []
        for combo in candidates:
            try:
                if all(c.check(combo) for c in constraints):
                    valid.append(combo)
            except Exception:
                # 单个候选异常不中断整批
                continue
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

                coverage = sensor_coverage_check(
                    det.sensor_w_mm or 0, det.sensor_h_mm or 0, lens.image_circle_mm or 0
                )

                nyquist = None
                if det.pixel_size_um and det.pixel_size_um > 0:
                    try:
                        nyquist = nyquist_match(
                            det.pixel_size_um,
                            lens_mtf50_lpmm=lens.mtf50_lpmm,
                        )
                    except ValueError:
                        pass

                # 评分 — 由领域维度 + 通用维度共同构成
                score_vector = self._scoring_engine.score(combo, scoring_dims)

                # 通用评分维度：补充领域未覆盖的物理指标
                score_vector["coverage_margin"] = self._score_coverage(
                    lens.image_circle_mm, det.sensor_diag_mm
                )
                score_vector["nyquist_match"] = self._score_nyquist(nyquist)

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
                )
                results.append(result)
            except Exception:
                # 单个候选异常不中断整批
                continue

        return results

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

        dims = domain.get_scoring_dimensions()
        # 将通用维度也加入排序维度列表
        from lensfit.domains.base import ScoringDimension
        all_dims = list(dims)
        all_dims.append(ScoringDimension(name="coverage_margin", label="覆盖裕量", weight=weights.get("coverage_margin", 1.5), is_benefit=True))
        all_dims.append(ScoringDimension(name="nyquist_match", label="奈奎斯特匹配", weight=weights.get("nyquist_match", 1.5), is_benefit=True))

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

        with self._session_factory() as session:
            domain = self.get_domain(requirements.domain)
            catalog = CatalogQuery(session)

            # Stage 1: PreFilter
            candidates = self.index_pre_filter(requirements, catalog)
            yield {
                "stage": "prefilter",
                "progress": 0.1,
                "candidates": len(candidates),
                "preview": [],
            }

            # Stage 2: QuickHardFilter
            candidates = self.quick_hard_filter(candidates)
            yield {
                "stage": "filtered",
                "progress": 0.3,
                "candidates": len(candidates),
            }

            # Stage 3: DomainHardFilter
            candidates = self.apply_domain_constraints(candidates, domain)
            yield {
                "stage": "domain_filter",
                "progress": 0.5,
                "candidates": len(candidates),
            }

            # Stage 4: Scoring
            results = self.score_candidates(candidates, domain)
            yield {
                "stage": "scoring",
                "progress": 0.8,
                "candidates": len(results),
            }

            # Stage 5: Ranking
            ranked = self.rank_results(results, domain, weights)
            yield {
                "stage": "completed",
                "progress": 1.0,
                "results": [r.to_dict() for r in ranked[:top_k]],
            }

    # =====================================================================
    # Public API
    # =====================================================================
    def match_sync(
        self,
        requirements: Requirements,
        top_k: int = 20,
        weights: dict[str, float] | None = None,
    ) -> list[MatchResult]:
        """同步匹配 — 小数据集场景."""
        if not self._session_factory:
            raise RuntimeError("Database session factory required for sync matching")

        with self._session_factory() as session:
            domain = self.get_domain(requirements.domain)
            catalog = CatalogQuery(session)

            candidates = self.index_pre_filter(requirements, catalog)
            candidates = self.quick_hard_filter(candidates)
            candidates = self.apply_domain_constraints(candidates, domain)
            results = self.score_candidates(candidates, domain)
            ranked = self.rank_results(results, domain, weights)

            return ranked[:top_k]

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

                # Stage 1
                candidates = self.index_pre_filter(requirements, catalog)
                if not _update(total_candidates=len(candidates), progress=0.1, stage="quick_filter"):
                    return

                # Stage 2
                candidates = self.quick_hard_filter(candidates)
                if not _update(filtered_candidates=len(candidates), progress=0.3, stage="domain_filter"):
                    return

                # Stage 3
                candidates = self.apply_domain_constraints(candidates, domain)
                if not _update(progress=0.5, stage="scoring"):
                    return

                # Stage 4
                results = self.score_candidates(candidates, domain)
                if not _update(progress=0.8, stage="ranking"):
                    return

                # Stage 5
                ranked = self.rank_results(results, domain)
                _update(result=ranked, progress=1.0, status="completed", completed_at=datetime.now(timezone.utc))

        except Exception as e:
            _update(status="failed", error=f"{e}\n{traceback.format_exc()}", completed_at=datetime.now(timezone.utc))

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
        now = datetime.now(timezone.utc)
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
                    [(tid, t) for tid, t in self._tasks.items() if t.status in ("completed", "failed", "cancelled")],
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
