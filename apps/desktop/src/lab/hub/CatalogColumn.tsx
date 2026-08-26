/** Catalog + parameter card columns (moved verbatim from LearningHub, slice B). */
import { X } from "lucide-react";
import { ExperimentCatalog } from "../ExperimentCatalog";
import { BreadboardPresetHeader } from "./BreadboardPresetHeader";
import { ParameterPanel } from "./panels";
import type { LabExperiment } from "../../utils/api";

interface DesktopProps {
  showSidebar: boolean;
  centerExpanded: boolean;
  handleSelectExperiment: (id: string) => void;
  experiment: LabExperiment | null;
  isPreset: boolean;
  activeExperimentId: string | null;
  params: Record<string, unknown>;
  handleParamChange: (name: string, value: unknown) => void;
  handleReset: () => void;
  isFetching: boolean;
  sceneError: string | null;
}

interface OverlayProps extends Omit<DesktopProps, "showSidebar" | "centerExpanded"> {
  setMobilePanel: (v: "left" | "right" | null) => void;
}

      export function DesktopCatalogColumn({
  showSidebar,
  centerExpanded,
  handleSelectExperiment,
  experiment,
  isPreset,
  activeExperimentId,
  params,
  handleParamChange,
  handleReset,
  isFetching,
  sceneError,
}: DesktopProps) {
  return (
    <>
      {!centerExpanded && (
        <aside
          className={`${
            showSidebar ? "hidden lg:flex" : "hidden"
          } h-full w-72 shrink-0 flex-col gap-3`}
        >
          <div className="min-h-0 flex-[1.2]">
            <ExperimentCatalog onSelect={handleSelectExperiment} />
          </div>
          {experiment && (
            <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[14px] border border-slate-200/60 bg-white/80 p-3 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
              {isPreset && activeExperimentId && (
                <BreadboardPresetHeader
                  presetId={activeExperimentId}
                  params={params}
                  onChange={handleParamChange}
                />
              )}
              <ParameterPanel
                experiment={experiment}
                params={params}
                onChange={handleParamChange}
                onReset={handleReset}
                isFetching={isFetching}
                isPreset={isPreset}
                sceneError={sceneError}
              />
            </div>
          )}
        </aside>
      )}
    </>
  );
}

export function MobileCatalogOverlay({
  setMobilePanel,
  handleSelectExperiment,
  experiment,
  isPreset,
  activeExperimentId,
  params,
  handleParamChange,
  handleReset,
  isFetching,
  sceneError,
}: OverlayProps) {
  return (
    <>
        <div className="absolute inset-y-0 left-0 z-30 w-[85%] max-w-xs bg-slate-50/95 p-3 shadow-2xl backdrop-blur dark:bg-slate-950/95 lg:hidden">
          <div className="flex h-full flex-col gap-3">
            <button
              onClick={() => setMobilePanel(null)}
              className="self-end rounded-lg p-2 text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800"
              aria-label="关闭面板"
            >
              <X size={18} />
            </button>
            <div className="min-h-0 flex-1">
              <ExperimentCatalog onSelect={handleSelectExperiment} />
            </div>
            {experiment && (
              <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[14px] border border-slate-200/60 bg-white/80 p-3 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
                {isPreset && activeExperimentId && (
                  <BreadboardPresetHeader
                    presetId={activeExperimentId}
                    params={params}
                    onChange={handleParamChange}
                  />
                )}
                <ParameterPanel
                  experiment={experiment}
                  params={params}
                  onChange={handleParamChange}
                  onReset={handleReset}
                  isFetching={isFetching}
                  isPreset={isPreset}
                  sceneError={sceneError}
                />
              </div>
            )}
          </div>
        </div>
    </>
  );
}
