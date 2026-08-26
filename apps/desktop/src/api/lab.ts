/** Optics Lab endpoints (`/api/v1/lab/*`). */

import { apiFetch } from "./client";
import type { WorkbenchScene } from "../lab/workbenchTypes";

export interface LabParameter {
  name: string;
  label: string;
  type: string;
  default: unknown;
  min?: number | null;
  max?: number | null;
  step?: number | null;
  unit?: string | null;
  options?: Array<{ value: unknown; label: string }>;
  description?: string;
}

export interface LabExperiment {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  linked_concepts: string[];
  linked_formulas: string[];
  prerequisites: string[];
  learning_objectives: string[];
  parameters: LabParameter[];
}

export interface LabRunResult {
  data: Record<string, unknown>;
  svg: string;
  warnings: string[];
  learning_hints: string[];
}

export async function listLabExperiments() {
  return apiFetch<{ items: LabExperiment[] }>("/api/v1/lab/experiments");
}

export async function getLabExperiment(id: string) {
  return apiFetch<{ items: LabExperiment[] }>(`/api/v1/lab/experiments/${id}`);
}

export async function runLabExperiment(id: string, params: Record<string, unknown>) {
  return apiFetch<LabRunResult>(`/api/v1/lab/experiments/${id}/run`, {
    method: "POST",
    body: JSON.stringify({ params }),
  });
}

export async function runWorkbench(
  scene: WorkbenchScene,
  includeRayImage: boolean = false
) {
  return apiFetch<LabRunResult>("/api/v1/lab/workbench/run", {
    method: "POST",
    body: JSON.stringify({ scene, include_ray_image: includeRayImage }),
  });
}
