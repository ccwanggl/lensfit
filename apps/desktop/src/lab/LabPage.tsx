import { useEffect, useRef, useState } from "react";
import { ArrowLeft, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { useLabStore } from "../stores/labStore";
import { ExperimentCatalog } from "./ExperimentCatalog";
import { ExperimentRunner } from "./ExperimentRunner";

export default function LabPage() {
  const activeExperimentId = useLabStore((s) => s.activeExperimentId);
  const showSidebar = useLabStore((s) => s.showSidebar);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);
  const toggleSidebar = useLabStore((s) => s.toggleSidebar);
  const runnerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // On mobile, auto-scroll the runner panel into view when an experiment is selected.
  useEffect(() => {
    if (activeExperimentId && runnerRef.current && !isFullscreen) {
      runnerRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [activeExperimentId, isFullscreen]);

  const handleBack = () => setActiveExperimentId(null);
  const handleToggleFullscreen = () => setIsFullscreen((prev) => !prev);

  if (isFullscreen && activeExperimentId) {
    return (
      <div className="fixed inset-0 z-50 flex flex-col bg-slate-50 dark:bg-slate-950">
        <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2 dark:border-slate-800 dark:bg-slate-900">
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            全屏实验
          </span>
          <button
            onClick={handleToggleFullscreen}
            className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            退出全屏
          </button>
        </div>
        <div className="flex-1 p-4">
          <ExperimentRunner
            experimentId={activeExperimentId}
            fullscreen
            onExitFullscreen={handleToggleFullscreen}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex h-[calc(100vh-140px)] gap-4">
      {/* Sidebar catalog */}
      <aside
        className={`shrink-0 overflow-hidden transition-all duration-300 ease-in-out ${
          showSidebar ? "w-80 opacity-100" : "w-0 opacity-0"
        }`}
      >
        <div className="h-full w-80">
          <ExperimentCatalog onSelect={setActiveExperimentId} />
        </div>
      </aside>

      {/* Main content */}
      <main className="flex min-w-0 flex-1 flex-col" ref={runnerRef}>
        {/* Toolbar */}
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {activeExperimentId && (
              <button
                onClick={handleBack}
                className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden dark:text-slate-400 dark:hover:bg-slate-800"
                title="返回目录" aria-label="返回目录"
              >
                <ArrowLeft size={18} />
              </button>
            )}
            <button
              onClick={toggleSidebar}
              className="hidden items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 lg:flex"
              title={showSidebar ? "收起目录" : "展开目录"}
            >
              {showSidebar ? <PanelLeftClose size={16} /> : <PanelLeftOpen size={16} />}
              {showSidebar ? "收起目录" : "展开目录"}
            </button>
          </div>

          {activeExperimentId && (
            <button
              onClick={handleToggleFullscreen}
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              全屏运行
            </button>
          )}
        </div>

        {/* Runner or empty state */}
        <div className="min-h-0 flex-1">
          {activeExperimentId ? (
            <ExperimentRunner experimentId={activeExperimentId} />
          ) : (
            <div className="flex h-full flex-col items-center justify-center rounded-[14px] border border-dashed border-slate-300 bg-white/50 p-8 text-center dark:border-slate-700 dark:bg-slate-800/50">
              <div className="mb-3 text-4xl">🔬</div>
              <h2 className="mb-2 text-lg font-semibold text-slate-800 dark:text-slate-200">
                选择一个实验开始
              </h2>
              <p className="max-w-md text-sm text-slate-500 dark:text-slate-400">
                光学实验室把知识库中的概念变成可操作的模拟。调整参数，观察结果，建立直觉。
              </p>
              {!showSidebar && (
                <button
                  onClick={toggleSidebar}
                  className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                >
                  打开实验目录
                </button>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Mobile: single panel with slide-like transition */}
      <div className="absolute inset-0 flex flex-col gap-3 bg-slate-50 dark:bg-slate-950 lg:hidden">
        {activeExperimentId ? (
          <>
            <button
              onClick={handleBack}
              className="flex w-fit items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
            >
              <ArrowLeft size={16} />
              返回实验列表
            </button>
            <div className="min-h-0 flex-1">
              <ExperimentRunner experimentId={activeExperimentId} />
            </div>
          </>
        ) : (
          <ExperimentCatalog onSelect={setActiveExperimentId} />
        )}
      </div>
    </div>
  );
}
