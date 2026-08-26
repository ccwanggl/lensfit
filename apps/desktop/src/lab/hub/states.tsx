/** Presentational states & badge for the sandbox display (slice B). */
import { FlaskConical, Loader2 } from "lucide-react";

export function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const cls =
    difficulty === "foundation"
      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
      : difficulty === "intermediate"
      ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
      : "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400";
  const label =
    difficulty === "foundation" ? "基础" : difficulty === "intermediate" ? "进阶" : "高级";
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${cls}`}>
      {label}
    </span>
  );
}

export function LoadingState() {
  return (
    <div className="flex h-full items-center justify-center">
      <Loader2 className="animate-spin text-indigo-500" size={32} />
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center p-4">
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        无法加载实验：{message}
      </div>
    </div>
  );
}

export function EmptyState({ onOpenCatalog }: { onOpenCatalog: () => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center rounded-[14px] border border-dashed border-slate-300 bg-white/50 p-6 text-center dark:border-slate-700 dark:bg-slate-800/50">
      <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-500 dark:bg-indigo-900/30 dark:text-indigo-400">
        <FlaskConical size={28} />
      </div>
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
