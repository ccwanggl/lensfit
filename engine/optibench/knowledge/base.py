"""光学物理知识库类型定义."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FormulaParam:
    """公式参数定义."""

    name: str
    name_cn: str
    unit: str = ""
    description: str = ""
    required: bool = True


@dataclass
class OpticalFormula:
    """光学公式定义 — 可计算、可解释、可查询."""

    id: str
    name_cn: str
    expression: str
    latex: str = ""          # LaTeX 渲染表达式
    params: list[FormulaParam] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    principle: str = ""      # 物理原理（中文）
    assumption: str = ""     # 适用假设（中文）
    domain: str = "all"      # "all" | "industrial" | "microscope" | "photography" | "infrared"
    compute_fn: Callable[..., Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name_cn": self.name_cn,
            "expression": self.expression,
            "latex": self.latex or self.expression,
            "params": [
                {"name": p.name, "name_cn": p.name_cn, "unit": p.unit, "description": p.description}
                for p in self.params
            ],
            "outputs": self.outputs,
            "principle": self.principle,
            "assumption": self.assumption,
            "domain": self.domain,
        }


@dataclass
class OpticalConstraint:
    """物理约束定义 — 可检查、可解释、可建议."""

    id: str
    name_cn: str
    principle: str = ""                  # 为什么有这个约束
    check_fn: Callable[[Any], bool] | None = None
    failure_explanation_tpl: str = ""    # 失败解释模板，支持 {key} 插值
    suggestion: str = ""                 # 失败时的建议
    severity: str = "error"              # "error" | "warning" | "info"

    def format_failure(self, context: dict[str, Any]) -> str:
        """根据上下文格式化失败解释."""
        try:
            return self.failure_explanation_tpl.format(**context)
        except (KeyError, ValueError):
            return self.failure_explanation_tpl

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name_cn": self.name_cn,
            "principle": self.principle,
            "failure_explanation_tpl": self.failure_explanation_tpl,
            "suggestion": self.suggestion,
            "severity": self.severity,
        }


@dataclass
class OpticalPrinciple:
    """物理原理条目 — 连接公式与约束的上层知识."""

    id: str
    name_cn: str
    description: str = ""
    related_formulas: list[str] = field(default_factory=list)
    related_constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name_cn": self.name_cn,
            "description": self.description,
            "related_formulas": self.related_formulas,
            "related_constraints": self.related_constraints,
        }


@dataclass
class ConstraintViolation:
    """约束违规记录."""

    constraint_id: str
    constraint_name: str
    explanation: str
    suggestion: str
    severity: str
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "constraint_name": self.constraint_name,
            "explanation": self.explanation,
            "suggestion": self.suggestion,
            "severity": self.severity,
            "context": self.context,
        }


@dataclass
class InferenceResult:
    """知识推理结果."""

    derived_params: dict[str, Any] = field(default_factory=dict)
    trace_chain: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ResultExplanation:
    """匹配结果的结构化解释."""

    formulas_used: list[dict[str, Any]] = field(default_factory=list)
    constraints_passed: list[dict[str, Any]] = field(default_factory=list)
    constraints_failed: list[dict[str, Any]] = field(default_factory=list)
    score_explanation: str = ""
    physical_summary: str = ""
