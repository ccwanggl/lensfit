import { Loader2 } from "lucide-react";
import type { LabRunResult } from "../utils/api";

interface BreadboardPresetRunnerProps {
  result?: LabRunResult;
  isFetching: boolean;
}

export function BreadboardPresetRunner({ result, isFetching }: BreadboardPresetRunnerProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200/60 bg-slate-50/60 p-3 text-sm dark:border-slate-700/60 dark:bg-slate-800/60">
        <div className="font-semibold text-slate-800 dark:text-slate-200">
          锁定布局：激光 → 单缝 → 屏幕
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-500" />
            单色激光器
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-slate-800 dark:bg-slate-200" />
            单缝光阑
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-indigo-500" />
            接收屏 / 强度曲线
          </span>
        </div>
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          几何层为示意图；下方曲线为波动光学计算得到的相对强度分布。
        </p>
      </div>

      <div
        className={`transition-opacity duration-200 ${
          isFetching ? "opacity-60" : "opacity-100"
        }`}
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: result?.svg ?? "" }}
      />

      {isFetching && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="animate-spin text-indigo-500" size={24} />
        </div>
      )}
    </div>
  );
}
