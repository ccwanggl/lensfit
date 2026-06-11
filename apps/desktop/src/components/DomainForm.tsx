import { useQuery } from "@tanstack/react-query";
import { Settings, Hash, Type, List, ToggleLeft } from "lucide-react";
import { Input } from "./ui";
import { type InputChangeEvent } from "./ui/Input";
import { getDomainParameters, type DomainParameterDef } from "../utils/api";
import { useLearningMode } from "../contexts/LearningModeContext";

interface DomainFormProps {
  domain: string;
  values: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
  disabled?: boolean;
}

/** Educational hints for common parameters — shown in Learning Mode */
const PARAM_HINTS: Record<string, string> = {
  sensor_size: "传感器物理尺寸（对角线）。尺寸越大，单个像素能收集的光子越多，画质通常越好。详见 docs/learning/04-sensors.md",
  pixel_size_um: "单个像素的物理边长（μm）。像元越小，同等面积像素数越多，但进光量和动态范围可能下降。",
  target_width_mm: "需要拍摄的区域在水平方向的物理宽度（mm）。与传感器尺寸和工作距离共同决定所需焦距。",
  target_height_mm: "需要拍摄的区域在垂直方向的物理宽度（mm）。",
  working_distance_mm: "镜头前端到被测物体的距离（mm）。WD、视场和传感器尺寸共同决定所需焦距。",
  lens_type: "镜头类型决定了光学设计目标：FA（通用工业）、Telecentric（无透视畸变，精密测量）、Macro（近距离高倍率）等。",
  interface: "机械安装接口。C-mount 最常用（法兰距17.5mm），F-mount 用于大面阵。接口不匹配无法安装。",
  focal_length_mm: "镜头焦距（mm）。焦距越短，视角越广；焦距越长，放大倍率越高。",
  f_number: "光圈值 F# = 焦距/入瞳直径。数字越小光圈越大，进光量越多，景深越浅。",
  magnification: "系统总放大倍率 β = 像高/物高。在显微镜中通常 >1；在摄影中通常 <1。",
  objective_na: "数值孔径 NA = n·sin(θ)。显微镜物镜最重要的参数，直接决定分辨率极限：d = 0.61λ/NA。",
  wavelength_nm: "照明光的波长（nm）。波长越短，衍射极限分辨率越高。可见光中心约 550nm（绿光）。",
  band: "红外波段：SWIR（短波红外，0.9–1.7μm）用于硅片检测；MWIR（3–5μm）用于高温；LWIR（8–14μm）用于常温热成像。",
  fov_deg: "视场角（度）。由焦距和传感器尺寸共同决定：AFOV = (360/π)·arctan(s/2f)。",
};

const TYPE_ICONS: Record<string, React.ReactNode> = {
  number: <Hash size={14} />,
  string: <Type size={14} />,
  enum: <List size={14} />,
  boolean: <ToggleLeft size={14} />,
};

/** Group parameter names by logical category */
const PARAM_GROUPS: Record<string, string[]> = {
  "传感器": ["sensor_size", "pixel_size_um"],
  "目标视场": ["target_width_mm", "target_height_mm"],
  "光学条件": ["working_distance_mm"],
  "镜头选型": ["lens_type", "interface"],
};

function ParameterField({
  def,
  value,
  onChange,
  disabled,
  learnHint,
}: {
  def: DomainParameterDef;
  value: unknown;
  onChange: (val: unknown) => void;
  disabled?: boolean;
  learnHint?: string;
}) {
  const { label, type, unit, default: defaultVal, required, options, min_value, max_value } = def;
  const currentValue = value !== undefined ? value : defaultVal;

  if (type === "enum" && options && options.length > 0) {
    return (
      <Input
        as="select"
        label={label}
        icon={TYPE_ICONS[type] || <Settings size={14} />}
        unit={unit || undefined}
        value={String(currentValue ?? "")}
        disabled={disabled}
        layout="horizontal"
        learnHint={learnHint}
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
        unit={unit || undefined}
        value={numValue}
        disabled={disabled}
        min={min_value ?? undefined}
        max={max_value ?? undefined}
        step="any"
        layout="horizontal"
        learnHint={learnHint}
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
      <div className="flex items-center gap-2">
        <span className="w-20 shrink-0 text-xs font-semibold text-slate-600 dark:text-slate-300 text-right leading-none">
          {label}
        </span>
        <label className="flex items-center gap-2 p-2 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700 cursor-pointer hover:border-slate-300 dark:hover:border-slate-600 transition-colors flex-1">
          <input
            type="checkbox"
            checked={!!currentValue}
            disabled={disabled}
            onChange={(e) => onChange(e.target.checked)}
            className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-sm text-slate-700 dark:text-slate-300">{currentValue ? "是" : "否"}</span>
        </label>
      </div>
    );
  }

  // Default: text input
  return (
    <Input
      type="text"
      label={label}
      icon={TYPE_ICONS[type] || <Settings size={14} />}
      unit={unit || undefined}
      value={String(currentValue ?? "")}
      disabled={disabled}
      required={required}
      layout="horizontal"
      learnHint={learnHint}
      onChange={(e: InputChangeEvent) => onChange(e.target.value)}
    />
  );
}

export default function DomainForm({ domain, values, onChange, disabled }: DomainFormProps) {
  const { learningMode } = useLearningMode();
  const { data, isLoading, error } = useQuery({
    queryKey: ["domainParams", domain],
    queryFn: () => getDomainParameters(domain),
    staleTime: Infinity,
  });

  if (isLoading) {
    return (
      <div className="space-y-2 animate-pulse">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-9 bg-slate-100 dark:bg-slate-800 rounded-[10px]" />
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

  // Build a lookup map for quick access
  const paramMap = new Map(data.parameters.map((p) => [p.name, p]));

  // Determine which params belong to a group vs ungrouped
  const groupedNames = new Set(Object.values(PARAM_GROUPS).flat());
  const ungroupedParams = data.parameters.filter((p) => !groupedNames.has(p.name));

  return (
    <div className="space-y-3">
      {Object.entries(PARAM_GROUPS).map(([groupName, paramNames]) => {
        const groupParams = paramNames
          .map((name) => paramMap.get(name))
          .filter(Boolean) as DomainParameterDef[];
        if (groupParams.length === 0) return null;

        return (
          <div key={groupName} className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
            <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">
              {groupName}
            </p>
            <div className="space-y-2">
              {groupParams.map((param) => (
                <ParameterField
                  key={param.name}
                  def={param}
                  value={values[param.name]}
                  onChange={(val) => onChange(param.name, val)}
                  disabled={disabled}
                  learnHint={learningMode ? PARAM_HINTS[param.name] : undefined}
                />
              ))}
            </div>
          </div>
        );
      })}

      {/* Ungrouped params (fallback for dynamic domains) */}
      {ungroupedParams.length > 0 && (
        <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
          {ungroupedParams.map((param) => (
            <ParameterField
              key={param.name}
              def={param}
              value={values[param.name]}
              onChange={(val) => onChange(param.name, val)}
              disabled={disabled}
              learnHint={learningMode ? PARAM_HINTS[param.name] : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}
