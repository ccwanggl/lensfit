import { useLabStore } from "../stores/labStore";
import { ExperimentCatalog } from "./ExperimentCatalog";
import { ExperimentRunner } from "./ExperimentRunner";

export default function LabPage() {
  const activeExperimentId = useLabStore((s) => s.activeExperimentId);
  const setActiveExperimentId = useLabStore((s) => s.setActiveExperimentId);

  return (
    <div className="grid h-[calc(100vh-140px)] grid-cols-1 gap-5 lg:grid-cols-12">
      <div className="lg:col-span-4 xl:col-span-3">
        <ExperimentCatalog onSelect={setActiveExperimentId} />
      </div>
      <div className="lg:col-span-8 xl:col-span-9">
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
  );
}
