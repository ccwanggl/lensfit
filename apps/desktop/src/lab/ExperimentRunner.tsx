import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, BookOpen, ChevronDown, ChevronUp, FlaskConical, Loader2, X } from "lucide-react";
import { getLabExperiment, LabExperiment, runLabExperiment } from "../utils/api";
import { useLabStore } from "../stores/labStore";
import { ParameterControl } from "./ParameterControl";

interface ExperimentRunnerProps {
  experimentId: string;
}

export function ExperimentRunner({ experimentId }: ExperimentRunnerProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["lab-experiment", experimentId],
    queryFn: () => getLabExperiment(experimentId),
  });

  const experiment = data?.items[0];

  if (isLoading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
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

  return <Runner experiment={experiment} />;
}

function Runner({ experiment }: { experiment: LabExperiment }) {
  const paramDrafts = useLabStore((s) => s.paramDrafts[experiment.id] ?? {});
  const setParams = useLabStore((s) => s.setParams);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);
  const showDataPanel = useLabStore((s) => s.showDataPanel);
  const toggleDataPanel = useLabStore((s) => s.toggleDataPanel);

  const initialParams = useMemo(() => {
    const defaults: Record<string, unknown> = {};
    for (const p of experiment.parameters) {
      defaults[p.name] = paramDrafts[p.name] ?? p.default;
    }
    return defaults;
  }, [experiment, paramDrafts]);

  const [params, setLocalParams] = useState(initialParams);
  const [debouncedParams, setDebouncedParams] = useState(initialParams);

  // Sync local state when persisted drafts change
  useEffect(() => {
    setLocalParams(initialParams);
  }, [initialParams]);

  // Debounce run params
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedParams(params), 150);
    return () => clearTimeout(timer);
  }, [params]);

  const {
    data: result,
    isFetching,
    error: runError,
  } = useQuery({
    queryKey: ["lab-run", experiment.id, debouncedParams],
    queryFn: () => runLabExperiment(experiment.id, debouncedParams),
    enabled: !!experiment,
  });

  const handleChange = (name: string, value: unknown) => {
    const next = { ...params, [name]: value };
    setLocalParams(next);
    setParams(experiment.id, { [name]: value });
  };

  const difficultyClass = {
    foundation: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    intermediate: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    advanced: "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400",
  }[experiment.difficulty] ?? "bg-slate-100 text-slate-700";

  return (
    <div className="flex h-full flex-col gap-5 lg:flex-row">
      {/* Controls */}
      <aside className="w-full shrink-0 rounded-[14px] border border-slate-200/60 bg-white/80 p-5 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80 lg:w-80">
        <div className="mb-4 flex items-center gap-2">
          <FlaskConical size={18} className="text-indigo-500" />
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">{experiment.title}</h2>
        </div>
        <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">{experiment.description}</p>
        <div className="mb-4 flex flex-wrap gap-2">
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${difficultyClass}`}>
            {experiment.difficulty === "foundation" ? "基础" : experiment.difficulty === "intermediate" ? "进阶" : "高级"}
          </span>
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

        {experiment.learning_objectives.length > 0 && (
          <div className="mt-6 rounded-lg bg-indigo-50 p-3 dark:bg-indigo-900/20">
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
                    href={`obsidian://open?vault=OpticKnowledgeSpace&file=${encodeURIComponent(concept)}`}
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

      {/* Visualization */}
      <main className="flex flex-1 flex-col rounded-[14px] border border-slate-200/60 bg-white/80 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
        <div className="flex items-center justify-between border-b border-slate-200/60 px-5 py-3 dark:border-slate-700/60">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveExperimentId(null)}
              className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 lg:hidden dark:hover:bg-slate-700 dark:hover:text-slate-300"
              title="返回列表"
            >
              <ArrowLeft size={16} />
            </button>
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">实验结果</h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleDataPanel}
              className="flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-medium text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700"
            >
              {showDataPanel ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              {showDataPanel ? "收起数据" : "展开数据"}
            </button>
            <button
              onClick={() => setActiveExperimentId(null)}
              className="hidden rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 lg:block dark:hover:bg-slate-700 dark:hover:text-slate-300"
              title="关闭实验"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        <div className="relative flex flex-1 items-center justify-center overflow-auto p-6">
          {isFetching && (
            <div className="absolute right-4 top-4">
              <Loader2 className="animate-spin text-indigo-500" size={20} />
            </div>
          )}

          {runError ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
              实验运行失败：{runError.message}
            </div>
          ) : result ? (
            <div
              className="w-full max-w-3xl"
              // eslint-disable-next-line react/no-danger
              dangerouslySetInnerHTML={{ __html: result.svg }}
            />
          ) : null}
        </div>

        {showDataPanel && result && (
          <div className="border-t border-slate-200/60 bg-slate-50/80 p-5 dark:border-slate-700/60 dark:bg-slate-900/50">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {result.warnings.length > 0 && (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-900 dark:bg-amber-950/30 md:col-span-2">
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
              )}

              {result.learning_hints.length > 0 && (
                <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-3 dark:border-indigo-900 dark:bg-indigo-950/30">
                  <div className="mb-1 text-sm font-semibold text-indigo-800 dark:text-indigo-400">学习提示</div>
                  <ul className="list-inside list-disc text-sm text-indigo-700 dark:text-indigo-300">
                    {result.learning_hints.map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
                <div className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-300">计算数据</div>
                <pre className="max-h-48 overflow-auto text-xs text-slate-600 dark:text-slate-400">
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
