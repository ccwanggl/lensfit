interface ProgressBarProps {
  value: number;
  max?: number;
  size?: "sm" | "md" | "lg";
  label?: string;
  showValue?: boolean;
  color?: "indigo" | "emerald" | "amber" | "rose";
}

export default function ProgressBar({
  value,
  max = 1,
  size = "md",
  label,
  showValue = true,
  color = "indigo",
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizes: Record<string, string> = {
    sm: "h-1",
    md: "h-1.5",
    lg: "h-2.5",
  };

  const colors: Record<string, string> = {
    indigo: "bg-gradient-to-r from-indigo-500 to-violet-500",
    emerald: "bg-gradient-to-r from-emerald-500 to-teal-500",
    amber: "bg-gradient-to-r from-amber-500 to-orange-500",
    rose: "bg-gradient-to-r from-rose-500 to-pink-500",
  };

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-1.5">
          {label && (
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {label}
            </span>
          )}
          {showValue && (
            <span className="text-xs font-bold text-slate-700 dark:text-slate-300 tabular-nums">
              {percentage.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div
        className={`
          w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden
          ${sizes[size]}
        `}
      >
        <div
          className={`
            ${colors[color]} rounded-full
            transition-all duration-500 ease-out
          `}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
