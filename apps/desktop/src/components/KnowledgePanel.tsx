import { useState, useEffect, useCallback } from "react";
import { ChevronDown, ChevronRight, Calculator, Loader2, BookOpen, Play, GraduationCap, Eye } from "lucide-react";
import { listKnowledgeFormulas, listKnowledgeConstraints, knowledgeInfer, type KnowledgeFormula, type KnowledgeConstraint } from "../utils/api";
import { toast } from "../hooks/useToast";
import { useLearningMode } from "../contexts/LearningModeContext";

/* ─── Frontend formula calculators (mirrors backend logic) ─── */
const FORMULA_CALCULATORS: Record<string, (vals: Record<string, number>) => Record<string, number>> = {
  thin_lens_imaging: (v) => ({ focal: (v.wd * v.sensor) / (v.fov + v.sensor) }),
  magnification: (v) => ({ magnification: v.focal / (v.wd - v.focal) }),
  fov_from_focal: (v) => ({ fov_w: (v.wd * v.sensor) / v.focal - v.sensor }),
  afov_from_focal: (v) => ({ afov_h: (360 / Math.PI) * Math.atan(v.sensor / (2 * v.focal)) }),
  nyquist_sampling: (v) => {
    const fn = 1000 / (2 * v.pixel_size_um);
    const fl = v.lens_mtf50_lpmm || (v.na ? (1000 * v.na) / (0.61 * (v.wavelength_um || 0.55)) : 0);
    return { sensor_nyquist_lpmm: fn, optical_limit_lpmm: fl, oversampling_ratio: fl / fn };
  },
  sensor_coverage: (v) => {
    const sd = Math.sqrt(v.sensor_w ** 2 + v.sensor_h ** 2);
    const ratio = sd === 0 ? 0 : Math.min(1, (v.image_circle / sd) ** 2);
    return { coverage_ratio: ratio, fully_covered: v.image_circle >= sd ? 1 : 0 };
  },
  depth_of_field: (v) => {
    const H = (v.focal ** 2) / (v.f_number * v.coc_diameter) + v.focal;
    const near = (H * v.focus_distance) / (H + v.focus_distance);
    const far = v.focus_distance >= H ? Infinity : (H * v.focus_distance) / (H - v.focus_distance);
    return { near_limit: near, far_limit: far, dof: far === Infinity ? Infinity : far - near };
  },
  pixel_accuracy: (v) => ({ pixel_accuracy_mm: v.pixel_size_um / (1000 * v.magnification) }),
};

const LEARN_LINKS: Record<string, string> = {
  thin_lens_imaging: "docs/learning/02-geometric-optics.md",
  magnification: "docs/learning/02-geometric-optics.md",
  fov_from_focal: "docs/learning/02-geometric-optics.md",
  afov_from_focal: "docs/learning/02-geometric-optics.md",
  nyquist_sampling: "docs/learning/04-sensors.md",
  sensor_coverage: "docs/learning/05-matching-basics.md",
  depth_of_field: "docs/learning/03-lens-parameters.md",
  pixel_accuracy: "docs/learning/05-matching-basics.md",
};

/** Plain-language intuition for non-experts. */
const FORMULA_INTUITIONS: Record<string, string> = {
  thin_lens_imaging: "工作距离越远、视场越大，需要的焦距就越长；传感器越大，同样视场下需要的焦距也越短。",
  magnification: "放大倍率就是像比物大多少倍。工作距离接近焦距时倍率会急剧上升。",
  fov_from_focal: "焦距越短，能拍到的范围越广；焦距越长，视野越窄、放大越明显。",
  afov_from_focal: "传感器尺寸不变时，焦距越短，视角越宽，适合广角场景。",
  nyquist_sampling: "像素太疏会漏掉细节（混叠）。采样频率最好是被采样信号频率的 2 倍以上。",
  sensor_coverage: "镜头的像圈必须覆盖住传感器，否则照片四角会变暗。",
  depth_of_field: "光圈越小、焦距越短、对焦越远，画面中清晰的范围就越大。",
  pixel_accuracy: "放大倍率越大，每个像素代表的物理尺寸越小，测量精度越高。",
};

