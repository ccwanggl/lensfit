import { lazy, Suspense, useState } from "react";
import { BarChart3, Box, Loader2, ScanLine } from "lucide-react";
import type { LabRunResult } from "../utils/api";
import { BreadboardRayCanvas } from "./BreadboardRayCanvas";
import type { WorkbenchScene } from "./workbenchTypes";

const Breadboard3DCanvas = lazy(() =>
  import("./Breadboard3DCanvas").then((m) => ({ default: m.Breadboard3DCanvas }))
);

interface BreadboardPresetRunnerProps {
  result?: LabRunResult;
  isFetching: boolean;
  presetId?: string;
  scene?: WorkbenchScene;
}

export function BreadboardPresetRunner({
  result,
  isFetching,
  presetId,
  scene,
}: BreadboardPresetRunnerProps) {
  const [view, setView] = useState<"3d" | "2d" | "ray">("3d");
  const isDoubleSlit = presetId === "double-slit-breadboard";

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200/60 bg-slate-50/60 p-3 text-sm dark:border-slate-700/60 dark:bg-slate-800/60">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-slate-800 dark:text-slate-200">
            锁定布局：激光 → {isDoubleSlit ? "双缝" : "单缝"} → 屏幕
          </div>
          <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-0.5 dark:border-slate-700 dark:bg-slate-900">
            <button
              onClick={() => setView("3d")}
              className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                view === "3d"
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`}
            >
              <Box size={13} />
              3D 场景
            </button>
            <button
              onClick={() => setView("2d")}
              className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                view === "2d"
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`}
            >
              <BarChart3 size={13} />
              2D 曲线
            </button>
            <button
              onClick={() => setView("ray")}
              className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                view === "ray"
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`}
            >
              <ScanLine size={13} />
              光路图
            </button>
          </div>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-500" />
            单色激光器
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-slate-800 dark:bg-slate-200" />
            {isDoubleSlit ? "双缝光阑" : "单缝光阑"}
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-indigo-500" />
            接收屏 / 强度曲线
          </span>
        </div>
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          {view === "3d"
            ? "3D 场景中可拖拽旋转、滚轮缩放；屏幕颜色表示相对光强分布。"
            : view === "2d"
            ? "下方曲线为波动光学计算得到的相对强度分布。"
            : "下方为基于几何光学实时绘制的交互式光路图，可调整光线密度与 Y 轴放大倍数。"}
        </p>
      </div>

      {view === "3d" ? (
        <Suspense
          fallback={
            <div className="flex h-96 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900">
              <Loader2 className="animate-spin text-indigo-500" size={24} />
            </div>
          }
        >
          <Breadboard3DCanvas
            result={result}
            presetId={presetId}
            isFetching={isFetching}
          />
        </Suspense>
      ) : view === "2d" ? (
        <div
          className={`transition-opacity duration-200 ${
            isFetching ? "opacity-60" : "opacity-100"
          }`}
          // eslint-disable-next-line react/no-danger
          dangerouslySetInnerHTML={{ __html: result?.svg ?? "" }}
        />
      ) : (
        <BreadboardRayCanvas scene={scene} result={result} />
      )}

      {isFetching && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="animate-spin text-indigo-500" size={24} />
        </div>
      )}
    </div>
  );
}
