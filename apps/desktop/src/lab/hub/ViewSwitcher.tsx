/** Top-level view switcher: 学习路径 / 实验沙盘 / 教程 (slice B). */
import { BookOpen, FlaskConical, Milestone } from "lucide-react";
import { TabButton } from "./TabButton";

export type LearningView = "path" | "sandbox" | "tutorials";

export function ViewSwitcher({
  learningView,
  setLearningView,
}: {
  learningView: LearningView;
  setLearningView: (v: LearningView) => void;
}) {
  return (
    <>
      {/* View switcher: 学习路径 / 实验沙盘 / 教程 */}
      <div className="flex items-center gap-1 self-start rounded-lg border border-slate-200 bg-slate-50 p-0.5 dark:border-slate-700 dark:bg-slate-900">
        <TabButton
          active={learningView === "path"}
          onClick={() => setLearningView("path")}
          icon={<Milestone size={14} />}
          label="学习路径"
        />
        <TabButton
          active={learningView === "sandbox"}
          onClick={() => setLearningView("sandbox")}
          icon={<FlaskConical size={14} />}
          label="实验沙盘"
        />
        <TabButton
          active={learningView === "tutorials"}
          onClick={() => setLearningView("tutorials")}
          icon={<BookOpen size={14} />}
          label="教程"
        />
      </div>
    </>
  );
}
