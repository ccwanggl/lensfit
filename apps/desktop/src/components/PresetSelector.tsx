import { useState, useEffect } from "react";
import { BookOpen, Check, ChevronDown, Award, Cpu, Lightbulb, Shield } from "lucide-react";
import { listPresets, type PresetConfigItem } from "../utils/api";
import { toast } from "../hooks/useToast";

interface PresetSelectorProps {
  domain: string;
  onSelect: (preset: PresetConfigItem) => void;
}

const difficultyBadge: Record<string, { label: string; className: string }> = {
  beginner: { label: "入门", className: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/40" },
  intermediate: { label: "中级", className: "bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800/40" },
  professional: { label: "专业", className: "bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200 dark:border-rose-800/40" },
};

export default function PresetSelector({ domain, onSelect }: PresetSelectorProps) {
  const [presets, setPresets] = useState<PresetConfigItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<PresetConfigItem | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    listPresets(domain)
      .then((data) => setPresets(data.items))
      .catch(() => toast("error", "加载预设失败", "无法从服务器获取预设方案"))
      .finally(() => setLoading(false));
  }, [domain]);

  const handleSelect = (preset: PresetConfigItem) => {
    setSelected(preset);
    setIsOpen(false);
    onSelect(preset);
    toast("success", "预设已应用", `已加载「${preset.name_cn}」配置方案`);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-xl border
          text-sm font-medium transition-all focus-ring
          ${selected
            ? "bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-900/30 dark:border-indigo-800/40 dark:text-indigo-400"
            : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600"
          }
        `}
      >
        <div className="flex items-center gap-2 min-w-0">
          <BookOpen size={14} className={selected ? "text-indigo-500" : "text-slate-400"} />
          <span className="truncate">
            {selected ? selected.name_cn : loading ? "加载中..." : "选择专业预设方案"}
          </span>
        </div>
        <ChevronDown size={14} className={`flex-shrink-0 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute z-50 mt-1.5 w-full bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden">
            <div className="max-h-[320px] overflow-y-auto">
              {presets.length === 0 ? (
                <div className="px-3 py-4 text-xs text-slate-400 dark:text-slate-500 text-center">
                  暂无该领域的预设方案
                </div>
              ) : (
                presets.map((preset) => {
                  const diff = difficultyBadge[preset.difficulty] || difficultyBadge.intermediate;
                  const isActive = selected?.id === preset.id;
                  return (
                    <button
                      key={preset.id}
                      onClick={() => handleSelect(preset)}
                      className={`
                        w-full text-left px-3 py-2.5 transition-colors flex items-start gap-2.5
                        ${isActive
                          ? "bg-indigo-50 dark:bg-indigo-900/20"
                          : "hover:bg-slate-50 dark:hover:bg-slate-700/50"
                        }
                      `}
                    >
                      <div className="mt-0.5">
                        {isActive ? (
                          <Check size={14} className="text-indigo-500" />
                        ) : (
                          <BookOpen size={14} className="text-slate-400 dark:text-slate-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                            {preset.name_cn}
                          </span>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded-md border font-medium ${diff.className}`}>
                            {diff.label}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                          {preset.description}
                        </p>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}

      {/* Selected preset detail panel */}
      {selected && (
        <div className="mt-3 space-y-3">
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{selected.description}</p>
          </div>

          {selected.lens_recommendations.length > 0 && (
            <div className="p-3 rounded-xl bg-indigo-50/50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/40">
              <div className="flex items-center gap-1.5 mb-2">
                <Award size={12} className="text-indigo-500" />
                <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-400">推荐镜头</span>
              </div>
              <div className="space-y-1.5">
                {selected.lens_recommendations.map((rec, i) => (
                  <div key={i} className="text-xs text-slate-600 dark:text-slate-300">
                    <span className="font-medium">{String(rec.model || rec.type || "推荐方案")}</span>
                    {!!rec.notes && <span className="text-slate-400 dark:text-slate-500 ml-1">— {String(rec.notes)}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {selected.detector_recommendations.length > 0 && (
            <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800/40">
              <div className="flex items-center gap-1.5 mb-2">
                <Cpu size={12} className="text-emerald-500" />
                <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">推荐传感器</span>
              </div>
              <div className="space-y-1.5">
                {selected.detector_recommendations.map((rec, i) => (
                  <div key={i} className="text-xs text-slate-600 dark:text-slate-300">
                    <span className="font-medium">{String(rec.model || "推荐方案")}</span>
                    {!!rec.notes && <span className="text-slate-400 dark:text-slate-500 ml-1">— {String(rec.notes)}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {selected.notes && (
            <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800/40">
              <div className="flex items-center gap-1.5 mb-1.5">
                <Lightbulb size={12} className="text-amber-500" />
                <span className="text-xs font-semibold text-amber-700 dark:text-amber-400">专业提示</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{selected.notes}</p>
            </div>
          )}

          {selected.standards.length > 0 && (
            <div className="flex items-center gap-1.5">
              <Shield size={11} className="text-slate-400" />
              <span className="text-[10px] text-slate-400 dark:text-slate-500">
                相关标准：{selected.standards.join("、")}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
