import { useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BookOpen, FlaskConical, Loader2 } from "lucide-react";
import {
  getContentConcept,
  listContentConcepts,
  listContentQuizzes,
  type ContentConcept,
} from "../utils/api";
import { useLabStore } from "../stores/labStore";
import { MarkdownView } from "./MarkdownView";
import QuizPanel from "./QuizPanel";
import { useReportProgress } from "./reportProgress";

const MODULE_LABELS: Record<string, string> = {
  "10-foundations": "光学基础",
  "20-geometric-optics": "几何光学",
  "30-wave-optics": "波动光学",
  "40-spectroscopy": "光谱学",
  "50-optical-design": "光学设计",
};

function moduleLabel(module: string): string {
  return MODULE_LABELS[module] ?? module;
}

const DIFFICULTY_LABELS: Record<string, string> = {
  foundation: "基础",
  intermediate: "进阶",
  advanced: "高级",
};

export default function TutorialView() {
  const activeConceptId = useLabStore((s) => s.activeConceptId);
  const setActiveConceptId = useLabStore((s) => s.setActiveConceptId);

  const { data, isLoading, error } = useQuery({
    queryKey: ["content-concepts"],
    queryFn: listContentConcepts,
  });

  const grouped = useMemo(() => {
    const groups = new Map<string, ContentConcept[]>();
    for (const item of data?.items ?? []) {
      const list = groups.get(item.module) ?? [];
      list.push(item);
      groups.set(item.module, list);
    }
    return [...groups.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={32} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        加载教程列表失败：{error.message}
      </div>
    );
  }

  return (
    <div className="flex h-full gap-4">
      {/* Concept list grouped by module */}
      <aside className="flex h-full w-72 shrink-0 flex-col gap-3 overflow-auto rounded-[14px] border border-slate-200/60 bg-white/80 p-4 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
        <div className="flex items-center gap-2">
          <BookOpen size={18} className="text-indigo-500" />
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">教程</h2>
        </div>

        {data?.errors.length ? (
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-700 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300">
            <div className="mb-1 flex items-center gap-1 font-semibold">
              <AlertTriangle size={12} />
              {data.errors.length} 篇文档未通过内容合同校验
            </div>
            {data.errors.map((e) => (
              <div key={e.path} className="mt-1 break-all">
                {e.path}
              </div>
            ))}
          </div>
        ) : null}

        {grouped.length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            暂无已收录的教程内容。
          </p>
        ) : (
          grouped.map(([module, items]) => (
            <div key={module}>
              <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                {moduleLabel(module)}
                <span className="ml-1 font-normal normal-case text-slate-400">
                  {module}
                </span>
              </h3>
              <ul className="space-y-1">
                {items.map((item) => {
                  const active = item.id === activeConceptId;
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => setActiveConceptId(item.id)}
                        className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                          active
                            ? "border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-800/40 dark:bg-indigo-900/30 dark:text-indigo-300"
                            : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                        }`}
                      >
                        <span className="min-w-0 truncate font-medium">{item.title}</span>
                        <span className="ml-2 shrink-0 text-xs text-slate-400">
                          {DIFFICULTY_LABELS[item.difficulty] ?? item.difficulty}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))
        )}
      </aside>

      {/* Concept detail */}
      <main className="min-w-0 flex-1 overflow-auto rounded-[14px] border border-slate-200/60 bg-white/80 p-4 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
        {activeConceptId ? (
          <ConceptDetail conceptId={activeConceptId} />
        ) : (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-500 dark:bg-indigo-900/30 dark:text-indigo-400">
              <BookOpen size={28} />
            </div>
            <h2 className="mb-2 text-lg font-semibold text-slate-800 dark:text-slate-200">
              选择一篇教程开始阅读
            </h2>
            <p className="max-w-md text-sm text-slate-500 dark:text-slate-400">
              教程按模块分组，文中会链接相关的实验，可直接跳转到实验沙盘动手验证。
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

function ConceptDetail({ conceptId }: { conceptId: string }) {
  const openExperimentFromTutorial = useLabStore((s) => s.openExperimentFromTutorial);
  const reportProgress = useReportProgress();

  const { data, isLoading, error } = useQuery({
    queryKey: ["content-concept", conceptId],
    queryFn: () => getContentConcept(conceptId),
  });

  // 教程加载成功后上报 viewed（同一教程只上报一次）
  useEffect(() => {
    if (data) {
      reportProgress("concept", data.id, "viewed");
    }
  }, [data, reportProgress]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={28} />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        无法加载教程：{error?.message ?? "未找到概念"}
      </div>
    );
  }

  return (
    <article>
      <header className="mb-4 border-b border-slate-200/60 pb-3 dark:border-slate-700/60">
        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">
          {data.title}
        </h1>
        <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <span>{moduleLabel(data.module)}</span>
          <span>·</span>
          <span>{DIFFICULTY_LABELS[data.difficulty] ?? data.difficulty}</span>
          {data.status === "draft" && (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 font-semibold text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
              草稿
            </span>
          )}
        </div>
        {data.linked_experiments.length > 0 && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
              关联实验：
            </span>
            {data.linked_experiments.map((expId) => (
              <button
                key={expId}
                onClick={() => openExperimentFromTutorial(expId)}
                className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-100 dark:border-emerald-800/40 dark:bg-emerald-900/30 dark:text-emerald-400 dark:hover:bg-emerald-900/50"
              >
                <FlaskConical size={12} />
                {expId}
              </button>
            ))}
          </div>
        )}
      </header>
      <MarkdownView markdown={data.body} />
      <LinkedQuizzes conceptId={data.id} />
    </article>
  );
}

/** 概念配套测验：学完教程后可直接做，成绩上报为 scored 记录。 */
function LinkedQuizzes({ conceptId }: { conceptId: string }) {
  const { data } = useQuery({
    queryKey: ["content-quizzes", conceptId],
    queryFn: () => listContentQuizzes(conceptId),
  });

  const quizzes = data?.items ?? [];
  if (quizzes.length === 0) return null;

  return (
    <section className="mt-4 border-t border-slate-200/60 pt-3 dark:border-slate-700/60">
      <h2 className="mb-3 text-sm font-bold text-slate-800 dark:text-slate-200">
        配套测验
      </h2>
      <div className="space-y-3">
        {quizzes.map((quiz) => (
          <QuizPanel key={quiz.id} quizId={quiz.id} />
        ))}
      </div>
    </section>
  );
}
