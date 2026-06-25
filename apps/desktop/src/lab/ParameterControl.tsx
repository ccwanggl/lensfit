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
  const label = (
    <span className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
      {param.label}
      {param.unit && <span className="text-xs text-slate-400">({param.unit})</span>}
    </span>
  );

  if (param.type === "bool") {
    const boolValue = Boolean(value ?? param.default);
    return (
      <label className="flex items-center justify-between gap-3 py-2">
        {label}
        <input
          type="checkbox"
          checked={boolValue}
          onChange={(e) => onChange(e.target.checked)}
          className="h-5 w-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
        />
      </label>
    );
  }

  if (param.type === "choice" || param.type === "enum") {
    const options = param.options ?? [];
    const selected = value ?? param.default;
    return (
      <label className="flex flex-col gap-2 py-2">
        {label}
        <select
          value={String(selected)}
          onChange={(e) => {
            const opt = options.find((o) => String(o.value) === e.target.value);
            onChange(opt?.value ?? e.target.value);
          }}
          className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100"
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
  const numericValue = value !== undefined ? Number(value) : Number(param.default);
  return (
    <label className="flex flex-col gap-2 py-2">
      <div className="flex items-center justify-between">
        {label}
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={numericValue}
          onChange={(e) => onChange(param.type === "int" ? parseInt(e.target.value, 10) : parseFloat(e.target.value))}
          className="w-24 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-2 py-1 text-right text-sm text-slate-900 dark:text-slate-100"
        />
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={numericValue}
        onChange={(e) => onChange(param.type === "int" ? parseInt(e.target.value, 10) : parseFloat(e.target.value))}
        className="w-full accent-indigo-600"
      />
    </label>
  );
}
