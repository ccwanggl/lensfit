import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  FlaskConical,
  Lightbulb,
  Loader2,
  Maximize2,
  Minimize2,
  X,
} from "lucide-react";
import { getLabExperiment, LabExperiment, runLabExperiment } from "../utils/api";
import { useLabStore } from "../stores/labStore";
import { ParameterControl } from "./ParameterControl";

interface ExperimentRunnerProps {
  experimentId: string;
  fullscreen?: boolean;
  onExitFullscreen?: () => void;
}

export function ExperimentRunner({
  experimentId,
  fullscreen,
  onExitFullscreen,
}: ExperimentRunnerProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["lab-experiment", experimentId],
    queryFn: () => getLabExperiment(experimentId),
  });

  const experiment = data?.items[0];

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={32} />
      </div>
    );
  }

  if (error || !experiment) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        无法加载实验：{error?.message ?? "未找到实验"}
      </div>
    );
  }

  return (
    <Runner
      experiment={experiment}
      fullscreen={fullscreen}
      onExitFullscreen={onExitFullscreen}
    />
  );
}

type TabId = "visual" | "data" | "hints";

function Runner({
  experiment,
  fullscreen,
  onExitFullscreen,
}: {
  experiment: LabExperiment;
  fullscreen?: boolean;
  onExitFullscreen?: () => void;
}) {
  const allDrafts = useLabStore((s) => s.paramDrafts);
  const setParams = useLabStore((s) => s.setParams);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);
  const showDataPanel = useLabStore((s) => s.showDataPanel);
  const toggleDataPanel = useLabStore((s) => s.toggleDataPanel);

  const [activeTab, setActiveTab] = useState<TabId>("visual");

  const paramDrafts = useMemo(
    () => allDrafts[experiment.id] ?? {},
    [allDrafts, experiment.id]
  );

  const initialParams = useMemo(() => {
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = paramDrafts[p.name] ?? p.default;
    }
    return defaults;
  }, [experiment, paramDrafts]);

  const [params, setLocalParams] = useState(initialParams);
  const [liveParams, setLiveParams] = useState(initialParams);
  const debounceRef = useRef<number | null>(null);

  // Sync local state when persisted drafts change
  useEffect(() => {
    setLocalParams(initialParams);
    setLiveParams(initialParams);
  }, [initialParams]);

  const {
    data: result,
    isFetching,
    error: runError,
  } = useQuery({
    queryKey: ["lab-run", experiment.id, liveParams],
    queryFn: () => runLabExperiment(experiment.id, liveParams),
    enabled: !!experiment,
  });

  const handleChange = (name: string, value: unknown) => {
    const next = { ...params, [name]: value };
    setLocalParams(next);
    setParams(experiment.id, { [name]: value });
    // Trigger a run with a short debounce to balance interactivity and backend load.
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
    }
    debounceRef.current = window.setTimeout(() => {
      setLiveParams(next);
    }, 60);
  };

  const handleReset = () => {
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = p.default;
    }
    setLocalParams(defaults);
    setParams(experiment.id, defaults);
    setLiveParams(defaults);
  };

  const difficultyClass = {
    foundation:
      "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    intermediate:
      "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    advanced:
      "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400",
  }[experiment.difficulty] ?? "bg-slate-100 text-slate-700";

  return (
    <div
      className={`flex h-full flex-col gap-4 ${
        fullscreen ? "lg:flex-row" : "lg:flex-row"
      }`}
    >
      {/* Controls */}
      <aside
        className={`shrink-0 overflow-y-auto rounded-[14px] border border-slate-200/60 bg-white/80 p-5 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80 ${
          fullscreen ? "lg:w-72" : "lg:w-80"
        }`}
      >
        <div className="mb-4 flex items-center gap-2">
          <FlaskConical size={18} className="text-indigo-500" />
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
            {experiment.title}
          </h2>
        </div>
        <p className="mb-3 text-sm text-slate-600 dark:text-slate-400">
          {experiment.description}
        </p>
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${difficultyClass}`}
          >
            {experiment.difficulty === "foundation"
              ? "基础"
              : experiment.difficulty === "intermediate"
              ? "进阶"
              : "高级"}
          </span>
          {isFetching && (
            <span className="inline-flex items-center gap-1 text-xs text-indigo-500">
              <Loader2 size={12} className="animate-spin" />
              计算中…
            </span>
          )}
        </div>

        <div className="space-y-3">
          {experiment.parameters.map((param) => (
            <ParameterControl
              key={param.name}
              param={param}
              value={params[param.name]}
              onChange={(value) => handleChange(param.name, value)}
            />
          ))}
        </div>

        <button
          onClick={handleReset}
          className="mt-4 w-full rounded-lg border border-slate-200 bg-white py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
        >
          重置默认参数
        </button>

        {experiment.learning_objectives.length > 0 && (
          <div className="mt-5 rounded-lg bg-indigo-50 p-3 dark:bg-indigo-900/20">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-indigo-700 dark:text-indigo-400">
              学习目标
            </h4>
            <ul className="list-inside list-disc space-y-1 text-xs text-indigo-800 dark:text-indigo-300">
              {experiment.learning_objectives.map((obj, i) => (
                <li key={i}>{obj}</li>
              ))}
            </ul>
          </div>
        )}

        {experiment.linked_concepts.length > 0 && (
          <div className="mt-4">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              关联知识
            </h4>
            <div className="flex flex-wrap gap-2">
              {experiment.linked_concepts.map((concept) => {
                const name = concept.split("/").pop() ?? concept;
                return (
                  <a
                    key={concept}
                    href={`obsidian://open?vault=OpticKnowledgeSpace&file=${encodeURIComponent(
                      concept
                    )}`}
                    className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-600 hover:border-indigo-300 hover:text-indigo-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:border-indigo-500 dark:hover:text-indigo-400"
                  >
                    <BookOpen size={12} />
                    {name}
                  </a>
                );
              })}
            </div>
          </div>
        )}
      </aside>

      {/* Main visualization + tabs */}
      <main className="flex min-w-0 flex-1 flex-col rounded-[14px] border border-slate-200/60 bg-white/80 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200/60 px-5 py-3 dark:border-slate-700/60">
          <div className="flex items-center gap-2">
            <div className="flex rounded-lg border border-slate-200 bg-slate-50 p-0.5 dark:border-slate-700 dark:bg-slate-900">
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
          </div>

          <div className="flex items-center gap-2">
            {fullscreen ? (
              <button
                onClick={onExitFullscreen}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-300"
                title="退出全屏"
              >
                <Minimize2 size={16} />
              </button>
            ) : (
              <>
                <button
                  onClick={toggleDataPanel}
                  className="hidden items-center gap-1 rounded-lg px-2 py-1 text-xs font-medium text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700 lg:flex"
                >
                  {showDataPanel ? "收起数据" : "展开数据"}
                </button>
                <button
                  onClick={() => setActiveExperimentId(null)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-300"
                  title="关闭实验"
                >
                  <X size={16} />
                </button>
              </>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="relative min-h-0 flex-1 overflow-auto p-6">
          {runError ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
              实验运行失败：{runError.message}
            </div>
          ) : activeTab === "visual" ? (
            <div
              className={`transition-opacity duration-200 ${
                isFetching ? "opacity-60" : "opacity-100"
              }`}
              // eslint-disable-next-line react/no-danger
              dangerouslySetInnerHTML={{ __html: result?.svg ?? "" }}
            />
          ) : activeTab === "data" ? (
            <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
              <h4 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
                计算数据
              </h4>
              <pre className="max-h-[60vh] overflow-auto text-xs text-slate-600 dark:text-slate-400">
                {result ? JSON.stringify(result.data, null, 2) : "暂无数据"}
              </pre>
            </div>
          ) : (
            <div className="space-y-4">
              {result?.warnings.length ? (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-900 dark:bg-amber-950/30">
                  <div className="mb-1 flex items-center gap-1 text-sm font-semibold text-amber-800 dark:text-amber-400">
                    <AlertTriangle size={14} />
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
                  <div className="mb-1 flex items-center gap-1 text-sm font-semibold text-indigo-800 dark:text-indigo-400">
                    <Lightbulb size={14} />
                    学习提示
                  </div>
                  <ul className="list-inside list-disc text-sm text-indigo-700 dark:text-indigo-300">
                    {result.learning_hints.map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  暂无学习提示
                </p>
              )}
            </div>
          )}

          {isFetching && (
            <div className="absolute right-4 top-4">
              <Loader2 className="animate-spin text-indigo-500" size={20} />
            </div>
          )}
        </div>

        {/* Optional bottom data panel (legacy toggle) */}
        {showDataPanel && result && activeTab === "visual" && (
          <div className="border-t border-slate-200/60 bg-slate-50/80 p-4 dark:border-slate-700/60 dark:bg-slate-900/50">
            <div className="grid grid-cols-2 gap-3 text-xs md:grid-cols-4">
              {Object.entries(result.data)
                .filter(([, v]) =>
                  ["string", "number", "boolean"].includes(typeof v)
                )
                .slice(0, 8)
                .map(([k, v]) => (
                  <div
                    key={k}
                    className="rounded-md border border-slate-200 bg-white p-2 dark:border-slate-700 dark:bg-slate-800"
                  >
                    <div className="text-slate-400">{k}</div>
                    <div className="font-medium text-slate-700 dark:text-slate-300">
                      {String(v)}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </main>
    </div>
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
