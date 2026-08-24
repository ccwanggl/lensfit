import { useState, useMemo } from "react";
import { Play, RotateCcw, TrendingUp, BookOpen } from "lucide-react";
import { listKnowledgeFormulas, type KnowledgeFormula } from "../utils/api";
import { useQuery } from "@tanstack/react-query";
import { toast } from "../hooks/useToast";

/* ─── Frontend calculators (mirror backend) ─── */
const CALC: Record<string, (vals: Record<string, number>) => Record<string, number>> = {
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
    return { coverage_ratio: sd === 0 ? 0 : Math.min(1, (v.image_circle / sd) ** 2) };
  },
  depth_of_field: (v) => {
    const H = (v.focal ** 2) / (v.f_number * v.coc_diameter) + v.focal;
    const near = (H * v.focus_distance) / (H + v.focus_distance);
    const far = v.focus_distance >= H ? Infinity : (H * v.focus_distance) / (H - v.focus_distance);
    return { near_limit: near, far_limit: far, dof: far === Infinity ? Infinity : far - near };
  },
  pixel_accuracy: (v) => ({ pixel_accuracy_mm: v.pixel_size_um / (1000 * v.magnification) }),
};

const PRESETS: Record<string, Record<string, Record<string, number>>> = {
  thin_lens_imaging: {
    "工业检测 50mm FOV": { wd: 200, sensor: 8.8, fov: 50 },
    "摄影 人像": { wd: 2500, sensor: 36, fov: 800 },
    "显微 40×": { wd: 10, sensor: 11, fov: 0.5 },
  },
  magnification: {
    "工业 0.5×": { focal: 25, wd: 150 },
    "摄影 1:1 微距": { focal: 100, wd: 200 },
    "显微 40×": { focal: 4, wd: 10.25 },
  },
  nyquist_sampling: {
    "工业相机 3.45μm": { pixel_size_um: 3.45, lens_mtf50_lpmm: 80, na: 0, wavelength_um: 0.55 },
    "手机 1.2μm": { pixel_size_um: 1.2, lens_mtf50_lpmm: 60, na: 0, wavelength_um: 0.55 },
    "显微镜 NA0.65": { pixel_size_um: 3.45, lens_mtf50_lpmm: 0, na: 0.65, wavelength_um: 0.55 },
  },
  depth_of_field: {
    "人像 f/1.4": { focal: 85, f_number: 1.4, coc_diameter: 0.03, focus_distance: 2500 },
    "风景 f/8": { focal: 24, f_number: 8, coc_diameter: 0.03, focus_distance: 2000 },
    "微距 f/2.8": { focal: 100, f_number: 2.8, coc_diameter: 0.03, focus_distance: 300 },
  },
};

const LEARN_CHAPTER: Record<string, string> = {
  thin_lens_imaging: "第2章 几何光学",
  magnification: "第2章 几何光学",
  fov_from_focal: "第2章 几何光学",
  afov_from_focal: "第2章 几何光学",
  nyquist_sampling: "第4章 传感器",
  sensor_coverage: "第5章 匹配基础",
  depth_of_field: "第3章 镜头参数",
  pixel_accuracy: "第5章 匹配基础",
};

function generateChartData(
  formulaId: string,
  inputs: Record<string, number>,
  sweepParam: string,
  sweepRange: [number, number],
  steps = 50
): { x: number; y: number }[] {
  const calc = CALC[formulaId];
  if (!calc) return [];
  const data: { x: number; y: number }[] = [];
  const outputKey = Object.keys(calc({ ...inputs, [sweepParam]: inputs[sweepParam] ?? 0 }))[0];
  for (let i = 0; i <= steps; i++) {
    const x = sweepRange[0] + (sweepRange[1] - sweepRange[0]) * (i / steps);
    try {
      const r = calc({ ...inputs, [sweepParam]: x });
      const y = r[outputKey];
      if (Number.isFinite(y)) data.push({ x, y });
    } catch { /* skip invalid */ }
  }
  return data;
}

