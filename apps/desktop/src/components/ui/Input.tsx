import { type ReactNode, forwardRef, type InputHTMLAttributes, useState } from "react";
import { HelpCircle } from "lucide-react";

export type InputChangeEvent = React.ChangeEvent<HTMLInputElement | HTMLSelectElement>;

interface InputProps extends InputHTMLAttributes<HTMLInputElement | HTMLSelectElement> {
  label?: string;
  icon?: ReactNode;
  error?: string;
  helper?: string;
  unit?: string;
  as?: "input" | "select";
  compact?: boolean;
  layout?: "vertical" | "horizontal";
  learnHint?: string;
}

const Input = forwardRef<HTMLInputElement | HTMLSelectElement, InputProps>(
  ({ label, icon, error, helper, unit, className = "", as = "input", compact = false, layout = "vertical", learnHint, ...props }, ref) => {
    const [showHint, setShowHint] = useState(false);
    const isHorizontal = layout === "horizontal";

    const sharedClasses = `
      w-full bg-slate-50/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700
      rounded-[10px] px-3 ${isHorizontal ? "h-7 py-0 text-[13px]" : compact ? "py-2 text-[13px]" : "py-2.5 text-[13px]"} text-slate-800 dark:text-slate-200
      placeholder:text-slate-400 dark:placeholder:text-slate-500
      transition-all duration-200 ease-out
      focus:outline-none focus:bg-white dark:focus:bg-slate-800
      focus:border-indigo-400 focus:ring-[3px] focus:ring-indigo-100
      hover:border-slate-300 dark:hover:border-slate-600
      ${error ? "border-rose-300 focus:border-rose-400 focus:ring-rose-100" : ""}
      ${icon ? (isHorizontal ? "pl-9" : "pl-10") : ""}
      ${className}
    `;

    const inputWrap = (
      <div className={`relative ${isHorizontal ? "flex-1 min-w-0" : "w-full"}`}>
        {icon && (
          <div className={`absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none ${isHorizontal ? "scale-90" : ""}`}>
            {icon}
          </div>
        )}
        {as === "input" ? (
          <input
            ref={ref as React.Ref<HTMLInputElement>}
            className={sharedClasses}
            {...(props as InputHTMLAttributes<HTMLInputElement>)}
          />
        ) : (
          <select
            ref={ref as React.Ref<HTMLSelectElement>}
            className={`${sharedClasses} appearance-none cursor-pointer`}
            {...(props as InputHTMLAttributes<HTMLSelectElement>)}
          >
            {props.children}
          </select>
        )}
        {as === "select" && (
          <div className={`absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none ${isHorizontal ? "scale-90" : ""}`}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m6 9 6 6 6-6" />
            </svg>
          </div>
        )}
      </div>
    );

    const hintNode = learnHint ? (
      <div className="relative inline-flex items-center">
        <button
          type="button"
          className="ml-1 text-slate-400 dark:text-slate-500 hover:text-indigo-500 dark:hover:text-indigo-400 transition-colors"
          onMouseEnter={() => setShowHint(true)}
          onMouseLeave={() => setShowHint(false)}
          onClick={() => setShowHint(!showHint)}
        >
          <HelpCircle size={12} />
        </button>
        {showHint && (
          <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-1.5 w-56 p-2.5 rounded-lg bg-slate-800 dark:bg-slate-700 text-slate-100 text-xs leading-relaxed shadow-xl border border-slate-600">
            {learnHint}
            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-4 border-transparent border-t-slate-800 dark:border-t-slate-700" />
          </div>
        )}
      </div>
    ) : null;

    if (isHorizontal) {
      return (
        <div className="w-full flex items-center gap-2">
          {label && (
            <label className="w-20 shrink-0 text-xs font-semibold text-slate-600 dark:text-slate-300 text-right leading-none flex items-center justify-end">
              {label}
              {hintNode}
            </label>
          )}
          {inputWrap}
          {(unit || helper) && (
            <span className="shrink-0 w-8 text-xs text-slate-400 dark:text-slate-500 tabular-nums text-right">
              {unit || helper}
            </span>
          )}
        </div>
      );
    }

    return (
      <div className="w-full">
        {label && (
          <label className={`flex items-center text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider ${compact ? "mb-1" : "mb-1.5"}`}>
            {label}
            {hintNode}
          </label>
        )}
        {inputWrap}
        {error && <p className={`${compact ? "mt-1" : "mt-1.5"} text-xs text-rose-500 font-medium`}>{error}</p>}
        {helper && !error && <p className={`${compact ? "mt-1" : "mt-1.5"} text-xs text-slate-400 dark:text-slate-500`}>{helper}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
