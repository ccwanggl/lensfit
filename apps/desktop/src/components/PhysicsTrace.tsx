import { useState } from "react";
import { ChevronDown, ChevronUp, FlaskConical } from "lucide-react";

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

export default function PhysicsTrace({ traces }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!traces || traces.length === 0) return null;

  return (
    <div className="mt-4">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
      >
        <FlaskConical size={14} />
        推导详情
        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {expanded && (
        <div className="mt-2 space-y-2">
          {traces.map((t, i) => (
            <div
              key={i}
              className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">{t.formula}</span>
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 tabular-nums">
                  {t.output.toFixed ? t.output.toFixed(4) : t.output} {t.unit}
                </span>
              </div>
              <div className="text-[10px] text-slate-400 dark:text-slate-500">
                {Object.entries(t.inputs).map(([k, v]) => (
                  <span key={k} className="mr-2">
                    {k}={typeof v === "number" && v.toFixed ? v.toFixed(2) : v}
                  </span>
                ))}
              </div>
              {t.assumption && (
                <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 italic">
                  * {t.assumption}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
