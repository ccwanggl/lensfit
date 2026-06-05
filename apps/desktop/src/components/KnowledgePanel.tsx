import { useState, useEffect, useCallback } from "react";
import { ChevronDown, ChevronRight, Calculator, Loader2 } from "lucide-react";
import { listKnowledgeFormulas, listKnowledgeConstraints, knowledgeInfer, type KnowledgeFormula, type KnowledgeConstraint } from "../utils/api";
import { toast } from "../hooks/useToast";

interface Props {
  form: Record<string, unknown>;
  domain?: string;
  activeTab: "formulas" | "constraints" | "trace";
  selectedResult?: {
    lens_model?: string;
    derivation_chain?: Array<{
      step?: string;
      formula?: string;
      inputs?: Record<string, unknown>;
      output?: number;
      unit?: string;
      assumption?: string;
      principle?: string;
    }>;
    reason?: string;
  } | null;
}

export default function KnowledgePanel({ form, domain = "industrial", activeTab, selectedResult }: Props) {
  const [formulas, setFormulas] = useState<KnowledgeFormula[]>([]);
  const [constraints, setConstraints] = useState<KnowledgeConstraint[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedFormula, setExpandedFormula] = useState<string | null>(null);
  const [expandedConstraint, setExpandedConstraint] = useState<string | null>(null);
  const [inferResult, setInferResult] = useState<{ derived_params: Record<string, unknown>; trace_chain: Array<Record<string, unknown>> } | null>(null);
  const [inferLoading, setInferLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listKnowledgeFormulas(domain).then((d) => setFormulas(d.items ?? [])).catch(() => toast("error", "加载失败", "无法获取公式库")),
      listKnowledgeConstraints().then((d) => setConstraints(d.items ?? [])).catch(() => toast("error", "加载失败", "无法获取约束库")),
    ]).finally(() => setLoading(false));
  }, [domain]);

  const runInfer = useCallback(async () => {
    setInferLoading(true);
    try {
      const result = await knowledgeInfer(form, domain);
      setInferResult(result);
    } catch {
      toast("error", "推理失败", "知识库推理出错");
    } finally {
      setInferLoading(false);
    }
  }, [form, domain]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 size={16} className="animate-spin text-indigo-500" />
      </div>
    );
  }

  if (activeTab === "formulas") {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-slate-500 dark:text-slate-400">共 {formulas.length} 个公式</span>
          <button
            onClick={runInfer}
            disabled={inferLoading}
            className="text-xs flex items-center gap-1.5 px-3 py-1 rounded-md bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors disabled:opacity-50"
          >
            {inferLoading ? <Loader2 size={14} className="animate-spin" /> : <Calculator size={14} />}
            实时推理
          </button>
        </div>

        {inferResult && (
          <div className="p-3 rounded-lg bg-white dark:bg-slate-800 border border-indigo-100 dark:border-indigo-800/30 mb-2">
            <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-300 mb-2">推理结果</p>
            <div className="space-y-1.5">
              {Object.entries(inferResult.derived_params).filter(([k]) => !Object.keys(form).includes(k)).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 dark:text-slate-400">{k}</span>
                  <span className="font-mono text-slate-700 dark:text-slate-300">{typeof v === "number" ? v.toFixed(3) : String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {formulas.map((f) => (
          <div key={f.id} className="rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 overflow-hidden">
            <button
              onClick={() => setExpandedFormula(expandedFormula === f.id ? null : f.id)}
              className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <div>
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{f.name_cn}</span>
                <span className="text-xs text-slate-400 dark:text-slate-500 ml-2 font-mono">{f.expression}</span>
              </div>
              {expandedFormula === f.id ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
            </button>
            {expandedFormula === f.id && (
              <div className="px-4 pb-4 space-y-3">
                {f.params.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">参数</p>
                    <div className="flex flex-wrap gap-1.5">
                      {f.params.map((p) => (
                        <span key={p.name} className="inline-flex items-center px-2 py-1 rounded bg-slate-100 dark:bg-slate-700 text-xs text-slate-600 dark:text-slate-300">
                          {p.name_cn} <span className="text-slate-400 dark:text-slate-500 ml-0.5">({p.unit})</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {f.principle && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">物理原理</p>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{f.principle}</p>
                  </div>
                )}
                {f.assumption && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">适用假设</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{f.assumption}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  }

  if (activeTab === "constraints") {
    return (
      <div className="space-y-3">
        {constraints.map((c) => (
          <div key={c.id} className="rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 overflow-hidden">
            <button
              onClick={() => setExpandedConstraint(expandedConstraint === c.id ? null : c.id)}
              className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${c.severity === "error" ? "bg-rose-400" : c.severity === "warning" ? "bg-amber-400" : "bg-emerald-400"}`} />
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{c.name_cn}</span>
              </div>
              {expandedConstraint === c.id ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
            </button>
            {expandedConstraint === c.id && (
              <div className="px-4 pb-4 space-y-3">
                <div>
                  <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">物理原理</p>
                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{c.principle}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">失败解释</p>
                  <p className="text-xs text-rose-600 dark:text-rose-400 leading-relaxed">{c.failure_explanation_tpl}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">建议</p>
                  <p className="text-xs text-indigo-600 dark:text-indigo-400 leading-relaxed">{c.suggestion}</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  }

  // trace tab
  return (
    <div className="space-y-4">
      {!selectedResult?.derivation_chain || selectedResult.derivation_chain.length === 0 ? (
        <div className="text-center py-4">
          <p className="text-sm text-slate-400 dark:text-slate-500">选择一个匹配方案查看推导链的物理原理解释</p>
        </div>
      ) : (
        <>
          {selectedResult.reason && (
            <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
              <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-300 mb-1">匹配理由</p>
              <p className="text-sm text-indigo-600 dark:text-indigo-400">{selectedResult.reason}</p>
            </div>
          )}
          <div className="space-y-3">
            {selectedResult.derivation_chain.map((step, i) => (
              <div key={i} className="relative pl-6">
                {i < (selectedResult.derivation_chain?.length ?? 0) - 1 && (
                  <div className="absolute left-[9px] top-6 bottom-[-12px] w-px bg-slate-200 dark:bg-slate-700" />
                )}
                <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-indigo-100 dark:bg-indigo-900/40 border border-indigo-300 dark:border-indigo-700 flex items-center justify-center">
                  <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400">{i + 1}</span>
                </div>
                <div className="p-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">{step.step || step.formula || "计算步骤"}</p>
                  {step.principle && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">{step.principle}</p>
                  )}
                  {step.assumption && (
                    <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">假设：{step.assumption}</p>
                  )}
                  {step.inputs && Object.keys(step.inputs).length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {Object.entries(step.inputs).slice(0, 4).map(([k, v]) => (
                        <span key={k} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400">
                          {k}={typeof v === "number" ? v.toFixed(2) : String(v)}
                        </span>
                      ))}
                    </div>
                  )}
                  {step.output !== undefined && (
                    <p className="text-xs font-mono text-indigo-600 dark:text-indigo-400 mt-2">
                      → {typeof step.output === "number" ? step.output.toFixed(4) : String(step.output)} {step.unit}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
