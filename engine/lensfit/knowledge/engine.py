"""光学物理知识推理引擎."""

from __future__ import annotations

from typing import Any

from lensfit.core.types import PhysicsTrace, MatchResult
from lensfit.knowledge.base import (
    ConstraintViolation,
    InferenceResult,
    ResultExplanation,
)
from lensfit.knowledge.formulas import ALL_FORMULAS, get_formula_by_id, list_formulas
from lensfit.knowledge.constraints import ALL_CONSTRAINTS, get_constraint_by_id, check_all_constraints


class OpticalKnowledgeBase:
    """光学知识库容器 — 管理公式、约束、原理的注册与查询."""

    def __init__(self):
        self._formulas = {f.id: f for f in ALL_FORMULAS}
        self._constraints = {c.id: c for c in ALL_CONSTRAINTS}

    def get_formula(self, fid: str) -> Any:
        return self._formulas.get(fid)

    def get_constraint(self, cid: str) -> Any:
        return self._constraints.get(cid)

    def list_formulas(self, domain: str | None = None) -> list[Any]:
        if domain is None or domain == "all":
            return list(self._formulas.values())
        return [f for f in self._formulas.values() if f.domain in ("all", domain)]

    def list_constraints(self) -> list[Any]:
        return list(self._constraints.values())


class KnowledgeInferenceEngine:
    """知识推理引擎 — 基于光学知识库进行推导、检查、解释."""

    def __init__(self, kb: OpticalKnowledgeBase | None = None):
        self.kb = kb or OpticalKnowledgeBase()

    # =====================================================================
    # Inference
    # =====================================================================
    def infer(self, known_params: dict[str, Any], domain: str = "all") -> InferenceResult:
        """基于已知参数，应用所有适用的公式推导未知参数，返回推导链.

        Args:
            known_params: 已知的物理参数字典。
            domain: 领域过滤，"all" 表示不限领域。

        Returns:
            InferenceResult 包含推导出的参数和推导链。
        """
        derived = dict(known_params)
        trace_chain: list[dict[str, Any]] = []

        formulas = self.kb.list_formulas(domain)
        changed = True
        max_iter = 10
        iteration = 0

        while changed and iteration < max_iter:
            changed = False
            iteration += 1
            for formula in formulas:
                if formula.compute_fn is None:
                    continue
                # 检查是否所有必需参数都已知
                missing = []
                for p in formula.params:
                    if p.required and p.name not in derived:
                        missing.append(p.name)
                if missing:
                    continue
                # 检查输出是否已存在（避免重复计算）
                all_outputs_exist = all(o in derived for o in formula.outputs)
                if all_outputs_exist:
                    continue

                # 收集参数
                kwargs = {}
                for p in formula.params:
                    if p.name in derived:
                        kwargs[p.name] = derived[p.name]

                try:
                    result = formula.compute_fn(**kwargs)
                    # 统一结果格式
                    if isinstance(result, dict):
                        for k, v in result.items():
                            if k not in derived:
                                derived[k] = v
                    elif isinstance(result, (int, float)):
                        if formula.outputs:
                            derived[formula.outputs[0]] = result
                    elif isinstance(result, tuple) and formula.outputs:
                        for i, v in enumerate(result):
                            if i < len(formula.outputs) and formula.outputs[i] not in derived:
                                derived[formula.outputs[i]] = v

                    trace_chain.append({
                        "formula_id": formula.id,
                        "formula_name": formula.name_cn,
                        "expression": formula.expression,
                        "inputs": kwargs,
                        "outputs": result if isinstance(result, dict) else {formula.outputs[0]: result} if formula.outputs else {},
                        "principle": formula.principle,
                        "assumption": formula.assumption,
                    })
                    changed = True
                except Exception:
                    continue

        return InferenceResult(derived_params=derived, trace_chain=trace_chain)

    # =====================================================================
    # Constraint Checking
    # =====================================================================
    def check_constraints(self, combo, domain: str = "all") -> list[ConstraintViolation]:
        """检查所有约束，返回违规列表（含解释、建议、严重程度）."""
        return check_all_constraints(combo)

    # =====================================================================
    # Explanation
    # =====================================================================
    def explain_trace(self, trace: PhysicsTrace) -> dict[str, Any]:
        """为单个推导步骤从知识库查询完整的公式和原理解释."""
        # 尝试通过 step 字段匹配公式 ID
        formula = None
        if trace.step:
            formula = get_formula_by_id(trace.step)
        if formula is None and trace.formula:
            # 尝试通过 formula 文本模糊匹配
            for f in ALL_FORMULAS:
                if f.name_cn in trace.formula or trace.formula in f.name_cn:
                    formula = f
                    break
        if formula is None:
            return {
                "matched": False,
                "formula_id": trace.step,
                "formula_name": trace.formula,
                "principle": trace.principle or "暂无知识库解释",
                "assumption": trace.assumption or "",
            }
        return {
            "matched": True,
            "formula_id": formula.id,
            "formula_name": formula.name_cn,
            "expression": formula.expression,
            "principle": formula.principle,
            "assumption": formula.assumption,
            "params": [
                {"name": p.name, "name_cn": p.name_cn, "unit": p.unit}
                for p in formula.params
            ],
        }

    def explain_result(self, result: MatchResult) -> ResultExplanation:
        """为匹配结果生成结构化解释."""
        explanation = ResultExplanation()

        # 收集使用的公式
        seen_formulas: set[str] = set()
        for t in result.derivation_chain:
            info = self.explain_trace(t)
            if info.get("matched") and info.get("formula_id"):
                fid = info["formula_id"]
                if fid not in seen_formulas:
                    seen_formulas.add(fid)
                    explanation.formulas_used.append({
                        "id": fid,
                        "name": info["formula_name"],
                        "expression": info.get("expression", ""),
                        "principle": info.get("principle", ""),
                    })

        # 物理摘要
        parts: list[str] = []
        if result.coverage_ratio >= 0.95:
            parts.append("像圈完全覆盖传感器")
        elif result.coverage_ratio >= 0.8:
            parts.append("像圈基本覆盖传感器")
        else:
            parts.append("像圈覆盖不足，存在渐晕风险")

        if result.derived:
            d = result.derived
            focal = d.get("focal_length")
            if isinstance(focal, (int, float)):
                parts.append(f"估算焦距 {focal:.1f}mm")
            mag = d.get("magnification")
            if isinstance(mag, (int, float)):
                parts.append(f"放大倍率 {mag:.3f}x")
            acc = d.get("pixel_accuracy_mm")
            if isinstance(acc, (int, float)):
                parts.append(f"像素精度 {acc:.4f}mm/px")

        sv = result.score_vector
        if sv:
            top_dim = max(sv.items(), key=lambda kv: kv[1])
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
            label = dim_label_map.get(top_dim[0], top_dim[0])
            parts.append(f"评分维度中「{label}」得分最高（{top_dim[1]:.2f}）")

        explanation.physical_summary = "；".join(parts)

        # 评分解释
        explanation.score_explanation = (
            f"综合评分 {result.score:.3f} 由 TOPSIS 多属性决策算法计算得出，"
            f"考虑了 {len(sv)} 个评分维度的加权贴近度。"
        )

        return explanation
