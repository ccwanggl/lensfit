interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error" | "info" | "neutral";
  size?: "sm" | "md";
  className?: string;
}

export default function Badge({
  children,
  variant = "default",
  size = "sm",
  className = "",
}: BadgeProps) {
  const variants: Record<string, string> = {
    default: "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 ring-indigo-500/20",
    success: "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 ring-emerald-500/20",
    warning: "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 ring-amber-500/20",
    error: "bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300 ring-rose-500/20",
    info: "bg-sky-50 dark:bg-sky-900/30 text-sky-700 dark:text-sky-300 ring-sky-500/20",
    neutral: "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 ring-slate-500/10",
  };

  const sizes: Record<string, string> = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1
        rounded-full font-semibold
        ring-1 ring-inset
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
    >
      {children}
    </span>
  );
}
