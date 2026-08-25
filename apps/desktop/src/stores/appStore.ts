import { create } from "zustand";

export type AppTabId =
  | "industrial"
  | "microscope"
  | "infrared"
  | "photography"
  | "projects"
  | "library"
  | "playground"
  | "learning";

interface AppState {
  activeTab: AppTabId;
  setActiveTab: (tab: AppTabId) => void;
}

/** App-shell state (top-level tab). Introduced in learning-first phase 1 so
 * the learning hub can route practice nodes to their domain workbench tabs.
 * Phase 4 (app-shell inversion): the learning hub is the default home tab. */
export const useAppStore = create<AppState>()((set) => ({
  activeTab: "learning",
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
