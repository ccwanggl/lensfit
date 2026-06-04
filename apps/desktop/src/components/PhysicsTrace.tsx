import { FlaskConical } from "lucide-react";

export interface PhysicsTraceItem {
  formula: string;
  inputs: Record<string, string | number>;
  output: number;
  unit: string;
  assumption: string;
}

interface Props {
  traces: PhysicsTraceItem[];
}

function formatValue(v: string | number): string {
  if (typeof v === "number") {
    if (Math.abs(v) >= 1000) return v.toFixed(0);
    if (Math.abs(v) >= 1) return v.toFixed(2);
    return v.toFixed(4);
  }
  return String(v);
}

export default function PhysicsTrace({ traces }: Props) {
  if (!traces || traces.length === 0) return null;

  return (
    <div className="mt-4">
      <h3 className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-3">
        <FlaskConical size={13} />
        推导过程
      </h3>

      <div className="relative pl-3">
        {/* vertical connector line */}
        <div className="absolute left-[11px] top-2 bottom-2 w-px bg-slate-200 dark:bg-slate-700" />

        <div className="space-y-0">
          {traces.map((t, i) => (
            <div key={i} className="relative flex items-start gap-3 py-2">
              {/* node dot */}
              <div className="relative z-10 mt-1.5 w-[22px] h-[22px] rounded-full bg-indigo-50 dark:bg-indigo-900/30 border-2 border-indigo-300 dark:border-indigo-700 flex items-center justify-center flex-shrink-0">
                <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 tabular-nums">
                  {i + 1}
                </span>
              </div>

              {/* content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                    {t.formula}
                  </span>
                  <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 tabular-nums flex-shrink-0">
                    {formatValue(t.output)} {t.unit}
                  </span>
                </div>

                {Object.keys(t.inputs).length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-x-2 gap-y-0.5">
                    {Object.entries(t.inputs).map(([k, v]) => (
                      <span
                        key={k}
                        className="text-[10px] text-slate-400 dark:text-slate-500 tabular-nums"
                      >
                        {k}={formatValue(v)}
                      </span>
                    ))}
                  </div>
                )}

                {t.assumption && (
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 italic">
                    * {t.assumption}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
