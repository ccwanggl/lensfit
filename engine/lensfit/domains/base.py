"""Domain module base interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from lensfit.core.types import MatchResult


@dataclass
class ParameterDef:
    """参数定义，用于UI动态渲染输入表单."""

    name: str
    label: str
    type: str  # "number" | "string" | "enum" | "boolean"
    unit: str = ""
    default: Any = None
    required: bool = False
    options: list[tuple[str, str]] | None = None  # (value, label) for enum
    min_value: float | None = None
    max_value: float | None = None
    description: str = ""


@dataclass
class Constraint:
    """约束定义."""

    name: str
    check: Callable[[Any], bool]
    description: str = ""


@dataclass
class ScoringDimension:
    """评分维度定义."""

    name: str
    label: str
    weight: float = 1.0
    is_benefit: bool = True  # True: 越大越好, False: 越小越好
    description: str = ""


@dataclass
class Requirements:
    """用户需求输入."""

    domain: str
    params: dict[str, Any]


@dataclass
class DeviceCombo:
    """镜头-探测器组合."""

    lens: Any
    detector: Any
    adapter: Any | None = None
    requirements: Requirements | None = None
    derived: dict[str, Any] | None = None


class DomainModule(ABC):
    """领域模块统一接口 — 新增领域只需实现此接口并注册."""

    @property
    @abstractmethod
    def domain_id(self) -> str:
        """唯一标识，如 "industrial" / "microscope" / "infrared"."""
        pass

    @property
    @abstractmethod
    def domain_name(self) -> str:
        """显示名称."""
        pass

    @abstractmethod
    def get_parameters(self) -> list[ParameterDef]:
        """该领域支持的参数定义."""
        pass

    @abstractmethod
    def get_hard_constraints(self) -> list[Constraint]:
        """硬约束检查器列表（Stage 3 调用）."""
        pass

    @abstractmethod
    def get_scoring_dimensions(self) -> list[ScoringDimension]:
        """评分维度定义（Stage 4 调用）."""
        pass

    @abstractmethod
    def calculate_derived(self, combo: DeviceCombo) -> dict[str, Any]:
        """计算领域相关的派生参数."""
        pass

    def default_weights(self) -> dict[str, float]:
        """默认评分权重，子类可覆盖."""
        dims = self.get_scoring_dimensions()
        n = len(dims)
        return {d.name: 1.0 / n for d in dims}

    def get_benefit_flags(self) -> dict[str, bool]:
        """获取各评分维度的收益标志."""
        dims = self.get_scoring_dimensions()
        return {d.name: d.is_benefit for d in dims}
