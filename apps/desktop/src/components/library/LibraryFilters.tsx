import { Package, Camera, Plus, Upload, Search, Database } from "lucide-react";
import { Card, Button, Input, SectionHeader } from "../ui";
import { type InputChangeEvent } from "../ui/Input";

export type Kind = "lens" | "detector";

interface Props {
  kind: Kind;
  onKindChange: (kind: Kind) => void;
  search: string;
  onSearchChange: (value: string) => void;
  sourceFilter: "all" | "seed" | "user";
  onSourceFilterChange: (value: "all" | "seed" | "user") => void;
  lensCount: number;
  detectorCount: number;
  onNew: () => void;
  onImport: () => void;
}

const KIND_CONFIG: Record<Kind, { label: string; icon: React.ReactNode; color: string }> = {
  lens: { label: "镜头", icon: <Package size={16} />, color: "text-indigo-500" },
  detector: { label: "探测器", icon: <Camera size={16} />, color: "text-emerald-500" },
};

export default function LibraryFilters({
  kind,
  onKindChange,
  search,
  onSearchChange,
  sourceFilter,
  onSourceFilterChange,
  lensCount,
  detectorCount,
  onNew,
  onImport,
}: Props) {
  return (
    <Card padding="none" className="overflow-hidden h-full flex flex-col">
      <div className="p-5 border-b border-slate-100 dark:border-slate-700">
        <SectionHeader title="器件库" subtitle="管理镜头与探测器目录" icon={<Database size={16} />} />
      </div>
      <div className="p-3 space-y-2">
        {(["lens", "detector"] as Kind[]).map((k) => {
          const cfg = KIND_CONFIG[k];
          const active = kind === k;
          return (
            <button
              key={k}
              onClick={() => onKindChange(k)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                active
                  ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300"
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
              }`}
            >
              <span className={active ? cfg.color : "text-slate-400 dark:text-slate-500"}>{cfg.icon}</span>
              {cfg.label}
            </button>
          );
        })}
      </div>

      <div className="px-3 pb-3 space-y-3">
        <Input
          placeholder="搜索型号、分类、接口"
          icon={<Search size={14} />}
          value={search}
          onChange={(e: InputChangeEvent) => onSearchChange(e.target.value)}
        />
        <div>
          <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5">数据来源</p>
          <div className="flex flex-wrap gap-1.5">
            {(["all", "seed", "user"] as const).map((s) => (
              <button
                key={s}
                onClick={() => onSourceFilterChange(s)}
                className={`text-[10px] px-2 py-1 rounded-md transition-colors ${
                  sourceFilter === s
                    ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 font-semibold"
                    : "bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
                }`}
              >
                {s === "all" ? "全部" : s === "seed" ? "内置" : "自定义"}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-center">
          <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800">
            <p className="text-lg font-bold text-slate-800 dark:text-slate-100">{lensCount}</p>
            <p className="text-[10px] text-slate-400 dark:text-slate-500">镜头</p>
          </div>
          <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800">
            <p className="text-lg font-bold text-slate-800 dark:text-slate-100">{detectorCount}</p>
            <p className="text-[10px] text-slate-400 dark:text-slate-500">探测器</p>
          </div>
        </div>
        <div className="space-y-2 pt-1">
          <Button variant="primary" size="sm" className="w-full" leftIcon={<Plus size={14} />} onClick={onNew}>
            新建{KIND_CONFIG[kind].label}
          </Button>
          <Button variant="outline" size="sm" className="w-full" leftIcon={<Upload size={14} />} onClick={onImport}>
            批量导入
          </Button>
        </div>
      </div>
    </Card>
  );
}
