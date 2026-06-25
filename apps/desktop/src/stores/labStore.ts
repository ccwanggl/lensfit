import { create } from "zustand";
import { persist } from "zustand/middleware";

interface LabState {
  activeExperimentId: string | null;
  paramDrafts: Record<string, Record<string, unknown>>;
  showDataPanel: boolean;
  showSidebar: boolean;
  recentExperiments: string[];

  setActiveExperimentId: (id: string | null) => void;
  setParam: (experimentId: string, name: string, value: unknown) => void;
  setParams: (experimentId: string, params: Record<string, unknown>) => void;
  toggleDataPanel: () => void;
  toggleSidebar: () => void;
  addRecentExperiment: (id: string) => void;
}

export const useLabStore = create<LabState>()(
  persist(
    (set) => ({
      activeExperimentId: null,
      paramDrafts: {},
      showDataPanel: true,
      showSidebar: true,
      recentExperiments: [],

      setActiveExperimentId: (id) =>
        set((state) => ({
          activeExperimentId: id,
          recentExperiments: id
            ? [id, ...state.recentExperiments.filter((x) => x !== id)].slice(0, 8)
            : state.recentExperiments,
        })),

      setParam: (experimentId, name, value) =>
        set((state) => ({
          paramDrafts: {
            ...state.paramDrafts,
            [experimentId]: {
              ...state.paramDrafts[experimentId],
              [name]: value,
            },
          },
        })),

      setParams: (experimentId, params) =>
        set((state) => ({
          paramDrafts: {
            ...state.paramDrafts,
            [experimentId]: {
              ...state.paramDrafts[experimentId],
              ...params,
            },
          },
        })),

      toggleDataPanel: () =>
        set((state) => ({ showDataPanel: !state.showDataPanel })),

      toggleSidebar: () =>
        set((state) => ({ showSidebar: !state.showSidebar })),

      addRecentExperiment: (id) =>
        set((state) => ({
          recentExperiments: [id, ...state.recentExperiments.filter((x) => x !== id)].slice(0, 8),
        })),
    }),
    {
      name: "lensfit-lab-store",
      partialize: (state) => ({
        paramDrafts: state.paramDrafts,
        recentExperiments: state.recentExperiments,
        showDataPanel: state.showDataPanel,
        showSidebar: state.showSidebar,
      }),
    }
  )
);
