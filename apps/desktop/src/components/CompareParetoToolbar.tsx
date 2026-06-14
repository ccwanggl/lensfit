import { ArrowLeftRight, Layers, X } from "lucide-react";
import { Button } from "./ui";
import type { UnifiedMatchResult } from "../hooks/useMatching";

interface Props {
  compareMode: boolean;
  onCompareModeChange: (v: boolean) => void;
  paretoOnly: boolean;
  onParetoChange: (v: boolean) => void;
  selectionCount: number;
  onClearSelection?: () => void;
}

export function computeParetoFrontier(results: UnifiedMatchResult[]): UnifiedMatchResult[] {
  return results.filter((a, i) => {
    return !results.some((b, j) => {
      if (i === j) return false;
      const aVec = a.score_vector ?? {};
      const bVec = b.score_vector ?? {};
      const keys = new Set([...Object.keys(aVec), ...Object.keys(bVec)]);
      let strictlyBetter = false;
      for (const k of keys) {
        const av = aVec[k] ?? 0;
        const bv = bVec[k] ?? 0;
        if (bv < av) return false;
        if (bv > av) strictlyBetter = true;
      }
      return strictlyBetter;
    });
  });
}

export default function CompareParetoToolbar({
  compareMode,
  onCompareModeChange,
  paretoOnly,
  onParetoChange,
  selectionCount,
  onClearSelection,
}: Props) {
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => onParetoChange(!paretoOnly)}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
          paretoOnly
            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
            : "bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
        }`}
        title="仅显示 Pareto 前沿方案（按评分维度无被支配项）"
      >
        <Layers size={12} />
        {paretoOnly ? "Pareto 前沿" : "全部方案"}
      </button>

      <Button
        variant={compareMode ? "primary" : "outline"}
        size="sm"
        leftIcon={<ArrowLeftRight size={12} />}
        onClick={() => {
          onCompareModeChange(!compareMode);
          if (compareMode) onClearSelection?.();
        }}
      >
        {compareMode ? `对比中 ${selectionCount}` : "对比"}
      </Button>

      {compareMode && selectionCount > 0 && (
        <button
          onClick={onClearSelection}
          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-colors"
          title="清空选择"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}
