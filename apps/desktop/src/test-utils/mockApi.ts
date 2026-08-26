/**
 * Complete manual mock factory for `utils/api` (slice C-0 characterization net).
 *
 * Slice A keeps every export re-exported from the aggregate module, so a single
 * factory covering the full surface safely backs any component tree that pulls
 * API functions transitively (pages, hooks, panels).
 */
import { vi } from "vitest";

export function buildApiMock() {
  return {
    // client
    ApiError: class ApiError extends Error {
      status: number;
      detail: string;
      constructor(status: number, detail: string) {
        super(detail);
        this.name = "ApiError";
        this.status = status;
        this.detail = detail;
      }
    },

    // domains
    listDomains: vi.fn().mockResolvedValue({ items: [] }),
    getDomainParameters: vi.fn().mockResolvedValue({ parameters: [] }),

    // matching
    calculate: vi.fn().mockResolvedValue({}),
    startMatch: vi.fn().mockResolvedValue({ task_id: "t", status: "pending", created_at: "" }),
    getMatchStatus: vi.fn().mockResolvedValue({ task_id: "t", status: "completed", progress: 100, stage: "done" }),
    getMatchResult: vi.fn().mockResolvedValue({ status: "completed", top_matches: [], diagnostics: [] }),
    cancelMatch: vi.fn().mockResolvedValue({ cancelled: true }),
    startMatchStream: vi.fn().mockReturnValue({ close: () => {} }),

    // visualization
    generateCoverage: vi.fn().mockRejectedValue(new Error("no coverage in smoke test")),
    generateMtf: vi.fn().mockRejectedValue(new Error("no mtf in smoke test")),
    generateCoc: vi.fn().mockRejectedValue(new Error("no coc in smoke test")),

    // catalog
    listLenses: vi.fn().mockResolvedValue({ items: [] }),
    listDetectors: vi.fn().mockResolvedValue({ items: [] }),
    listManufacturers: vi.fn().mockResolvedValue({ items: [] }),
    createManufacturer: vi.fn(),
    createLens: vi.fn(),
    updateLens: vi.fn(),
    deleteLens: vi.fn(),
    createDetector: vi.fn(),
    updateDetector: vi.fn(),
    deleteDetector: vi.fn(),
    importCatalog: vi.fn(),

    // projects
    listProjects: vi.fn().mockResolvedValue({ items: [] }),
    createProject: vi.fn(),
    deleteProject: vi.fn(),
    listSetups: vi.fn().mockResolvedValue({ items: [] }),
    saveSetup: vi.fn(),
    deleteSetup: vi.fn(),
    generateProjectReport: vi.fn(),

    // export
    exportReport: vi.fn(),

    // knowledge
    listKnowledgeFormulas: vi.fn().mockResolvedValue({ items: [] }),
    listKnowledgeConstraints: vi.fn().mockResolvedValue({ items: [] }),
    knowledgeInfer: vi.fn().mockResolvedValue({ derived_params: {}, trace_chain: [] }),
    listPresets: vi.fn().mockResolvedValue({ items: [] }),
    getPreset: vi.fn(),

    // lab
    listLabExperiments: vi.fn().mockResolvedValue({ items: [] }),
    getLabExperiment: vi.fn().mockResolvedValue({ items: [] }),
    runLabExperiment: vi.fn(),
    runWorkbench: vi.fn(),

    // content / curriculum / learning
    listContentConcepts: vi.fn().mockResolvedValue({ items: [], errors: [] }),
    getContentConcept: vi.fn(),
    listContentQuizzes: vi.fn().mockResolvedValue({ items: [], errors: [] }),
    getContentQuiz: vi.fn(),
    getCurriculumGraph: vi.fn().mockResolvedValue({ nodes: [], edges: [] }),
    getLearningProgress: vi.fn().mockResolvedValue({ items: [] }),
    putLearningProgress: vi.fn().mockResolvedValue({}),
  };
}

export type ApiMock = ReturnType<typeof buildApiMock>;
