import { X, GraduationCap, Eye, Monitor, Info } from "lucide-react";
import { useLearningMode } from "../contexts/LearningModeContext";

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

export default function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const { learningMode, setLearningMode } = useLearningMode();

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex justify-end">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/30 dark:bg-slate-950/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="relative w-full max-w-sm h-full bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col animate-in slide-in-from-right duration-200">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <Monitor size={18} className="text-indigo-500" />
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">设置</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Learning Mode section */}
          <section className="space-y-3">
            <div className="flex items-center gap-2">
              <GraduationCap size={16} className="text-emerald-500" />
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">学习模式</h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              开启后，所有参数旁会显示光学知识提示，知识面板会高亮并自动展开相关学习章节，帮助非专业人员理解每个参数和公式的物理含义。
            </p>

            <button
              onClick={() => setLearningMode(!learningMode)}
              className={`w-full flex items-center justify-between p-3.5 rounded-xl border transition-colors ${
                learningMode
                  ? "bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800/40"
                  : "bg-slate-50 border-slate-200 dark:bg-slate-800 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${
                  learningMode
                    ? "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-400"
                    : "bg-slate-200 text-slate-500 dark:bg-slate-700 dark:text-slate-400"
                }`}>
                  {learningMode ? <Eye size={18} /> : <Info size={18} />}
                </div>
                <div className="text-left">
                  <p className={`text-sm font-semibold ${learningMode ? "text-emerald-700 dark:text-emerald-400" : "text-slate-700 dark:text-slate-200"}`}>
                    {learningMode ? "学习模式已开启" : "学习模式已关闭"}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">参数提示 · 公式讲解 · 概念图解</p>
                </div>
              </div>
              <div className={`w-11 h-6 rounded-full relative transition-colors ${learningMode ? "bg-emerald-500" : "bg-slate-300 dark:bg-slate-600"}`}>
                <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform ${learningMode ? "translate-x-5" : ""}`} />
              </div>
            </button>

            {learningMode && (
              <div className="p-3 rounded-lg bg-emerald-50/50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-800/20">
                <p className="text-xs text-emerald-700 dark:text-emerald-400 leading-relaxed">
                  已启用：表单参数会显示 ? 提示，展开公式可查看交互式计算器和章节链接。
                </p>
              </div>
            )}
          </section>

          <hr className="border-slate-100 dark:border-slate-800" />

          {/* Learning tips for non-experts */}
          <section className="space-y-3">
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">新手学习建议</h3>
            <ul className="space-y-2">
              {[
                "从最左侧的表单参数提示开始，逐一看懂每个输入的含义。",
                "点击知识面板中的公式，查看 LaTeX 表达式和互动计算器。",
                "切换到“概念图解”页，用鼠标拖动/滑动理解薄透镜、传感器覆盖和奈奎斯特采样。",
                "使用“游乐场”页任意调整参数，观察公式结果如何变化。",
              ].map((tip, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  <span className="w-5 h-5 shrink-0 rounded-full bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-[10px] font-bold">
                    {idx + 1}
                  </span>
                  {tip}
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
