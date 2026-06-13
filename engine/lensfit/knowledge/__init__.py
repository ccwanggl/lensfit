"""LensFit 光学物理知识库.

将零散的光学计算函数和硬编码的约束检查重构为可查询、可解释、可扩展的结构化知识系统。
"""

from lensfit.knowledge.base import (
    ConstraintViolation,
    InferenceResult,
    OpticalConstraint,
    OpticalFormula,
    OpticalPrinciple,
    ResultExplanation,
)
from lensfit.knowledge.constraints import (
    ALL_CONSTRAINTS,
    check_all_constraints,
    get_constraint_by_id,
)
from lensfit.knowledge.engine import KnowledgeInferenceEngine, OpticalKnowledgeBase
from lensfit.knowledge.formulas import ALL_FORMULAS, get_formula_by_id, list_formulas
from lensfit.knowledge.presets import ALL_PRESETS, PresetConfig, get_preset_by_id, list_presets

__all__ = [
    "OpticalFormula",
    "OpticalConstraint",
    "OpticalPrinciple",
    "ConstraintViolation",
    "InferenceResult",
    "ResultExplanation",
    "ALL_FORMULAS",
    "get_formula_by_id",
    "list_formulas",
    "ALL_CONSTRAINTS",
    "get_constraint_by_id",
    "check_all_constraints",
    "KnowledgeInferenceEngine",
    "OpticalKnowledgeBase",
    "ALL_PRESETS",
    "list_presets",
    "get_preset_by_id",
    "PresetConfig",
]
