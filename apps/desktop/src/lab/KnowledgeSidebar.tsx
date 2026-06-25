import { BookOpen, Calculator, ExternalLink, Lightbulb } from "lucide-react";
import type { LabExperiment } from "../utils/api";

interface KnowledgeSidebarProps {
  experiment: LabExperiment | null;
}

function obsidianUrl(path: string): string {
  return `obsidian://open?vault=OpticKnowledgeSpace&file=${encodeURIComponent(
    path
  )}`;
}

function conceptName(path: string): string {
  return path.split("/").pop() ?? path;
}

export function KnowledgeSidebar({ experiment }: KnowledgeSidebarProps) {
  if (!experiment) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-[14px] border border-dashed border-slate-300 bg-white/50 p-6 text-center dark:border-slate-700 dark:bg-slate-800/50">
        <Lightbulb size={32} className="mb-3 text-slate-300 dark:text-slate-600" />
        <p className="text-sm text-slate-500 dark:text-slate-400">
          选择一个实验后，这里会展示它涉及的关键概念与公式。
        </p>
      </div>
    );
  }

  const hasConcepts = experiment.linked_concepts.length > 0;
  const hasFormulas = experiment.linked_formulas.length > 0;

  return (
    <div className="flex h-full flex-col gap-4 rounded-[14px] border border-slate-200/60 bg-white/80 p-5 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
      <div className="flex items-center gap-2">
        <BookOpen size={18} className="text-emerald-500" />
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
          关联知识点
        </h2>
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400">
        本实验与知识库中的以下概念和公式直接相关，点击可在 Obsidian 中打开。
      </p>

      {!hasConcepts && !hasFormulas && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          暂无关联知识点。
        </p>
      )}

      {hasConcepts && (
        <section className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            相关概念
          </h3>
          <div className="flex flex-wrap gap-2">
            {experiment.linked_concepts.map((concept) => (
              <a
                key={concept}
                href={obsidianUrl(concept)}
                target="_blank"
                rel="noreferrer"
                className="group inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 hover:border-emerald-300 hover:text-emerald-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-emerald-500 dark:hover:text-emerald-400"
              >
                <BookOpen size={12} />
                <span>{conceptName(concept)}</span>
                <ExternalLink
                  size={10}
                  className="ml-0.5 opacity-0 transition-opacity group-hover:opacity-100"
                />
              </a>
            ))}
          </div>
        </section>
      )}

      {hasFormulas && (
        <section className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            相关公式
          </h3>
          <div className="space-y-2">
            {experiment.linked_formulas.map((formula) => (
              <a
                key={formula}
                href={obsidianUrl(formula)}
                target="_blank"
                rel="noreferrer"
                className="group flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-indigo-500 dark:hover:text-indigo-400"
              >
                <span className="flex items-center gap-1.5">
                  <Calculator size={12} />
                  {conceptName(formula)}
                </span>
                <ExternalLink
                  size={10}
                  className="opacity-0 transition-opacity group-hover:opacity-100"
                />
              </a>
            ))}
          </div>
        </section>
      )}

      <div className="mt-auto rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
        <p className="text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          提示：参数调整会实时影响中间的模拟结果。右侧知识点可帮你把实验现象与理论公式联系起来。
        </p>
      </div>
    </div>
  );
}
