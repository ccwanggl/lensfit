/** Project & setup endpoints (`/api/v1/projects/*`). */

import { apiFetch, getEndpoint, getApiKey, apiErrorFromResponse } from "./client";
import type { ApiListResponse } from "./types";

export interface ProjectItem {
  id: number;
  name: string;
  description?: string;
  domain: string;
  created_at: string;
}

export interface SetupItem {
  id: number;
  project_id: number;
  name: string;
  lens_id?: number;
  detector_id?: number;
  created_at: string;
  lens_snapshot?: Record<string, unknown> | null;
  detector_snapshot?: Record<string, unknown> | null;
  match_result_snapshot?: Record<string, unknown> | null;
  notes?: string | null;
}

export async function listProjects() {
  return apiFetch<ApiListResponse<ProjectItem>>("/api/v1/projects");
}

export async function createProject(data: { name: string; description?: string; domain?: string }) {
  return apiFetch<ProjectItem>("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteProject(projectId: number) {
  return apiFetch<{ deleted: boolean }>(`/api/v1/projects/${projectId}`, {
    method: "DELETE",
  });
}

/* ─── Setups ─── */
export async function listSetups(projectId: number) {
  return apiFetch<ApiListResponse<SetupItem>>(`/api/v1/projects/${projectId}/setups`);
}

export async function saveSetup(
  projectId: number,
  data: { name: string; lens_id?: number; detector_id?: number; notes?: string; match_result_snapshot?: object }
) {
  return apiFetch<SetupItem>(`/api/v1/projects/${projectId}/setups`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteSetup(projectId: number, setupId: number) {
  return apiFetch<{ deleted: boolean }>(`/api/v1/projects/${projectId}/setups/${setupId}`, {
    method: "DELETE",
  });
}

export async function generateProjectReport(
  projectId: number,
  format: "pdf" | "excel" = "pdf"
): Promise<Blob> {
  const base = await getEndpoint();
  const apiKey = await getApiKey();
  const res = await fetch(`${base}/api/v1/projects/${projectId}/report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
    },
    body: JSON.stringify({ format }),
  });
  if (!res.ok) {
    throw await apiErrorFromResponse(res);
  }
  return res.blob();
}
