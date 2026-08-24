"""Core type definitions for OptiBench engine."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class OpticalParams:
    """光学系统核心参数."""

    focal_length: float | None = None
    working_distance: float | None = None
    fov_w: float | None = None
    fov_h: float | None = None
    sensor_w: float | None = None
    sensor_h: float | None = None
    magnification: float | None = None
    afov_h: float | None = None
    afov_v: float | None = None
    extension: float | None = None


@dataclass
class SensorSize:
    """传感器物理尺寸."""

    w: float
    h: float

    @property
    def diag(self) -> float:
        return (self.w**2 + self.h**2) ** 0.5


@dataclass
class PhysicsTrace:
    """物理推导链单步记录 — 可审计的光学计算溯源."""

    step: str = ""
    formula: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    output: float = 0.0
    unit: str = ""
    assumption: str = ""
    principle: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "formula": self.formula,
            "inputs": self.inputs,
            "output": self.output,
            "unit": self.unit,
            "assumption": self.assumption,
            "principle": self.principle,
        }


@dataclass
class MatchResult:
    """单个匹配结果."""

    lens_id: int
    detector_id: int
    lens_model: str = ""
    detector_model: str = ""
    score: float = 0.0
    score_vector: dict[str, float] = field(default_factory=dict)
    derived: dict[str, Any] = field(default_factory=dict)
    coverage_ratio: float = 1.0
    vignetting: bool = False
    derivation_chain: list[PhysicsTrace] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "lens_id": self.lens_id,
            "detector_id": self.detector_id,
            "lens_model": self.lens_model,
            "detector_model": self.detector_model,
            "score": self.score,
            "score_vector": self.score_vector,
            "derived": self.derived,
            "coverage_ratio": self.coverage_ratio,
            "vignetting": self.vignetting,
            "derivation_chain": [t.to_dict() for t in self.derivation_chain],
            "reason": self.reason,
        }


@dataclass
class FilterDiagnostic:
    """匹配过滤阶段诊断信息 — 用于零结果分析."""

    stage: str = ""
    before_count: int = 0
    after_count: int = 0
    rejected_reasons: dict[str, int] = field(default_factory=dict)
    suggestion: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "before_count": self.before_count,
            "after_count": self.after_count,
            "rejected_reasons": self.rejected_reasons,
            "suggestion": self.suggestion,
        }


@dataclass
class MatchingTask:
    """异步匹配任务状态."""

    task_id: str
    status: str = "pending"
    progress: float = 0.0
    stage: str = ""
    total_candidates: int = 0
    filtered_candidates: int = 0
    result: list[MatchResult] | None = None
    diagnostics: list[FilterDiagnostic] | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    # Internal cancellation signal — not serialized.
    cancel_event: threading.Event = field(default_factory=threading.Event)
