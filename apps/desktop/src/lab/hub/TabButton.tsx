/** Shared pill-style tab button (moved verbatim from LearningHub, slice B). */
import type { ReactNode } from "react";

export function TabButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: ReactNode;
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
