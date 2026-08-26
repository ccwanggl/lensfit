/** Main sandbox display card: tabs + visual/data/hints content (slice B).
 *
 * Purely presentational: all queries stay in LearningHub.
 */
import { BarChart3, Lightbulb, Loader2, Maximize2 } from "lucide-react";
import { BreadboardPresetRunner } from "../BreadboardPresetRunner";
import { DataPanel, HintsPanel, MediaPanel } from "./panels";
import { EmptyState, ErrorState, LoadingState } from "./states";
import { TabButton } from "./TabButton";
import type { LabExperiment, LabRunResult } from "../../utils/api";
import type { WorkbenchScene } from "../workbenchTypes";

export type HubTabId = "visual" | "data" | "hints";

export function DisplayCard({
  activeExperimentId, isLoading, error, experiment,
  activeTab, setActiveTab, isFetching, runError,
  isPreset, result, workbenchScene, onOpenCatalog,
}: {
  activeExperimentId: string | null;
  isLoading: boolean;
  error: Error | null;
  experiment: LabExperiment | null;
  activeTab: HubTabId;
  setActiveTab: (t: HubTabId) => void;
  isFetching: boolean;
  runError: Error | null;
  isPreset: boolean;
  result?: LabRunResult;
  workbenchScene: WorkbenchScene | null;
  onOpenCatalog: () => void;
}) {
  return (
    <>
{/* Main display card */}
        <div className="flex min-h-0 flex-1 flex-col rounded-[14px] border border-slate-200/60 bg-white/80 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
          {activeExperimentId ? (
            isLoading ? (
              <LoadingState />
            ) : error || !experiment ? (
              <ErrorState message={error?.message ?? "未找到实验"} />
            ) : (
              <>
                {/* Header / tabs */}
                <div className="flex items-center justify-between border-b border-slate-200/60 px-4 py-2 dark:border-slate-700/60">
                  <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-0.5 dark:border-slate-700 dark:bg-slate-900">
                    <TabButton
                      active={activeTab === "visual"}
                      onClick={() => setActiveTab("visual")}
                      icon={<Maximize2 size={14} />}
                      label="可视化"
                    />
                    <TabButton
                      active={activeTab === "data"}
                      onClick={() => setActiveTab("data")}
                      icon={<BarChart3 size={14} />}
                      label="数据"
                    />
                    <TabButton
                      active={activeTab === "hints"}
                      onClick={() => setActiveTab("hints")}
                      icon={<Lightbulb size={14} />}
                      label="提示"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    {isFetching && (
                      <span className="inline-flex items-center gap-1 text-xs text-indigo-500">
                        <Loader2 size={12} className="animate-spin" />
                        计算中…
                      </span>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className="relative min-h-0 flex-1 overflow-auto p-4">
                  {runError ? (
                    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
                      实验运行失败：{runError.message}
                    </div>
                  ) : activeTab === "visual" ? (
                    isPreset ? (
                      <BreadboardPresetRunner
                        result={result}
                        isFetching={isFetching}
                        presetId={activeExperimentId ?? undefined}
                        scene={workbenchScene ?? undefined}
                      />
                    ) : (
                      <div className="space-y-3">
                        <MediaPanel experimentId={experiment.id} />
                        <div
                          className={`transition-opacity duration-200 ${
                            isFetching ? "opacity-60" : "opacity-100"
                          }`}
                          // eslint-disable-next-line react/no-danger
                          dangerouslySetInnerHTML={{ __html: result?.svg ?? "" }}
                        />
                      </div>
                    )
                  ) : activeTab === "data" ? (
                    <DataPanel result={result} />
                  ) : (
                    <HintsPanel result={result} />
                  )}

                  {isFetching && (
                    <div className="absolute right-4 top-4">
                      <Loader2 className="animate-spin text-indigo-500" size={20} />
                    </div>
                  )}
                </div>
              </>
            )
          ) : (
            <EmptyState onOpenCatalog={onOpenCatalog} />
          )}
        </div>
    </>
  );
}
