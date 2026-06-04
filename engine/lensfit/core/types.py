"""Core type definitions for LensFit engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class OpticalParams:
    """光学系统核心参数."""

    focal_length: Optional[float] = None
    working_distance: Optional[float] = None
    fov_w: Optional[float] = None
    fov_h: Optional[float] = None
    sensor_w: Optional[float] = None
    sensor_h: Optional[float] = None
    magnification: Optional[float] = None
    afov_h: Optional[float] = None
    afov_v: Optional[float] = None
    extension: Optional[float] = None


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

    formula: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    output: float = 0.0
    unit: str = ""
    assumption: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "formula": self.formula,
            "inputs": self.inputs,
            "output": self.output,
            "unit": self.unit,
            "assumption": self.assumption,
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
    result: Optional[list[MatchResult]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
