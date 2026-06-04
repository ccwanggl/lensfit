import { useQuery } from "@tanstack/react-query";
import { Settings, Hash, Type, List, ToggleLeft } from "lucide-react";
import { Input } from "./ui";
import { type InputChangeEvent } from "./ui/Input";
import { getDomainParameters, type DomainParameterDef } from "../utils/api";

interface DomainFormProps {
  domain: string;
  values: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
  disabled?: boolean;
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  number: <Hash size={14} />,
  string: <Type size={14} />,
  enum: <List size={14} />,
  boolean: <ToggleLeft size={14} />,
};

function ParameterField({
  def,
  value,
  onChange,
  disabled,
}: {
  def: DomainParameterDef;
  value: unknown;
  onChange: (val: unknown) => void;
  disabled?: boolean;
}) {
  const { label, type, unit, default: defaultVal, required, options, min_value, max_value, description } = def;

  const helper = [unit || "", description || ""].filter(Boolean).join(" · ");

  const currentValue = value !== undefined ? value : defaultVal;

  if (type === "enum" && options && options.length > 0) {
    return (
      <Input
        as="select"
        label={label}
        icon={TYPE_ICONS[type] || <Settings size={14} />}
        helper={helper || undefined}
        value={String(currentValue ?? "")}
        disabled={disabled}
        onChange={(e: InputChangeEvent) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </Input>
    );
  }

  if (type === "number") {
    const numValue = typeof currentValue === "number" ? currentValue : (typeof defaultVal === "number" ? defaultVal : 0);
    return (
      <Input
        type="number"
        label={label}
        icon={TYPE_ICONS[type] || <Settings size={14} />}
        helper={helper || undefined}
        value={numValue}
        disabled={disabled}
        min={min_value ?? undefined}
        max={max_value ?? undefined}
        step="any"
        onChange={(e: InputChangeEvent) => {
          const v = e.target.value;
          if (v === "") {
            onChange(defaultVal ?? 0);
          } else {
            const n = parseFloat(v);
            onChange(Number.isFinite(n) ? n : defaultVal ?? 0);
          }
        }}
      />
    );
  }

  if (type === "boolean") {
    return (
      <label className="flex items-center gap-3 p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700 cursor-pointer hover:border-slate-300 dark:hover:border-slate-600 transition-colors">
        <input
          type="checkbox"
          checked={!!currentValue}
          disabled={disabled}
          onChange={(e) => onChange(e.target.checked)}
          className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
        />
        <div>
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">{label}</span>
          {description && <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{description}</p>}
        </div>
      </label>
    );
  }

  // Default: text input
  return (
    <Input
      type="text"
      label={label}
      icon={TYPE_ICONS[type] || <Settings size={14} />}
      helper={helper || undefined}
      value={String(currentValue ?? "")}
      disabled={disabled}
      required={required}
      onChange={(e: InputChangeEvent) => onChange(e.target.value)}
    />
  );
}

export default function DomainForm({ domain, values, onChange, disabled }: DomainFormProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["domainParams", domain],
    queryFn: () => getDomainParameters(domain),
    staleTime: Infinity, // Domain definitions rarely change
  });

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-10 bg-slate-100 dark:bg-slate-800 rounded-[10px]" />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-900/20 border border-rose-100 dark:border-rose-800/30">
        <p className="text-sm font-semibold text-rose-700 dark:text-rose-300">无法加载参数定义</p>
        <p className="text-xs text-rose-600 dark:text-rose-400 mt-1">请检查后端服务是否正常运行</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {data.parameters.map((param) => (
        <ParameterField
          key={param.name}
          def={param}
          value={values[param.name]}
          onChange={(val) => onChange(param.name, val)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}