export default function FormulaPlayground() {
  const { data } = useQuery({
    queryKey: ["playgroundFormulas"],
    queryFn: () => listKnowledgeFormulas("all"),
    staleTime: Infinity,
  });

  const formulas = useMemo(() => (data?.items ?? []).filter((f) => CALC[f.id]), [data]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [inputs, setInputs] = useState<Record<string, number>>({});
  const [result, setResult] = useState<Record<string, number> | null>(null);
  const [sweepParam, setSweepParam] = useState<string>("");
  const [chartData, setChartData] = useState<{ x: number; y: number }[]>([]);

  const selected = formulas.find((f) => f.id === selectedId);

  const applyPreset = (presetValues: Record<string, number>) => {
    setInputs(presetValues);
    if (selected) {
      compute(selected, presetValues);
    }
  };

  const compute = (formula: KnowledgeFormula, vals = inputs) => {
    const calc = CALC[formula.id];
    if (!calc) return;
    try {
      const fullVals: Record<string, number> = {};
      for (const p of formula.params) {
        fullVals[p.name] = vals[p.name] ?? 0;
      }
      const out = calc(fullVals);
      setResult(out);

      // Auto-generate chart if sweep param selected
      if (sweepParam && fullVals[sweepParam] !== undefined) {
        const base = fullVals[sweepParam];
        const range: [number, number] = [base * 0.2, base * 2];
        setChartData(generateChartData(formula.id, fullVals, sweepParam, range));
      } else {
        setChartData([]);
      }
    } catch {
      toast("error", "计算错误", "输入值可能无效");
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
          <TrendingUp size={16} />
        </div>
        <div>
          <h2 className="text-sm font-bold text-slate-900 dark:text-slate-100">公式游乐场</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">输入参数，实时观察公式行为</p>
        </div>
      </div>

      {/* Formula selector */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {formulas.map((f) => (
          <button
            key={f.id}
            onClick={() => { setSelectedId(f.id); setInputs({}); setResult(null); setChartData([]); }}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
              selectedId === f.id
                ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800/40"
                : "bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700"
            }`}
          >
            {f.name_cn}
          </button>
        ))}
      </div>

      {!selected && (
        <div className="flex-1 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm">
          选择一个公式开始探索
        </div>
      )}

      {selected && (
        <div className="flex-1 flex gap-4 min-h-0">
          {/* Left: inputs */}
          <div className="w-64 shrink-0 space-y-3 overflow-y-auto pr-1">
            {/* Presets */}
            {PRESETS[selected.id] && (
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">预设场景</p>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(PRESETS[selected.id]).map(([name, vals]) => (
                    <button
                      key={name}
                      onClick={() => applyPreset(vals)}
                      className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-700 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                    >
                      {name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Inputs */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">参数</p>
              {selected.params.map((p) => (
                <div key={p.name}>
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-xs text-slate-700 dark:text-slate-200">{p.name_cn}</span>
                    <span className="text-xs text-slate-400">{p.unit}</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={p.unit === "mm" ? 1000 : p.unit === "μm" || p.unit === "um" ? 20 : p.unit === "" && (p.name.includes("na") || p.name.includes("mtf")) ? 2 : 100}
                    step="any"
                    value={inputs[p.name] ?? 0}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value);
                      setInputs((prev) => ({ ...prev, [p.name]: v }));
                    }}
                    className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full appearance-none cursor-pointer accent-indigo-500"
                  />
                  <div className="flex items-center gap-1 mt-0.5">
                    <input
                      type="number"
                      step="any"
                      value={inputs[p.name] ?? 0}
                      onChange={(e) => {
                        const v = e.target.value === "" ? 0 : parseFloat(e.target.value);
                        setInputs((prev) => ({ ...prev, [p.name]: v }));
                      }}
                      className="flex-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md px-2 py-0.5 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-400"
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-1">
              <button
                onClick={() => compute(selected)}
                className="flex-1 py-1.5 rounded-md bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors flex items-center justify-center gap-1"
              >
                <Play size={12} />
                计算
              </button>
              <button
                onClick={() => { setInputs({}); setResult(null); setChartData([]); }}
                className="px-2 py-1.5 rounded-md bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                title="重置" aria-label="重置"
              >
                <RotateCcw size={12} />
              </button>
            </div>

            {/* Sweep selector */}
            {selected.params.length > 1 && (
              <div className="pt-1">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">扫描参数（绘图）</p>
                <select
                  value={sweepParam}
                  onChange={(e) => setSweepParam(e.target.value)}
                  className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md px-2 py-1 text-xs text-slate-800 dark:text-slate-200"
                >
                  <option value="">不绘图</option>
                  {selected.params.map((p) => (
                    <option key={p.name} value={p.name}>{p.name_cn}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Learn link */}
            {LEARN_CHAPTER[selected.id] && (
              <div className="flex items-center gap-1.5 pt-1">
                <BookOpen size={11} className="text-emerald-500" />
                <span className="text-xs text-emerald-700 dark:text-emerald-400">{LEARN_CHAPTER[selected.id]}</span>
              </div>
            )}
          </div>

          {/* Right: results + chart */}
          <div className="flex-1 min-w-0 space-y-3 overflow-y-auto">
            {/* Results */}
            {result && (
              <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 space-y-2">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">计算结果</p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(result).map(([k, v]) => (
                    <div key={k} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-700/50">
                      <p className="text-xs text-slate-500 dark:text-slate-400 uppercase">{k}</p>
                      <p className="text-sm font-mono font-bold text-slate-800 dark:text-slate-200">
                        {Number.isNaN(v) ? "无效" : Number.isFinite(v) ? (Math.abs(v) > 10000 ? v.toExponential(3) : v.toFixed(v % 1 === 0 ? 0 : 4)) : "∞"}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Chart */}
            {chartData.length > 0 && (
              <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">参数扫描曲线</p>
                <svg viewBox="0 0 400 150" className="w-full h-32">
                  {/* Axes */}
                  <line x1="40" y1="130" x2="390" y2="130" stroke="currentColor" className="text-slate-300 dark:text-slate-600" strokeWidth={1} />
                  <line x1="40" y1="10" x2="40" y2="130" stroke="currentColor" className="text-slate-300 dark:text-slate-600" strokeWidth={1} />
                  {/* Data path */}
                  {(() => {
                    const xs = chartData.map((d) => d.x);
                    const ys = chartData.map((d) => d.y).filter(Number.isFinite);
                    const minX = Math.min(...xs);
                    const maxX = Math.max(...xs);
                    const minY = Math.min(...ys);
                    const maxY = Math.max(...ys);
                    const rangeY = maxY - minY || 1;
                    const points = chartData
                      .filter((d) => Number.isFinite(d.y))
                      .map((d) => {
                        const px = 40 + ((d.x - minX) / (maxX - minX || 1)) * 350;
                        const py = 130 - ((d.y - minY) / rangeY) * 110;
                        return `${px},${py}`;
                      })
                      .join(" ");
                    return (
                      <>
                        <polyline
                          fill="none"
                          stroke="#6366f1"
                          strokeWidth={2}
                          points={points}
                        />
                        {/* Min/Max labels */}
                        <text x="45" y="140" fontSize="8" fill="currentColor" className="text-slate-400 dark:text-slate-500">{minX.toFixed(1)}</text>
                        <text x="350" y="140" fontSize="8" fill="currentColor" className="text-slate-400 dark:text-slate-500">{maxX.toFixed(1)}</text>
                        <text x="10" y="135" fontSize="8" fill="currentColor" className="text-slate-400 dark:text-slate-500">{minY.toFixed(2)}</text>
                        <text x="10" y="15" fontSize="8" fill="currentColor" className="text-slate-400 dark:text-slate-500">{maxY.toFixed(2)}</text>
                      </>
                    );
                  })()}
                </svg>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
