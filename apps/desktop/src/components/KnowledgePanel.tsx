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
      <div className="space-y-2">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-slate-400 dark:text-slate-500">共 {formulas.length} 个公式</span>
          <button
            onClick={runInfer}
            disabled={inferLoading}
            className="text-[10px] flex items-center gap-1 px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors disabled:opacity-50"
          >
            {inferLoading ? <Loader2 size={10} className="animate-spin" /> : <Calculator size={10} />}
            实时推理
          </button>
        </div>

        {inferResult && (
          <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-indigo-100 dark:border-indigo-800/30 mb-2">
            <p className="text-[10px] font-semibold text-indigo-700 dark:text-indigo-300 mb-1">推理结果</p>
            <div className="space-y-1">
              {Object.entries(inferResult.derived_params).filter(([k]) => !Object.keys(form).includes(k)).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between text-[10px]">
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
              className="w-full flex items-center justify-between p-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <div>
                <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-200">{f.name_cn}</span>
                <span className="text-[10px] text-slate-400 dark:text-slate-500 ml-2 font-mono">{f.expression}</span>
              </div>
              {expandedFormula === f.id ? <ChevronDown size={12} className="text-slate-400" /> : <ChevronRight size={12} className="text-slate-400" />}
            </button>
            {expandedFormula === f.id && (
              <div className="px-3 pb-3 space-y-2">
                {f.params.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400">参数</p>
                    <div className="flex flex-wrap gap-1">
                      {f.params.map((p) => (
                        <span key={p.name} className="inline-flex items-center px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-[10px] text-slate-600 dark:text-slate-300">
                          {p.name_cn} <span className="text-slate-400 dark:text-slate-500 ml-0.5">({p.unit})</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {f.principle && (
                  <div>
                    <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">物理原理</p>
                    <p className="text-[10px] text-slate-600 dark:text-slate-300 leading-relaxed">{f.principle}</p>
                  </div>
                )}
                {f.assumption && (
                  <div>
                    <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">适用假设</p>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-relaxed">{f.assumption}</p>
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
      <div className="space-y-2">
        {constraints.map((c) => (
          <div key={c.id} className="rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 overflow-hidden">
            <button
              onClick={() => setExpandedConstraint(expandedConstraint === c.id ? null : c.id)}
              className="w-full flex items-center justify-between p-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${c.severity === "error" ? "bg-rose-400" : c.severity === "warning" ? "bg-amber-400" : "bg-emerald-400"}`} />
                <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-200">{c.name_cn}</span>
              </div>
              {expandedConstraint === c.id ? <ChevronDown size={12} className="text-slate-400" /> : <ChevronRight size={12} className="text-slate-400" />}
            </button>
            {expandedConstraint === c.id && (
              <div className="px-3 pb-3 space-y-2">
                <div>
                  <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">物理原理</p>
                  <p className="text-[10px] text-slate-600 dark:text-slate-300 leading-relaxed">{c.principle}</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">失败解释</p>
                  <p className="text-[10px] text-rose-600 dark:text-rose-400 leading-relaxed">{c.failure_explanation_tpl}</p>
                </div>
                <div>
                  <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 mb-0.5">建议</p>
                  <p className="text-[10px] text-indigo-600 dark:text-indigo-400 leading-relaxed">{c.suggestion}</p>
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
    <div className="space-y-3">
      {!selectedResult?.derivation_chain || selectedResult.derivation_chain.length === 0 ? (
        <div className="text-center py-4">
          <p className="text-xs text-slate-400 dark:text-slate-500">选择一个匹配方案查看推导链的物理原理解释</p>
        </div>
      ) : (
        <>
          {selectedResult.reason && (
            <div className="p-2.5 rounded-lg bg-indigo-50/60 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
              <p className="text-[10px] font-semibold text-indigo-700 dark:text-indigo-300 mb-0.5">匹配理由</p>
              <p className="text-[11px] text-indigo-600 dark:text-indigo-400">{selectedResult.reason}</p>
            </div>
          )}
          <div className="space-y-2">
            {selectedResult.derivation_chain.map((step, i) => (
              <div key={i} className="relative pl-5">
                {i < (selectedResult.derivation_chain?.length ?? 0) - 1 && (
                  <div className="absolute left-[7px] top-5 bottom-[-8px] w-px bg-slate-200 dark:bg-slate-700" />
                )}
                <div className="absolute left-0 top-0.5 w-3.5 h-3.5 rounded-full bg-indigo-100 dark:bg-indigo-900/40 border border-indigo-300 dark:border-indigo-700 flex items-center justify-center">
                  <span className="text-[8px] font-bold text-indigo-600 dark:text-indigo-400">{i + 1}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                  <p className="text-[11px] font-semibold text-slate-700 dark:text-slate-200">{step.step || step.formula || "计算步骤"}</p>
                  {step.principle && (
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">{step.principle}</p>
                  )}
                  {step.assumption && (
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">假设：{step.assumption}</p>
                  )}
                  {step.inputs && Object.keys(step.inputs).length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {Object.entries(step.inputs).slice(0, 4).map(([k, v]) => (
                        <span key={k} className="text-[9px] px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400">
                          {k}={typeof v === "number" ? v.toFixed(2) : String(v)}
                        </span>
                      ))}
                    </div>
                  )}
                  {step.output !== undefined && (
                    <p className="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 mt-1">
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
