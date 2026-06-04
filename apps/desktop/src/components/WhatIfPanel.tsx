import { useState, useEffect, useRef, useCallback } from "react";
import { SlidersHorizontal, TrendingUp, Flame, Zap } from "lucide-react";
import { type UnifiedMatchResult } from "../hooks/useMatching";

interface Props {
  form: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
  onRunWhatIf: (requirements: Record<string, unknown>) => void;
  baselineResults: UnifiedMatchResult[];
  whatIfResults: UnifiedMatchResult[];
  isRunning: boolean;
}

const NUMERIC_PARAMS: Array<{ key: string; label: string; min: number; max: number; step: number }> = [
  { key: "working_distance_mm", label: "工作距离", min: 10, max: 2000, step: 10 },
  { key: "target_width_mm", label: "视场宽度", min: 1, max: 500, step: 5 },
  { key: "target_height_mm", label: "视场高度", min: 1, max: 500, step: 5 },
  { key: "pixel_size_um", label: "像素尺寸", min: 1, max: 10, step: 0.1 },
];

function getSensitivityLabel(_baseline: UnifiedMatchResult[], key: string): { label: string; icon: React.ReactNode; color: string } {
  // Simple heuristic: if changing this param by ±20% would change focal estimate significantly,
  // it's high sensitivity. For now, use fixed rules based on parameter key.
  if (key === "working_distance_mm" || key === "target_width_mm") {
    return { label: "高影响", icon: <Flame size={10} />, color: "text-rose-500 dark:text-rose-400" };
  }
  if (key === "pixel_size_um") {
    return { label: "中影响", icon: <Zap size={10} />, color: "text-amber-500 dark:text-amber-400" };
  }
  return { label: "低影响", icon: <TrendingUp size={10} />, color: "text-slate-400 dark:text-slate-500" };
}

export default function WhatIfPanel({ form, onChange, onRunWhatIf, baselineResults, whatIfResults, isRunning }: Props) {
  const [activeParam, setActiveParam] = useState<string | null>(null);
  const [sliderValue, setSliderValue] = useState<number>(0);
  const [localForm, setLocalForm] = useState<Record<string, unknown>>(form);
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const originalValueRef = useRef<number | null>(null);

  const paramDef = NUMERIC_PARAMS.find((p) => p.key === activeParam);
  const currentVal = paramDef ? Number(localForm[paramDef.key] ?? 0) : 0;

  useEffect(() => {
    setLocalForm(form);
  }, [form]);

  useEffect(() => {
    if (paramDef) {
      setSliderValue(currentVal);
      if (originalValueRef.current === null) {
        originalValueRef.current = Number(form[paramDef.key] ?? 0);
      }
    }
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
        debounceTimer.current = null;
      }
    };
  }, [activeParam, paramDef, currentVal, form]);

  const handleSliderChange = useCallback((val: number) => {
    setSliderValue(val);
    if (paramDef) {
      setLocalForm((prev) => ({ ...prev, [paramDef.key]: val }));
    }
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    debounceTimer.current = setTimeout(() => {
      onRunWhatIf({ ...localForm, [paramDef!.key]: val });
    }, 600);
  }, [paramDef, localForm, onRunWhatIf]);

  const handleBack = useCallback(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
      debounceTimer.current = null;
    }
    if (paramDef && originalValueRef.current !== null) {
      onChange(paramDef.key, originalValueRef.current);
      setLocalForm((prev) => ({ ...prev, [paramDef.key]: originalValueRef.current }));
    }
    setActiveParam(null);
    originalValueRef.current = null;
  }, [paramDef, onChange]);

  const diffCount = whatIfResults.length - baselineResults.length;

  return (
    <div className="mt-5 p-4 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
      <div className="flex items-center gap-2 mb-3">
        <SlidersHorizontal size={14} className="text-indigo-500" />
        <h3 className="text-xs font-bold text-slate-700 dark:text-slate-200">参数灵敏度分析</h3>
      </div>

      {!activeParam ? (
        <div className="space-y-2">
          {NUMERIC_PARAMS.map((p) => {
            const val = Number(form[p.key] ?? 0);
            const sens = getSensitivityLabel(baselineResults, p.key);
            return (
              <button
                key={p.key}
                onClick={() => setActiveParam(p.key)}
                className="w-full flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-700 transition-colors text-left"
              >
                <div>
                  <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-200">{p.label}</span>
                  <span className="text-[11px] text-slate-400 dark:text-slate-500 ml-2">{val}{p.key === "pixel_size_um" ? "μm" : "mm"}</span>
                </div>
                <span className={`flex items-center gap-1 text-[10px] font-medium ${sens.color}`}>
                  {sens.icon}
                  {sens.label}
                </span>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-700 dark:text-slate-200">{paramDef?.label}</span>
            <button
              onClick={handleBack}
              className="text-[10px] text-slate-400 dark:text-slate-500 hover:text-indigo-500"
            >
              返回
            </button>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 tabular-nums w-10 text-right">{paramDef?.min}</span>
            <input
              type="range"
              min={paramDef?.min}
              max={paramDef?.max}
              step={paramDef?.step}
              value={sliderValue}
              onChange={(e) => handleSliderChange(Number(e.target.value))}
              className="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full appearance-none cursor-pointer accent-indigo-500"
            />
            <span className="text-[10px] text-slate-400 dark:text-slate-500 tabular-nums w-10">{paramDef?.max}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400 tabular-nums">
              {sliderValue.toFixed(paramDef?.step && paramDef.step < 1 ? 2 : 0)}{paramDef?.key === "pixel_size_um" ? "μm" : "mm"}
            </span>
            {isRunning ? (
              <span className="text-[10px] text-indigo-500 animate-pulse">计算中...</span>
            ) : (
              <span className={`text-[10px] font-medium ${diffCount > 0 ? "text-emerald-500" : diffCount < 0 ? "text-rose-500" : "text-slate-400"}`}>
                {diffCount > 0 ? `+${diffCount} 个结果` : diffCount < 0 ? `${diffCount} 个结果` : "结果数量不变"}
              </span>
            )}
          </div>

          {whatIfResults.length > 0 && baselineResults.length > 0 && (
            <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
              <p className="text-[10px] text-slate-500 dark:text-slate-500 mb-1">Top 3 对比</p>
              <div className="space-y-1">
                {whatIfResults.slice(0, 3).map((r) => {
                  const baseline = baselineResults.find((b) => b.lens_id === r.lens_id && b.detector_id === r.detector_id);
                  const scoreDiff = baseline ? r.score - baseline.score : 0;
                  return (
                    <div key={`${r.lens_id}-${r.detector_id}`} className="flex items-center justify-between text-[10px]">
                      <span className="text-slate-600 dark:text-slate-300 truncate max-w-[120px]">{r.lens_model}</span>
                      <span className={`tabular-nums font-medium ${scoreDiff > 0.01 ? "text-emerald-500" : scoreDiff < -0.01 ? "text-rose-500" : "text-slate-400"}`}>
                        {r.score.toFixed(2)}
                        {Math.abs(scoreDiff) > 0.01 && ` (${scoreDiff > 0 ? "+" : ""}${scoreDiff.toFixed(2)})`}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
