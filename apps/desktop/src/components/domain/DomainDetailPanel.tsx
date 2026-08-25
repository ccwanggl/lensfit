import type { ReactNode } from "react";
import { BarChart3, Activity, BookOpen, GraduationCap } from "lucide-react";
import { Card, SectionHeader } from "../ui";

export type RightTab = "viz" | "trace" | "knowledge" | "learning";

interface TabConfig {
  key: RightTab;
  label: string;
  icon: ReactNode;
}

interface DomainDetailPanelProps {
  title: string;
  subtitle: string;
  icon: ReactNode;
  activeTab: RightTab;
  onTabChange: (tab: RightTab) => void;
  tabs?: TabConfig[];
  theme?: "indigo" | "orange";
  viz: ReactNode;
  trace: ReactNode;
  knowledge: ReactNode;
  learning: ReactNode;
}

const DEFAULT_TABS: TabConfig[] = [
  { key: "viz", label: "可视化", icon: <BarChart3 size={13} /> },
  { key: "trace", label: "推导链", icon: <Activity size={13} /> },
  { key: "knowledge", label: "知识库", icon: <BookOpen size={13} /> },
  { key: "learning", label: "学习指导", icon: <GraduationCap size={13} /> },
];

const ACTIVE_TAB_CLASSES: Record<string, string> = {
  indigo:
    "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-semibold",
  orange:
    "bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 font-semibold",
};

/** Right-hand detail panel with viz / trace / knowledge / learning tabs. */
export function DomainDetailPanel({
  title,
  subtitle,
  icon,
  activeTab,
  onTabChange,
  tabs = DEFAULT_TABS,
  theme = "indigo",
  viz,
  trace,
  knowledge,
  learning,
}: DomainDetailPanelProps) {
  const tabContent: Record<RightTab, ReactNode> = {
    viz,
    trace,
    knowledge,
    learning,
  };

  return (
    <Card padding="none" className="overflow-hidden h-full flex flex-col">
      <div className="p-4 border-b border-slate-100 dark:border-slate-700">
        <SectionHeader title={title} subtitle={subtitle} icon={icon} />
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col">
        <div className="flex items-center gap-1 mb-3 pb-2 border-b border-slate-100 dark:border-slate-700">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => onTabChange(t.key)}
              className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === t.key
                  ? ACTIVE_TAB_CLASSES[theme]
                  : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50"
              }`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>
        <div className="flex-1 overflow-y-auto pr-1">
          {tabContent[activeTab]}
        </div>
      </div>
    </Card>
  );
}
