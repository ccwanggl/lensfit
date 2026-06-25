import { create } from "zustand";
import { persist } from "zustand/middleware";

interface LabState {
  activeExperimentId: string | null;
  paramDrafts: Record<string, Record<string, unknown>>;
  sceneDrafts: Record<string, Record<string, unknown>>;
  showDataPanel: boolean;
  showSidebar: boolean;
  recentExperiments: string[];

  setActiveExperimentId: (id: string | null) => void;
  setParam: (experimentId: string, name: string, value: unknown) => void;
  setParams: (experimentId: string, params: Record<string, unknown>) => void;
  setSceneDraft: (presetId: string, params: Record<string, unknown>) => void;
  resetSceneDraft: (presetId: string) => void;
  toggleDataPanel: () => void;
  toggleSidebar: () => void;
  addRecentExperiment: (id: string) => void;
}

export const useLabStore = create<LabState>()(
  persist(
    (set) => ({
      activeExperimentId: null,
      paramDrafts: {},
      sceneDrafts: {},
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

      setSceneDraft: (presetId, params) =>
        set((state) => ({
          sceneDrafts: {
            ...state.sceneDrafts,
            [presetId]: {
              ...state.sceneDrafts[presetId],
              ...params,
            },
          },
        })),

      resetSceneDraft: (presetId) =>
        set((state) => {
          const next = { ...state.sceneDrafts };
          delete next[presetId];
          return { sceneDrafts: next };
        }),

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
        sceneDrafts: state.sceneDrafts,
        recentExperiments: state.recentExperiments,
        showDataPanel: state.showDataPanel,
        showSidebar: state.showSidebar,
      }),
    }
  )
);
