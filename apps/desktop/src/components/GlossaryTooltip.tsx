import { useState, useRef, useEffect } from "react";
import { HelpCircle } from "lucide-react";
import { lookupGlossary } from "./OpticalGlossary";

interface Props {
  term: string;
  children: React.ReactNode;
  showIcon?: boolean;
}

export default function GlossaryTooltip({ term, children, showIcon = false }: Props) {
  const [open, setOpen] = useState(false);
  const entry = lookupGlossary(term);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!open) return;
    const handle = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, [open]);

  if (!entry) {
    return <>{children}</>;
  }

  return (
    <span ref={ref} className="relative inline-flex items-center gap-0.5">
      <span
        className="cursor-help border-b border-dashed border-slate-400/60 dark:border-slate-500/60 hover:border-sky-400 dark:hover:border-sky-400 transition-colors"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={() => setOpen((v) => !v)}
      >
        {children}
      </span>
      {showIcon && (
        <HelpCircle
          size={12}
          className="text-slate-400 dark:text-slate-500 cursor-help"
          onMouseEnter={() => setOpen(true)}
          onMouseLeave={() => setOpen(false)}
        />
      )}

      {open && (
        <span className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 rounded-xl bg-white dark:bg-slate-800 shadow-xl border border-slate-200 dark:border-slate-700 text-xs leading-relaxed text-slate-700 dark:text-slate-200">
          <span className="font-semibold text-slate-900 dark:text-white block mb-1">
            {entry.term}
          </span>
          {entry.explanation}
          {entry.related && entry.related.length > 0 && (
            <span className="block mt-2 text-xs text-slate-400 dark:text-slate-500">
              相关：{entry.related.map((r) => lookupGlossary(r)?.term ?? r).join("、")}
            </span>
          )}
          <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-white dark:border-t-slate-800" />
        </span>
      )}
    </span>
  );
}
