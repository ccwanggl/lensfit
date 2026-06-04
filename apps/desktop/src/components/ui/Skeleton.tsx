interface SkeletonProps {
  className?: string;
  variant?: "rect" | "circle" | "text" | "card";
  lines?: number;
}

export default function Skeleton({
  className = "",
  variant = "rect",
  lines = 1,
}: SkeletonProps) {
  const base =
    "bg-slate-200/70 dark:bg-slate-700/70 rounded-md animate-pulse";

  const variants: Record<string, string> = {
    rect: "",
    circle: "rounded-full",
    text: "h-3 rounded",
    card: "rounded-xl",
  };

  if (variant === "text" && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`${base} ${variants.text} w-full`}
            style={{
              width: i === lines - 1 ? `${60 + Math.random() * 30}%` : "100%",
            }}
          />
        ))}
      </div>
    );
  }

  return <div className={`${base} ${variants[variant]} ${className}`} />;
}

/* ─── Result Card Skeleton ─── */
export function ResultCardSkeleton() {
  return (
    <div className="flex items-start gap-3 p-4 rounded-xl border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800">
      <Skeleton variant="circle" className="w-7 h-7 flex-shrink-0" />
      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center justify-between">
          <Skeleton variant="text" className="w-32" />
          <Skeleton variant="text" className="w-10" />
        </div>
        <Skeleton variant="text" className="w-24" />
        <div className="flex gap-2 pt-1">
          <Skeleton variant="text" className="w-16 h-5 rounded-full" />
          <Skeleton variant="text" className="w-14 h-5 rounded-full" />
        </div>
        <Skeleton variant="rect" className="w-full h-1 rounded-full mt-1" />
      </div>
    </div>
  );
}

/* ─── Coverage Plot Skeleton ─── */
export function CoverageSkeleton({ width = 320, height = 280 }: { width?: number; height?: number }) {
  return (
    <div
      className="flex items-center justify-center rounded-[14px] border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/60"
      style={{ width, height }}
    >
      <div className="flex flex-col items-center gap-3">
        <Skeleton variant="circle" className="w-16 h-16" />
        <Skeleton variant="text" className="w-32" />
        <Skeleton variant="text" className="w-20" />
      </div>
    </div>
  );
}
