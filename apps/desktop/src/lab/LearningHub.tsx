import {
  BarChart3,
  BookOpen,
  ChevronRight,
  ExternalLink,
  FlaskConical,
  Lightbulb,
  Loader2,
  Maximize2,
  Minimize2,
  PanelLeft,
  Play,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  getLabExperiment,
  runLabExperiment,
  runWorkbench,
  type LabExperiment,
} from "../utils/api";
import { useLabStore } from "../stores/labStore";
import { ExperimentCatalog } from "./ExperimentCatalog";
import { ParameterControl } from "./ParameterControl";
import { KnowledgeSidebar } from "./KnowledgeSidebar";
import { getExperimentMedia } from "./experimentMedia";
import { BreadboardPresetRunner } from "./BreadboardPresetRunner";
import {
  getBreadboardPreset,
  isBreadboardPreset,
} from "./workbenchTypes";

type TabId = "visual" | "data" | "hints";

export default function LearningHub() {
  const activeExperimentId = useLabStore((s) => s.activeExperimentId);
  const showSidebar = useLabStore((s) => s.showSidebar);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);
  const toggleSidebar = useLabStore((s) => s.toggleSidebar);
  const storeSetParams = useLabStore((s) => s.setParams);
  const allDrafts = useLabStore((s) => s.paramDrafts);

  const [showKnowledge, setShowKnowledge] = useState(true);
  const [centerExpanded, setCenterExpanded] = useState(false);
  const [mobilePanel, setMobilePanel] = useState<"left" | "right" | null>(null);

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

  const paramDrafts = useMemo(
    () => (activeExperimentId ? allDrafts[activeExperimentId] ?? {} : {}),
    [allDrafts, activeExperimentId]
  );

  const initialParams = useMemo(() => {
    if (!experiment) return {};
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = paramDrafts[p.name] ?? p.default;
    }
    return defaults;
  }, [experiment, paramDrafts]);

  const [params, setParams] = useState(initialParams);
  const [liveParams, setLiveParams] = useState(initialParams);
  const [activeTab, setActiveTab] = useState<TabId>("visual");
  const debounceRef = useRef<number | null>(null);

  useEffect(() => {
    setParams(initialParams);
    setLiveParams(initialParams);
  }, [initialParams]);

  const {
    data: result,
    isFetching,
    error: runError,
  } = useQuery({
    queryKey: ["lab-run", activeExperimentId, liveParams],
    queryFn: () => {
      if (isPreset && preset) {
        return runWorkbench(preset.buildScene(liveParams));
      }
      return runLabExperiment(activeExperimentId!, liveParams);
    },
    enabled: !!activeExperimentId && !!experiment,
  });

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
      storeSetParams(activeExperimentId, { [name]: value });
    }
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
    }
    debounceRef.current = window.setTimeout(() => {
      setLiveParams(next);
    }, 60);
  };

  const handleReset = () => {
    if (!experiment) return;
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = p.default;
    }
    setParams(defaults);
    if (activeExperimentId) {
      storeSetParams(activeExperimentId, defaults);
    }
    setLiveParams(defaults);
  };

  return (
    <div className="relative flex h-[calc(100vh-140px)] gap-4">
      {/* ─── Left column: catalog + parameters ─── */}
      {!centerExpanded && (
        <aside
          className={`${
            showSidebar ? "hidden lg:flex" : "hidden"
          } h-full w-80 shrink-0 flex-col gap-3`}
        >
          <div className="min-h-0 flex-[1.2]">
            <ExperimentCatalog onSelect={handleSelectExperiment} />
          </div>
          {experiment && (
            <div className="min-h-0 flex-1 overflow-hidden rounded-[14px] border border-slate-200/60 bg-white/80 p-4 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
              <ParameterPanel
                experiment={experiment}
                params={params}
                onChange={handleParamChange}
                onReset={handleReset}
                isFetching={isFetching}
              />
            </div>
          )}
        </aside>
      )}

      {/* ─── Mobile left overlay ─── */}
      {mobilePanel === "left" && (
        <div className="absolute inset-y-0 left-0 z-30 w-[85%] max-w-xs bg-slate-50/95 p-3 shadow-2xl backdrop-blur dark:bg-slate-950/95 lg:hidden">
          <div className="flex h-full flex-col gap-3">
            <button
              onClick={() => setMobilePanel(null)}
              className="self-end rounded-lg p-2 text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              <X size={18} />
            </button>
            <div className="min-h-0 flex-1">
              <ExperimentCatalog onSelect={handleSelectExperiment} />
            </div>
            {experiment && (
              <div className="min-h-0 flex-1 overflow-hidden rounded-[14px] border border-slate-200/60 bg-white/80 p-4 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
                <ParameterPanel
                  experiment={experiment}
                  params={params}
                  onChange={handleParamChange}
                  onReset={handleReset}
                  isFetching={isFetching}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── Center column: display ─── */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* Top toolbar */}
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMobilePanel("left")}
              className="rounded-lg border border-slate-200 bg-white p-2 text-slate-600 hover:bg-slate-50 lg:hidden dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              title="目录"
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
                  title="知识点"
                >
                  <BookOpen size={18} />
                </button>
                <button
                  onClick={handleCloseExperiment}
                  className="rounded-lg border border-slate-200 bg-white p-2 text-slate-500 hover:bg-slate-50 hover:text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
                  title="关闭实验"
                >
                  <X size={18} />
                </button>
              </>
            )}
          </div>
        </div>

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
                      <BreadboardPresetRunner result={result} isFetching={isFetching} />
                    ) : (
                      <div className="space-y-4">
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
            <EmptyState onOpenCatalog={() => setMobilePanel("left")} />
          )}
        </div>
      </main>

      {/* ─── Right column: knowledge ─── */}
      {!centerExpanded && (
        <aside
          className={`${
            showKnowledge ? "hidden lg:flex" : "hidden"
          } h-full w-80 shrink-0 flex-col`}
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
  );
}