/** Link formulas to the interactive Concept Explorer diagrams. */
const FORMULA_VIZ_LINKS: Record<string, string> = {
  thin_lens_imaging: "薄透镜光线追踪",
  magnification: "薄透镜光线追踪",
  fov_from_focal: "传感器覆盖与像圈",
  afov_from_focal: "传感器覆盖与像圈",
  nyquist_sampling: "奈奎斯特采样",
  sensor_coverage: "传感器覆盖与像圈",
  depth_of_field: "薄透镜光线追踪",
  pixel_accuracy: "奈奎斯特采样",
};

/* ─── Lightweight LaTeX → HTML renderer (no KaTeX) ─── */
const GREEK: Record<string, string> = {
  alpha: "α", beta: "β", gamma: "γ", delta: "δ", epsilon: "ε",
  theta: "θ", lambda: "λ", mu: "μ", pi: "π", rho: "ρ", sigma: "σ",
  phi: "φ", omega: "ω",
};

/** Upright math operators and symbols (not italicized). */
const UPRIGHT: Record<string, string> = {
  cdot: "·",
  times: "×",
  div: "÷",
  pm: "±",
  sim: "~",
  approx: "≈",
  neq: "≠",
  leq: "≤",
  geq: "≥",
  infty: "∞",
  arctan: "arctan",
  arctg: "arctan",
  arcsin: "arcsin",
  arccos: "arccos",
  sin: "sin",
  cos: "cos",
  tan: "tan",
  ln: "ln",
  log: "log",
  exp: "exp",
};

/** Functions rendered in italic (variables / multi-letter identifiers). */
const ITALIC_FN = new Set([
  "beta", "f", "H", "FOV", "WD", "AFOV", "acc", "coverage_ratio",
]);

function findBrace(s: string, start: number): number {
  let depth = 1;
  for (let i = start + 1; i < s.length; i++) {
    if (s[i] === "{") depth++;
    else if (s[i] === "}") {
      depth--;
      if (depth === 0) return i;
    }
  }
  return -1;
}

function latexToHtml(src: string): string {
  function parse(s: string): string {
    let out = "";
    let i = 0;
    while (i < s.length) {
      if (s[i] === "\\") {
        const m = s.slice(i + 1).match(/^([a-zA-Z]+)/);
        if (m) {
          const cmd = m[1];
          const end = i + 1 + cmd.length;

          if (cmd === "frac") {
            const a1s = s.indexOf("{", end);
            if (a1s === -1) { out += s.slice(i); break; }
            const a1e = findBrace(s, a1s);
            const a2s = s.indexOf("{", a1e + 1);
            if (a2s === -1) { out += s.slice(i); break; }
            const a2e = findBrace(s, a2s);
            const num = parse(s.slice(a1s + 1, a1e));
            const den = parse(s.slice(a2s + 1, a2e));
            out += `<span class="latex-frac"><span class="latex-num">${num}</span><span class="latex-den">${den}</span></span>`;
            i = a2e + 1;
            continue;
          }

          if (cmd === "text") {
            const ts = s.indexOf("{", end);
            const te = findBrace(s, ts);
            out += `<span class="latex-text">${parse(s.slice(ts + 1, te))}</span>`;
            i = te + 1;
            continue;
          }

          if (cmd === "left" || cmd === "right") {
            const next = s[end];
            if (next === "(" || next === "[" || next === "{" || next === ")" || next === "]" || next === "}") {
              out += `<span class="latex-paren">${next}</span>`;
              i = end + 1;
              continue;
            }
          }

          if (GREEK[cmd]) {
            out += `<span class="latex-greek">${GREEK[cmd]}</span>`;
            i = end;
            continue;
          }

          if (UPRIGHT[cmd] !== undefined) {
            out += `<span class="latex-up">${UPRIGHT[cmd]}</span>`;
            i = end;
            continue;
          }

          const cls = ITALIC_FN.has(cmd) ? "latex-fn" : "latex-up";
          out += `<span class="${cls}">${cmd}</span>`;
          i = end;
          continue;
        }

        const next = s[i + 1];
        if (next === ";" || next === ",") {
          out += "&nbsp;";
          i += 2;
          continue;
        }
        if (next === " " || next === "\t") {
          out += " ";
          i += 2;
          continue;
        }
        if (next === "(" || next === ")" || next === "[" || next === "]" || next === "{" || next === "}") {
          out += `<span class="latex-paren">${next}</span>`;
          i += 2;
          continue;
        }
      }

      if (s[i] === "^") {
        if (s[i + 1] === "{") {
          const e = findBrace(s, i + 1);
          out += `<sup>${parse(s.slice(i + 2, e))}</sup>`;
          i = e + 1;
        } else {
          out += `<sup>${s[i + 1]}</sup>`;
          i += 2;
        }
        continue;
      }

      if (s[i] === "_") {
        if (s[i + 1] === "{") {
          const e = findBrace(s, i + 1);
          out += `<sub>${parse(s.slice(i + 2, e))}</sub>`;
          i = e + 1;
        } else {
          out += `<sub>${s[i + 1]}</sub>`;
          i += 2;
        }
        continue;
      }

      if (s[i] === "+" || s[i] === "-" || s[i] === "=") {
        out += `<span class="latex-op">${s[i]}</span>`;
        i++;
        continue;
      }

      out += s[i];
      i++;
    }
    return out;
  }

  return parse(src);
}

