import { AlertTriangle, Lightbulb, SlidersHorizontal } from "lucide-react";
import { type FilterDiagnosticItem } from "../hooks/useMatching";

interface Props {
  diagnostics: FilterDiagnosticItem[];
  onAdjustParam?: (name: string, value: unknown) => void;
}

const STAGE_LABELS: Record<string, string> = {
  index_pre_filter: "索引预筛选",
  quick_hard_filter: "硬约束剪枝",
  domain_constraints: "领域约束",
};

const REASON_LABELS: Record<string, string> = {
  image_circle_too_small: "像圆不足",
  mount_incompatible: "接口不兼容",
  wd_out_of_range: "工作距离超出范围",
};

export default function DiagnosticsPanel({ diagnostics, onAdjustParam }: Props) {
  if (!diagnostics || diagnostics.length === 0) return null;

  const hasZeroResult = diagnostics.every((d) => d.after_count === 0);

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 p-4 bg-amber-50/60 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800/30 rounded-xl">
        <AlertTriangle size={18} className="text-amber-500 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-bold text-amber-800 dark:text-amber-300">未找到匹配方案</p>
          <p className="text-xs text-amber-600 dark:text-amber-400 mt-0.5">
            系统在 {diagnostics.length} 个过滤阶段中逐步排除了所有候选，诊断如下：
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {diagnostics.map((d, i) => (
          <div
            key={i}
            className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-200">
                {STAGE_LABELS[d.stage] || d.stage}
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400 tabular-nums">
                {d.before_count} → {d.after_count}
              </span>
            </div>

            {d.after_count === 0 && d.before_count > 0 && (
              <div className="w-full h-1.5 bg-rose-100 dark:bg-rose-900/30 rounded-full overflow-hidden mb-2">
                <div className="h-full bg-rose-400 rounded-full w-full" />
              </div>
            )}

            {Object.entries(d.rejected_reasons).length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {Object.entries(d.rejected_reasons).map(([reason, count]) => (
                  <span
                    key={reason}
                    className="inline-flex items-center px-2 py-0.5 rounded-md bg-rose-50 dark:bg-rose-900/20 text-xs font-medium text-rose-600 dark:text-rose-400"
                  >
                    {REASON_LABELS[reason] || reason}: {count}
                  </span>
                ))}
              </div>
            )}

            {d.suggestion && (
              <div className="flex items-start gap-1.5">
                <Lightbulb size={13} className="text-amber-500 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  {d.suggestion}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {hasZeroResult && onAdjustParam && (
        <div className="p-3 rounded-[10px] bg-indigo-50/60 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <div className="flex items-center gap-1.5 mb-2">
            <SlidersHorizontal size={14} className="text-indigo-500" />
            <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300">快捷调整</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onAdjustParam("sensor_size", "1/2")}
              className="px-2.5 py-1 rounded-md bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-700 text-xs text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
            >
              改用 1/2" 传感器
            </button>
            <button
              onClick={() => onAdjustParam("interface", "CS-mount")}
              className="px-2.5 py-1 rounded-md bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-700 text-xs text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
            >
              改用 CS-mount
            </button>
            <button
              onClick={() => onAdjustParam("working_distance_mm", 500)}
              className="px-2.5 py-1 rounded-md bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-700 text-xs text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
            >
              工作距离 500mm
            </button>
            <button
              onClick={() => onAdjustParam("target_width_mm", 100)}
              className="px-2.5 py-1 rounded-md bg-white dark:bg-slate-800 border border-indigo-200 dark:border-indigo-700 text-xs text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
            >
              视场 100mm
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
