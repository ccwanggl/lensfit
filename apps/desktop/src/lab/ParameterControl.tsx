import { RotateCcw } from "lucide-react";
import { LabParameter } from "../utils/api";

interface ParameterControlProps {
  param: LabParameter;
  value: unknown;
  onChange: (value: unknown) => void;
}

export function ParameterControl({ param, value, onChange }: ParameterControlProps) {
  const min = param.min ?? undefined;
  const max = param.max ?? undefined;
  const step = param.step ?? (param.type === "int" ? 1 : 0.1);

  if (param.type === "bool") {
    const boolValue = Boolean(value ?? param.default);
    return (
      <label className="flex items-center justify-between gap-2 rounded-lg border border-slate-100 bg-white px-3 py-2 dark:border-slate-700/50 dark:bg-slate-800/50">
        <Label param={param} />
        <input
          type="checkbox"
          checked={boolValue}
          onChange={(e) => onChange(e.target.checked)}
          className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
        />
      </label>
    );
  }

  if (param.type === "choice" || param.type === "enum") {
    const options = param.options ?? [];
    const selected = value ?? param.default;
    return (
      <label className="flex flex-col gap-1.5 rounded-lg border border-slate-100 bg-white px-3 py-2 dark:border-slate-700/50 dark:bg-slate-800/50">
        <Label param={param} />
        <select
          value={String(selected)}
          onChange={(e) => {
            const opt = options.find((o) => String(o.value) === e.target.value);
            onChange(opt?.value ?? e.target.value);
          }}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        >
          {options.map((opt) => (
            <option key={String(opt.value)} value={String(opt.value)}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>
    );
  }

  // float / int
  const numericValue =
    value !== undefined ? Number(value) : Number(param.default);
  const isChanged = numericValue !== Number(param.default);

  return (
    <div className="rounded-lg border border-slate-100 bg-white px-3 py-2 transition-colors hover:border-slate-200 dark:border-slate-700/50 dark:bg-slate-800/50 dark:hover:border-slate-700">
      <div className="mb-1.5 flex items-center justify-between">
        <Label param={param} />
        <div className="flex items-center gap-2">
          <input
            type="number"
            min={min}
            max={max}
            step={step}
            value={numericValue}
            onChange={(e) =>
              onChange(
                param.type === "int"
                  ? parseInt(e.target.value, 10)
                  : parseFloat(e.target.value)
              )
            }
            className="w-24 rounded-lg border border-slate-200 bg-white px-2 py-1 text-right text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          />
          {isChanged && (
            <button
              onClick={() => onChange(param.default)}
              className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-300"
              title="恢复默认值" aria-label="恢复默认值"
            >
              <RotateCcw size={14} />
            </button>
          )}
        </div>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={numericValue}
        onInput={(e) =>
          onChange(
            param.type === "int"
              ? parseInt((e.target as HTMLInputElement).value, 10)
              : parseFloat((e.target as HTMLInputElement).value)
          )
        }
        className="w-full accent-indigo-600"
      />
    </div>
  );
}

function Label({ param }: { param: LabParameter }) {
  return (
    <span className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
      {param.label}
      {param.unit && (
        <span className="text-xs text-slate-400">({param.unit})</span>
      )}
    </span>
  );
}