/* ─── Interactive formula calculator sub-component ─── */
function FormulaCalculator({ formula }: { formula: KnowledgeFormula }) {
  const calc = FORMULA_CALCULATORS[formula.id];
  const [inputs, setInputs] = useState<Record<string, number>>({});
  const [result, setResult] = useState<Record<string, number> | null>(null);

  if (!calc) return null;

  const handleCompute = () => {
    try {
      const vals: Record<string, number> = {};
      for (const p of formula.params) {
        vals[p.name] = inputs[p.name] ?? 0;
      }
      const out = calc(vals);
      setResult(out);
    } catch {
      toast("error", "计算错误", "请检查输入值是否有效");
    }
  };

  return (
    <div className="rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-3 space-y-2.5">
      <div className="flex items-center gap-1.5">
        <Play size={12} className="text-indigo-500" />
        <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-400">互动计算</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {formula.params.map((p) => (
          <div key={p.name} className="flex items-center gap-1.5">
            <span className="text-xs text-slate-600 dark:text-slate-300 w-16 truncate" title={p.name_cn}>{p.name_cn}</span>
            <input
              type="number"
              step="any"
              placeholder={p.unit || "值"}
              className="flex-1 min-w-0 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-md px-2 py-1 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-400"
              value={inputs[p.name] ?? ""}
              onChange={(e) => {
                const v = e.target.value;
                setInputs((prev) => ({ ...prev, [p.name]: v === "" ? 0 : parseFloat(v) }));
              }}
            />
            <span className="text-xs text-slate-400 dark:text-slate-500 w-8">{p.unit}</span>
          </div>
        ))}
      </div>
      <button
        onClick={handleCompute}
        className="w-full py-1.5 rounded-md bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 text-xs font-semibold hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors flex items-center justify-center gap-1"
      >
        <Calculator size={12} />
        计算
      </button>
      {result && (
        <div className="space-y-1 pt-1 border-t border-slate-200 dark:border-slate-700">
          {Object.entries(result).map(([k, v]) => (
            <div key={k} className="flex items-center justify-between text-xs">
              <span className="text-slate-600 dark:text-slate-300">{k}</span>
              <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                {Number.isNaN(v) ? "无效" : Number.isFinite(v) ? (Math.abs(v) > 10000 ? v.toExponential(3) : v.toFixed(v % 1 === 0 ? 0 : 4)) : "∞"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

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
  const { learningMode } = useLearningMode();

  useEffect(() => {
    setLoading(true);
    Promise.all([
      listKnowledgeFormulas(domain).then((d) => setFormulas(d.items ?? [])).catch(() => toast("error", "加载失败", "无法获取公式库")),
      listKnowledgeConstraints().then((d) => setConstraints(d.items ?? [])).catch(() => toast("error", "加载失败", "无法获取约束库")),
    ]).finally(() => setLoading(false));
  }, [domain]);

  // In learning mode, auto-expand the first formula that has a learning link
  useEffect(() => {
    if (learningMode && formulas.length > 0 && !expandedFormula) {
      const firstLearnable = formulas.find((f) => LEARN_LINKS[f.id]);
      if (firstLearnable) {
        setExpandedFormula(firstLearnable.id);
      }
    }
  }, [learningMode, formulas, expandedFormula]);

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
      <div className="flex items-center justify-center py-6">
        <Loader2 size={16} className="animate-spin text-indigo-500" />
      </div>
    );
  }

  if (activeTab === "formulas") {
    return (
      <div className="space-y-3">
        <style>{`
          .latex-formula {
            font-family: "Latin Modern Math", "STIX Two Math", "Cambria Math", "Times New Roman", "Noto Serif CJK SC", serif;
            font-size: 1.15rem;
            line-height: 1.9;
            letter-spacing: 0.01em;
          }
          .latex-formula .latex-frac {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            vertical-align: middle;
            margin: 0 0.25em;
            font-size: 0.96em;
          }
          .latex-formula .latex-num,
          .latex-formula .latex-den {
            display: inline-block;
            min-width: 1.1em;
            padding: 0.15em 0.55em;
            text-align: center;
            line-height: 1.35;
          }
          .latex-formula .latex-num {
            border-bottom: 1.5px solid currentColor;
          }
          .latex-formula .latex-den {
            padding-top: 0.3em;
          }
          .latex-formula .latex-text {
            font-style: normal;
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 0.78em;
          }
          .latex-formula .latex-fn {
            font-style: italic;
            padding: 0 0.04em;
          }
          .latex-formula .latex-up {
            font-style: normal;
            padding: 0 0.04em;
          }
          .latex-formula .latex-greek {
            font-style: italic;
            padding: 0 0.04em;
          }
          .latex-formula .latex-paren {
            padding: 0 0.08em;
          }
          .latex-formula .latex-op {
            margin: 0 0.18em;
          }
          .latex-formula sup,
          .latex-formula sub {
            font-size: 0.72em;
            line-height: 0;
            position: relative;
            vertical-align: baseline;
          }
          .latex-formula sup { top: -0.45em; }
          .latex-formula sub { top: 0.25em; }
        `}</style>

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
            <p className="text-xs font-bold text-indigo-700 dark:text-indigo-300 mb-2">推理结果</p>
            <div className="space-y-1.5">
              {Object.entries(inferResult.derived_params).filter(([k]) => !Object.keys(form).includes(k)).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 dark:text-slate-300">{k}</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200">{typeof v === "number" ? v.toFixed(3) : String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {formulas.map((f) => (
          <div key={f.id} className={`rounded-lg bg-white dark:bg-slate-800 border overflow-hidden ${learningMode && LEARN_LINKS[f.id] ? "border-emerald-200 dark:border-emerald-800/40" : "border-slate-100 dark:border-slate-700"}`}>
            <button
              onClick={() => setExpandedFormula(expandedFormula === f.id ? null : f.id)}
              className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-800 dark:text-slate-100">{f.name_cn}</span>
                {learningMode && LEARN_LINKS[f.id] && (
                  <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400">
                    <GraduationCap size={10} />
                    可学习
                  </span>
                )}
              </div>
              {expandedFormula === f.id ? <ChevronDown size={16} className="text-slate-500 shrink-0" /> : <ChevronRight size={16} className="text-slate-500 shrink-0" />}
            </button>
            {expandedFormula === f.id && (
              <div className="px-3 pb-3 space-y-3">
                {/* LaTeX formula — centered, large */}
                <div
                  className="latex-formula py-4 px-4 flex justify-center overflow-x-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 text-slate-800 dark:text-slate-100 shadow-sm"
                  dangerouslySetInnerHTML={{ __html: latexToHtml(f.latex || f.expression) }}
                />

                {/* Plain-language intuition for non-experts */}
                {FORMULA_INTUITIONS[f.id] && (
                  <div className="flex items-start gap-2 p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-900/15 border border-indigo-100 dark:border-indigo-800/20">
                    <Eye size={14} className="text-indigo-500 shrink-0 mt-0.5" />
                    <p className="text-xs text-indigo-700 dark:text-indigo-300 leading-relaxed">
                      <span className="font-semibold">一句话理解：</span>
                      {FORMULA_INTUITIONS[f.id]}
                    </p>
                  </div>
                )}

                {/* Interactive calculator */}
                {FORMULA_CALCULATORS[f.id] && (
                  <FormulaCalculator formula={f} />
                )}

                {f.params.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-xs font-bold text-slate-600 dark:text-slate-300">参数</p>
                    <div className="flex flex-wrap gap-1.5">
                      {f.params.map((p) => (
                        <span key={p.name} className="inline-flex items-center px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-700 text-xs text-slate-700 dark:text-slate-200">
                          {p.name_cn} <span className="text-slate-500 dark:text-slate-400 ml-0.5">({p.unit})</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {f.principle && (
                  <div>
                    <p className="text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">物理原理</p>
                    <p className="text-xs text-slate-700 dark:text-slate-200 leading-relaxed">{f.principle}</p>
                  </div>
                )}
                {f.assumption && (
                  <div>
                    <p className="text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">适用假设</p>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{f.assumption}</p>
                  </div>
                )}

                {/* Link to learning chapter */}
                {LEARN_LINKS[f.id] && (
                  <div className={`flex items-center gap-1.5 p-2 rounded-lg ${learningMode ? "bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800/30" : "pt-1"}`}>
                    <BookOpen size={12} className="text-emerald-500" />
                    <span className="text-xs text-emerald-700 dark:text-emerald-400">
                      相关学习章节：{LEARN_LINKS[f.id].includes("02") ? "几何光学" : LEARN_LINKS[f.id].includes("03") ? "镜头参数" : LEARN_LINKS[f.id].includes("04") ? "传感器" : "匹配基础"}
                    </span>
                  </div>
                )}

                {/* Link to interactive concept explorer */}
                {FORMULA_VIZ_LINKS[f.id] && (
                  <div className="flex items-center gap-1.5 pt-1">
                    <Eye size={12} className="text-indigo-500" />
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      可在<span className="font-medium text-indigo-600 dark:text-indigo-400">“概念图解”</span>页查看「{FORMULA_VIZ_LINKS[f.id]}」的交互演示
                    </span>
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
                <span className="text-sm font-bold text-slate-800 dark:text-slate-100">{c.name_cn}</span>
              </div>
              {expandedConstraint === c.id ? <ChevronDown size={16} className="text-slate-500 shrink-0" /> : <ChevronRight size={16} className="text-slate-500 shrink-0" />}
            </button>
            {expandedConstraint === c.id && (
              <div className="px-3 pb-3 space-y-3">
                <div>
                  <p className="text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">物理原理</p>
                  <p className="text-xs text-slate-700 dark:text-slate-200 leading-relaxed">{c.principle}</p>
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">失败解释</p>
                  <p className="text-xs text-rose-700 dark:text-rose-300 leading-relaxed">{c.failure_explanation_tpl}</p>
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-600 dark:text-slate-300 mb-1">建议</p>
                  <p className="text-xs text-indigo-700 dark:text-indigo-300 leading-relaxed">{c.suggestion}</p>
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
          <p className="text-sm text-slate-500 dark:text-slate-400">选择一个匹配方案查看推导链的物理原理解释</p>
        </div>
      ) : (
        <>
          {selectedResult.reason && (
            <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
              <p className="text-xs font-bold text-indigo-700 dark:text-indigo-300 mb-1">匹配理由</p>
              <p className="text-sm text-indigo-700 dark:text-indigo-300">{selectedResult.reason}</p>
            </div>
          )}
          <div className="space-y-3">
            {selectedResult.derivation_chain.map((step, i) => (
              <div key={i} className="relative pl-6">
                {i < (selectedResult.derivation_chain?.length ?? 0) - 1 && (
                  <div className="absolute left-[9px] top-6 bottom-[-12px] w-px bg-slate-200 dark:bg-slate-700" />
                )}
                <div className="absolute left-0 top-1 w-4 h-4 rounded-full bg-indigo-100 dark:bg-indigo-900/40 border border-indigo-300 dark:border-indigo-700 flex items-center justify-center">
                  <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">{i + 1}</span>
                </div>
                <div className="p-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                  <p className="text-sm font-bold text-slate-800 dark:text-slate-100">{step.step || step.formula || "计算步骤"}</p>
                  {step.principle && (
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-1.5 leading-relaxed">{step.principle}</p>
                  )}
                  {step.assumption && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">假设：{step.assumption}</p>
                  )}
                  {step.inputs && Object.keys(step.inputs).length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {Object.entries(step.inputs).slice(0, 4).map(([k, v]) => (
                        <span key={k} className="text-xs px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                          {k}={typeof v === "number" ? v.toFixed(2) : String(v)}
                        </span>
                      ))}
                    </div>
                  )}
                  {step.output !== undefined && (
                    <p className="text-xs font-mono text-indigo-700 dark:text-indigo-300 mt-2">
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
