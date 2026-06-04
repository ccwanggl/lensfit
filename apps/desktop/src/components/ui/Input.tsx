import { type ReactNode, forwardRef, type InputHTMLAttributes } from "react";

export type InputChangeEvent = React.ChangeEvent<HTMLInputElement | HTMLSelectElement>;

interface InputProps extends InputHTMLAttributes<HTMLInputElement | HTMLSelectElement> {
  label?: string;
  icon?: ReactNode;
  error?: string;
  helper?: string;
  as?: "input" | "select";
}

const Input = forwardRef<HTMLInputElement | HTMLSelectElement, InputProps>(
  ({ label, icon, error, helper, className = "", as = "input", ...props }, ref) => {
    const sharedClasses = `
      w-full bg-slate-50/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700
      rounded-[10px] px-3 py-2.5 text-[13px] text-slate-800 dark:text-slate-200
      placeholder:text-slate-400 dark:placeholder:text-slate-500
      transition-all duration-200 ease-out
      focus:outline-none focus:bg-white dark:focus:bg-slate-800
      focus:border-indigo-400 focus:ring-[3px] focus:ring-indigo-100
      hover:border-slate-300 dark:hover:border-slate-600
      ${error ? "border-rose-300 focus:border-rose-400 focus:ring-rose-100" : ""}
      ${icon ? "pl-10" : ""}
      ${className}
    `;

    return (
      <div className="w-full">
        {label && (
          <label className="block text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1.5">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none">
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
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>
          )}
        </div>
        {error && <p className="mt-1.5 text-xs text-rose-500 font-medium">{error}</p>}
        {helper && !error && <p className="mt-1.5 text-xs text-slate-400 dark:text-slate-500">{helper}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
