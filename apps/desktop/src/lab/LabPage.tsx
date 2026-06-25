import { useEffect, useRef } from "react";
import { ArrowLeft } from "lucide-react";
import { useLabStore } from "../stores/labStore";
import { ExperimentCatalog } from "./ExperimentCatalog";
import { ExperimentRunner } from "./ExperimentRunner";

export default function LabPage() {
  const activeExperimentId = useLabStore((s) => s.activeExperimentId);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);
  const runnerRef = useRef<HTMLDivElement>(null);

  // On mobile, auto-scroll the runner panel into view when an experiment is selected.
  useEffect(() => {
    if (activeExperimentId && runnerRef.current) {
      runnerRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [activeExperimentId]);

  const handleBack = () => setActiveExperimentId(null);

  return (
    <div className="relative min-h-[calc(100vh-140px)]">
      {/* Desktop: side-by-side grid */}
      <div className="hidden h-[calc(100vh-140px)] gap-5 lg:grid lg:grid-cols-12">
        <div className="lg:col-span-4 xl:col-span-3">
          <ExperimentCatalog onSelect={setActiveExperimentId} />
        </div>
        <div className="lg:col-span-8 xl:col-span-9" ref={runnerRef}>
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
            </div>
          )}
        </div>
      </div>

      {/* Mobile: single panel with slide-like transition */}
      <div className="flex h-[calc(100vh-140px)] flex-col gap-5 lg:hidden">
        {activeExperimentId ? (
          <div className="flex h-full flex-col gap-3" ref={runnerRef}>
            <button
              onClick={handleBack}
              className="flex w-fit items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              <ArrowLeft size={16} />
              返回实验列表
            </button>
            <div className="min-h-0 flex-1">
              <ExperimentRunner experimentId={activeExperimentId} />
            </div>
          </div>
        ) : (
          <ExperimentCatalog onSelect={setActiveExperimentId} />
        )}
      </div>
    </div>
  );
}
