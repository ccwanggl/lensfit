import {
  BookOpen,
  ChevronRight,
  FlaskConical,
  Maximize2,
  Minimize2,
  PanelLeft,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  getLabExperiment,
  runLabExperiment,
  runWorkbench,
} from "../utils/api";
import { useLabStore } from "../stores/labStore";
import { KnowledgeSidebar } from "./KnowledgeSidebar";
import { useReportProgress } from "./reportProgress";
import TutorialView from "./TutorialView";
import PathView from "./PathView";
import {
  getBreadboardPreset,
  isBreadboardPreset,
  type WorkbenchScene,
  validatePresetParams,
} from "./workbenchTypes";
import { ViewSwitcher } from "./hub/ViewSwitcher";
import { DifficultyBadge } from "./hub/states";
import { DesktopCatalogColumn, MobileCatalogOverlay } from "./hub/CatalogColumn";
import { DisplayCard, type HubTabId } from "./hub/DisplayCard";

export { BreadboardPresetHeader } from "./hub/BreadboardPresetHeader";

export default function LearningHub() {
  const activeExperimentId = useLabStore((s) => s.activeExperimentId);
  const showSidebar = useLabStore((s) => s.showSidebar);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);
  const toggleSidebar = useLabStore((s) => s.toggleSidebar);
  const storeSetParams = useLabStore((s) => s.setParams);
  const sceneDrafts = useLabStore((s) => s.sceneDrafts);
  const setSceneDraft = useLabStore((s) => s.setSceneDraft);
  const resetSceneDraft = useLabStore((s) => s.resetSceneDraft);
  const allDrafts = useLabStore((s) => s.paramDrafts);
  const learningView = useLabStore((s) => s.learningView);
  const setLearningView = useLabStore((s) => s.setLearningView);

  const [showKnowledge, setShowKnowledge] = useState(true);
  const [centerExpanded, setCenterExpanded] = useState(false);
  const [mobilePanel, setMobilePanel] = useState<"left" | "right" | null>(null);
  const [sceneError, setSceneError] = useState<string | null>(null);

  const isPreset = useMemo(
    () => isBreadboardPreset(activeExperimentId),
    [activeExperimentId]
  );
  const preset = useMemo(
    () => getBreadboardPreset(activeExperimentId ?? ""),
    [activeExperimentId]
  );

  const { data, isLoading, error } = useQuery({
    queryKey: ["lab-experiment", activeExperimentId],
    queryFn: () => getLabExperiment(activeExperimentId!),
    enabled: !!activeExperimentId && !isPreset,
  });

  const experiment = preset ?? data?.items[0] ?? null;

  const drafts = useMemo(
    () =>
      activeExperimentId
        ? (isPreset ? sceneDrafts[activeExperimentId] : allDrafts[activeExperimentId]) ?? {}
        : {},
    [isPreset, sceneDrafts, allDrafts, activeExperimentId]
  );

  const initialParams = useMemo(() => {
    if (!experiment) return {};
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = drafts[p.name] ?? p.default;
    }
    return defaults;
  }, [experiment, drafts]);

  const [params, setParams] = useState(initialParams);
  const [liveParams, setLiveParams] = useState(initialParams);
  const [activeTab, setActiveTab] = useState<HubTabId>("visual");
  const debounceRef = useRef<number | null>(null);

  const workbenchScene: WorkbenchScene | null = useMemo(() => {
    if (!isPreset || !preset) return null;
    return preset.buildScene(liveParams);
  }, [isPreset, preset, liveParams]);

  useEffect(() => {
    setParams(initialParams);
    const error =
      isPreset && activeExperimentId
        ? validatePresetParams(activeExperimentId, initialParams)
        : null;
    setSceneError(error);
    if (!error) {
      setLiveParams(initialParams);
    }
  }, [initialParams, isPreset, activeExperimentId]);

  const {
    data: result,
    isFetching,
    error: runError,
  } = useQuery({
    queryKey: ["lab-run", activeExperimentId, liveParams],
    queryFn: () => {
      if (isPreset && workbenchScene) {
        return runWorkbench(workbenchScene, false);
      }
      return runLabExperiment(activeExperimentId!, liveParams);
    },
    enabled:
      !!activeExperimentId &&
      !!experiment &&
      sceneError === null &&
      (!isPreset || !!workbenchScene),
    // 调参触发新 queryKey 时保留上一次结果，避免 SVG 区域清空重绘造成闪烁；
    // 切换实验（queryKey[1] 变化）时不保留，防止短暂显示上一个实验的图像。
    placeholderData: (prev, prevQuery) =>
      prevQuery?.queryKey[1] === activeExperimentId ? prev : undefined,
  });

  const reportProgress = useReportProgress();

  // 实验运行成功后上报 completed（同一实验只上报一次）
  useEffect(() => {
    if (result && !runError && activeExperimentId) {
      reportProgress(isPreset ? "preset" : "experiment", activeExperimentId, "completed");
    }
  }, [result, runError, activeExperimentId, isPreset, reportProgress]);

  const handleSelectExperiment = (id: string) => {
    setActiveExperimentId(id);
    setActiveTab("visual");
    setMobilePanel(null);
  };

  const handleCloseExperiment = () => {
    setActiveExperimentId(null);
    setParams({});
    setLiveParams({});
  };

  const handleParamChange = (name: string, value: unknown) => {
    const next = { ...params, [name]: value };
    setParams(next);
    if (activeExperimentId) {
      if (isPreset) {
        setSceneDraft(activeExperimentId, { [name]: value });
      } else {
        storeSetParams(activeExperimentId, { [name]: value });
      }
    }
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
    }
    debounceRef.current = window.setTimeout(() => {
      const error =
        isPreset && activeExperimentId
          ? validatePresetParams(activeExperimentId, next)
          : null;
      setSceneError(error);
      if (!error) {
        setLiveParams(next);
      }
    }, 60);
  };

  const handleReset = () => {
    if (!experiment) return;
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = p.default;
    }
    setParams(defaults);
    setSceneError(null);
    if (activeExperimentId) {
      if (isPreset) {
        resetSceneDraft(activeExperimentId);
      } else {
        storeSetParams(activeExperimentId, defaults);
      }
    }
    setLiveParams(defaults);
  };

  return (
    <div className="flex h-[calc(100vh-112px)] flex-col gap-3">
        <ViewSwitcher
          learningView={learningView}
          setLearningView={setLearningView}
        />

      {learningView === "path" ? (
        <div className="min-h-0 flex-1">
          <PathView />
        </div>
      ) : learningView === "tutorials" ? (
        <div className="min-h-0 flex-1">
          <TutorialView />
        </div>
      ) : (
    <div className="relative flex min-h-0 flex-1 gap-4">
      {/* ─── Left column: catalog + parameters ─── */}
      {!centerExpanded && (
        <DesktopCatalogColumn
          showSidebar={showSidebar}
          centerExpanded={centerExpanded}
          handleSelectExperiment={handleSelectExperiment}
          experiment={experiment}
          isPreset={isPreset}
          activeExperimentId={activeExperimentId}
          params={params}
          handleParamChange={handleParamChange}
          handleReset={handleReset}
          isFetching={isFetching}
          sceneError={sceneError}
        />
      )}

      {/* ─── Mobile left overlay ─── */}
      {mobilePanel === "left" && (
        <MobileCatalogOverlay
          setMobilePanel={setMobilePanel}
          handleSelectExperiment={handleSelectExperiment}
          experiment={experiment}
          isPreset={isPreset}
          activeExperimentId={activeExperimentId}
          params={params}
          handleParamChange={handleParamChange}
          handleReset={handleReset}
          isFetching={isFetching}
          sceneError={sceneError}
        />
      )}

      {/* ─── Center column: display ─── */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* Top toolbar */}
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMobilePanel("left")}
              className="rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-50 lg:hidden dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              title="目录" aria-label="目录"
            >
              <PanelLeft size={18} />
            </button>
            {!showSidebar && !centerExpanded && (
              <button
                onClick={toggleSidebar}
                className="hidden items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 lg:flex dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                <ChevronRight size={14} />
                目录
              </button>
            )}
            {activeExperimentId && experiment && (
              <div className="hidden items-center gap-2 sm:flex">
                <FlaskConical size={16} className="text-indigo-500" />
                <span className="text-sm font-bold text-slate-800 dark:text-slate-200">
                  {experiment.title}
                </span>
                <DifficultyBadge difficulty={experiment.difficulty} />
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {activeExperimentId && (
              <>
                <button
                  onClick={() => setCenterExpanded((v) => !v)}
                  className="hidden items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 lg:flex dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  {centerExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
                  {centerExpanded ? "退出全屏" : "全屏"}
                </button>
                <button
                  onClick={() => setShowKnowledge((v) => !v)}
                  className={`hidden items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium lg:flex ${
                    showKnowledge
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800/40 dark:bg-emerald-900/30 dark:text-emerald-400"
                      : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                  }`}
                >
                  {showKnowledge ? <ChevronRight size={14} /> : <BookOpen size={14} />}
                  {showKnowledge ? "收起知识" : "知识点"}
                </button>
                <button
                  onClick={() => setMobilePanel("right")}
                  className="rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-50 lg:hidden dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                  title="知识点" aria-label="知识点"
                >
                  <BookOpen size={18} />
                </button>
                <button
                  onClick={handleCloseExperiment}
                  className="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 hover:bg-slate-50 hover:text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
                  title="关闭实验" aria-label="关闭实验"
                >
                  <X size={18} />
                </button>
              </>
            )}
          </div>
        </div>

          <DisplayCard
            activeExperimentId={activeExperimentId}
            isLoading={isLoading}
            error={error}
            experiment={experiment}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            isFetching={isFetching}
            runError={runError}
            isPreset={isPreset}
            result={result}
            workbenchScene={workbenchScene}
            onOpenCatalog={() => setMobilePanel("left")}
          />
      </main>

      {/* ─── Right column: knowledge ─── */}
      {!centerExpanded && (
        <aside
          className={`${
            showKnowledge ? "hidden lg:flex" : "hidden"
          } h-full w-72 shrink-0 flex-col`}
        >
          <KnowledgeSidebar experiment={experiment} />
        </aside>
      )}

      {/* ─── Mobile right overlay ─── */}
      {mobilePanel === "right" && (
        <div className="absolute inset-y-0 right-0 z-30 w-[85%] max-w-xs bg-slate-50/95 p-3 shadow-2xl backdrop-blur dark:bg-slate-950/95 lg:hidden">
          <div className="flex h-full flex-col">
            <button
              onClick={() => setMobilePanel(null)}
              className="self-end rounded-lg p-2 text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800"
              aria-label="关闭面板"
            >
              <X size={18} />
            </button>
            <div className="min-h-0 flex-1">
              <KnowledgeSidebar experiment={experiment} />
            </div>
          </div>
        </div>
      )}

      {/* Backdrop for mobile overlays */}
      {mobilePanel && (
        <div
          className="absolute inset-0 z-20 bg-slate-900/20 backdrop-blur-sm lg:hidden"
          onClick={() => setMobilePanel(null)}
        />
      )}
    </div>
      )}
    </div>
  );
}
