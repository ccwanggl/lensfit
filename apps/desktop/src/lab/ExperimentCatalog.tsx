import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FlaskConical, Loader2, Search } from "lucide-react";
import { listLabExperiments } from "../utils/api";
import { useLabStore } from "../stores/labStore";

interface ExperimentCatalogProps {
  onSelect: (id: string) => void;
}

export function ExperimentCatalog({ onSelect }: ExperimentCatalogProps) {
  const [filter, setFilter] = useState("");
  const { data, isLoading, error } = useQuery({
    queryKey: ["lab-experiments"],
    queryFn: listLabExperiments,
  });
  const recent = useLabStore((s) => s.recentExperiments);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={24} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        加载实验列表失败：{error.message}
      </div>
    );
  }

  const items = data?.items ?? [];
  const filtered = items.filter(
    (e) =>
      e.title.toLowerCase().includes(filter.toLowerCase()) ||
      e.description.toLowerCase().includes(filter.toLowerCase()) ||
      e.linked_concepts.some((c) => c.toLowerCase().includes(filter.toLowerCase()))
  );

  const difficultyLabel = (d: string) => {
    if (d === "foundation") return "基础";
    if (d === "intermediate") return "进阶";
    return "高级";
  };

  return (
    <div className="flex h-full flex-col gap-4 rounded-[14px] border border-slate-200/60 bg-white/80 p-5 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
      <div className="flex items-center gap-2">
        <FlaskConical size={18} className="text-indigo-500" />
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">光学实验室</h2>
      </div>

      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="搜索实验或概念..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        />
      </div>

      {recent.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            最近运行
          </h3>
          <div className="flex flex-wrap gap-2">
            {recent.map((id) => {
              const exp = items.find((e) => e.id === id);
              if (!exp) return null;
              return (
                <button
                  key={id}
                  onClick={() => onSelect(id)}
                  className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700 hover:bg-indigo-100 hover:text-indigo-700 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-indigo-900/30 dark:hover:text-indigo-400"
                >
                  {exp.title}
                </button>
              );
            })}
          </div>
        </div>
      )}

      <div className="flex-1 space-y-2 overflow-auto">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          全部实验
        </h3>
        {filtered.map((exp) => (
          <button
            key={exp.id}
            onClick={() => onSelect(exp.id)}
            className="w-full rounded-xl border border-slate-200 bg-white p-4 text-left transition-all hover:border-indigo-300 hover:shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:hover:border-indigo-500"
          >
            <div className="mb-1 flex items-center justify-between">
              <span className="font-semibold text-slate-900 dark:text-slate-100">{exp.title}</span>
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                  exp.difficulty === "foundation"
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                    : exp.difficulty === "intermediate"
                    ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                    : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400"
                }`}
              >
                {difficultyLabel(exp.difficulty)}
              </span>
            </div>
            <p className="line-clamp-2 text-xs text-slate-600 dark:text-slate-400">{exp.description}</p>
            {exp.linked_concepts.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {exp.linked_concepts.slice(0, 3).map((c) => (
                  <span
                    key={c}
                    className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500 dark:bg-slate-700 dark:text-slate-400"
                  >
                    {c.split("/").pop()}
                  </span>
                ))}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