/* ─── Sub-components ─── */

function ParameterPanel({
  experiment,
  params,
  onChange,
  onReset,
  isFetching,
}: {
  experiment: LabExperiment;
  params: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
  onReset: () => void;
  isFetching: boolean;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
          参数控制
        </h3>
        {isFetching && (
          <Loader2 size={14} className="animate-spin text-indigo-500" />
        )}
      </div>
      <div className="min-h-0 flex-1 space-y-3 overflow-auto pr-1">
        {experiment.parameters.map((param) => (
          <ParameterControl
            key={param.name}
            param={param}
            value={params[param.name]}
            onChange={(value) => onChange(param.name, value)}
          />
        ))}
      </div>
      <button
        onClick={onReset}
        className="mt-3 w-full rounded-lg border border-slate-200 bg-white py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
      >
        重置默认参数
      </button>
    </div>
  );
}

function MediaPanel({ experimentId }: { experimentId: string }) {
  const media = useMemo(() => getExperimentMedia(experimentId), [experimentId]);
  const [open, setOpen] = useState(false);

  if (!media) return null;

  return (
    <div className="rounded-xl border border-slate-200/60 bg-slate-50/60 p-3 dark:border-slate-700/60 dark:bg-slate-800/60">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between"
      >
        <span className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
          <Play size={14} className="text-rose-500" />
          实验实操
          {media.caption && (
            <span className="font-normal text-slate-500 dark:text-slate-400">
              · {media.caption}
            </span>
          )}
        </span>
        <span className="text-xs text-indigo-600 dark:text-indigo-400">
          {open ? "收起" : "展开"}
        </span>
      </button>

      {open && (
        <div className="mt-3">
          {media.video?.provider === "youtube" && (
            <div className="relative aspect-video w-full max-h-56 overflow-hidden rounded-lg bg-black">
              <iframe
                className="h-full w-full"
                src={`https://www.youtube-nocookie.com/embed/${media.video.id}${
                  media.video.start ? `?start=${media.video.start}` : ""
                }`}
                title={media.video.title ?? "实验视频"}
                allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
              />
            </div>
          )}
          {media.image && (
            <div className="relative max-h-56 overflow-hidden rounded-lg">
              <img
                src={media.image.src}
                alt={media.image.alt}
                className="max-h-56 w-full object-contain"
                loading="lazy"
              />
              {media.image.credit && (
                <p className="mt-1 text-[10px] text-slate-400">
                  来源：{media.image.credit}
                </p>
              )}
            </div>
          )}
          {media.video?.provider === "youtube" && (
            <a
              href={`https://www.youtube.com/watch?v=${media.video.id}`}
              target="_blank"
              rel="noreferrer"
              className="mt-2 inline-flex items-center gap-1 text-xs text-indigo-600 hover:underline dark:text-indigo-400"
            >
              在 YouTube 打开 <ExternalLink size={10} />
            </a>
          )}
        </div>
      )}
    </div>
  );
}

function DataPanel({ result }: { result?: { data: Record<string, unknown> } }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h4 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
        计算数据
      </h4>
      <pre className="max-h-[60vh] overflow-auto text-xs text-slate-600 dark:text-slate-400">
        {result ? JSON.stringify(result.data, null, 2) : "暂无数据"}
      </pre>
    </div>
  );
}

function HintsPanel({
  result,
}: {
  result?: { warnings: string[]; learning_hints: string[] };
}) {
  return (
    <div className="space-y-4">
      {result?.warnings.length ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-900 dark:bg-amber-950/30">
          <div className="mb-1 text-sm font-semibold text-amber-800 dark:text-amber-400">
            注意
          </div>
          <ul className="list-inside list-disc text-sm text-amber-700 dark:text-amber-300">
            {result.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {result?.learning_hints.length ? (
        <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-3 dark:border-indigo-900 dark:bg-indigo-950/30">
          <div className="mb-1 text-sm font-semibold text-indigo-800 dark:text-indigo-400">
            学习提示
          </div>
          <ul className="list-inside list-disc text-sm text-indigo-700 dark:text-indigo-300">
            {result.learning_hints.map((h, i) => (
              <li key={i}>{h}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-sm text-slate-500 dark:text-slate-400">暂无学习提示</p>
      )}
    </div>
  );
}

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const cls =
    difficulty === "foundation"
      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
      : difficulty === "intermediate"
      ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
      : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400";
  const label =
    difficulty === "foundation" ? "基础" : difficulty === "intermediate" ? "进阶" : "高级";
  return (
    <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${cls}`}>
      {label}
    </span>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
        active
          ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-400"
          : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function LoadingState() {
  return (
    <div className="flex h-full items-center justify-center">
      <Loader2 className="animate-spin text-indigo-500" size={32} />
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        无法加载实验：{message}
      </div>
    </div>
  );
}

function EmptyState({ onOpenCatalog }: { onOpenCatalog: () => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center rounded-[14px] border border-dashed border-slate-300 bg-white/50 p-8 text-center dark:border-slate-700 dark:bg-slate-800/50">
      <div className="mb-3 text-4xl">🔬</div>
      <h2 className="mb-2 text-lg font-semibold text-slate-800 dark:text-slate-200">
        欢迎来到学习中心
      </h2>
      <p className="max-w-md text-sm text-slate-500 dark:text-slate-400">
        在左侧选择一项光学实验，调整参数观察实时模拟，右侧会显示相关的概念与公式。
      </p>
      <button
        onClick={onOpenCatalog}
        className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 lg:hidden"
      >
        打开实验目录
      </button>
    </div>
  );
}
