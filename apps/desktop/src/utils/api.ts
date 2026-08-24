/** API client for OptiBench engine.
 *
 * In Tauri desktop mode, the endpoint is discovered dynamically from the
 * Rust sidecar supervisor. In web/dev mode it falls back to localhost.
 */

let _cachedEndpoint: string | null = null;
let _cachedApiKey: string | null = null;

async function getEndpoint(): Promise<string> {
  if (_cachedEndpoint) return _cachedEndpoint;

  const isTauri =
    typeof window !== "undefined" &&
    ("__TAURI_INTERNALS__" in window || "__TAURI__" in window);

  if (isTauri) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      const endpoint = await invoke<string>("get_engine_endpoint");
      _cachedEndpoint = endpoint;
      return endpoint;
    } catch {
      // fall through
    }
  }

  _cachedEndpoint = "http://127.0.0.1:8765";
  return _cachedEndpoint;
}

async function getApiKey(): Promise<string | null> {
  if (_cachedApiKey) return _cachedApiKey;

  const isTauri =
    typeof window !== "undefined" &&
    ("__TAURI_INTERNALS__" in window || "__TAURI__" in window);

  if (isTauri) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      const key = await invoke<string | null>("get_engine_api_key");
      _cachedApiKey = key ?? null;
      return _cachedApiKey;
    } catch {
      // fall through
    }
  }

  // Web/dev fallback: the key can be injected via VITE_ENGINE_API_KEY.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const envKey = ((import.meta as any).env?.VITE_ENGINE_API_KEY) as string | undefined;
  if (envKey) {
    _cachedApiKey = envKey;
    return _cachedApiKey;
  }

  return null;
}

/* ─── Types ─── */
export interface ApiListResponse<T> {
  items: T[];
  total?: number;
}

export interface CatalogLens {
  id: number;
  model: string;
  manufacturer_id: number;
  category: string;
  focal_length_mm: number;
  focal_length_max?: number;
  focal_length_min?: number;
  max_aperture: number;
  image_circle_mm: number;
  mount_type: string;
  price_usd: number;
  wavelength_min_nm?: number;
  wavelength_max_nm?: number;
  image_url?: string;
  na?: number;
  nominal_wd_mm?: number;
  [key: string]: unknown;
}

export interface CatalogDetector {
  id: number;
  model: string;
  manufacturer_id: number;
  category: string;
  sensor_format_inch?: string;
  sensor_w_mm?: number;
  sensor_h_mm?: number;
  sensor_diag_mm?: number;
  resolution_w?: number;
  resolution_h?: number;
  pixel_size_um?: number;
  mount_type?: string;
  price_usd: number;
  netd_mk?: number;
  spectral_range_min_um?: number;
  spectral_range_max_um?: number;
  [key: string]: unknown;
}

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

/* ─── Errors ─── */
export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function apiErrorFromResponse(res: Response): Promise<ApiError> {
  let detail = res.statusText;
  try {
    const data = (await res.json()) as Record<string, unknown>;
    if (typeof data.detail === "string") {
      detail = data.detail;
    } else if (data.detail != null) {
      detail = JSON.stringify(data.detail);
    }
  } catch {
    // leave detail as statusText
  }
  return new ApiError(res.status, detail);
}

/* ─── API Core ─── */
async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const base = await getEndpoint();
  const apiKey = await getApiKey();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(apiKey ? { "X-API-Key": apiKey } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };
  const res = await fetch(`${base}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    throw await apiErrorFromResponse(res);
  }
  return res.json() as Promise<T>;
}

export async function listDomains() {
  return apiFetch<{ items: { id: string; name: string }[] }>("/api/v1/domains");
}

export interface DomainParameterDef {
  name: string;
  label: string;
  type: string;
  unit: string;
  default: unknown;
  required: boolean;
  options: { value: string; label: string }[];
  min_value: number | null;
  max_value: number | null;
  description: string;
}

export async function getDomainParameters(domain: string) {
  return apiFetch<{
    domain_id: string;
    domain_name: string;
    parameters: DomainParameterDef[];
  }>(`/api/v1/domains/${domain}/parameters`);
}

export async function calculate(params: Record<string, number>) {
  return apiFetch<Record<string, number>>("/api/v1/calculate", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function startMatch(req: Record<string, unknown>) {
  return apiFetch<{ task_id: string; status: string; created_at: string }>("/api/v1/match/async", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function getMatchStatus(taskId: string) {
  return apiFetch<{ task_id: string; status: string; progress: number; stage: string; error?: string }>(
    `/api/v1/match/async/${taskId}`
  );
}

export async function getMatchResult(taskId: string) {
  return apiFetch<{
    status: string;
    top_matches?: unknown[];
    results?: unknown[];
    diagnostics?: unknown[];
    error?: string;
  }>(
    `/api/v1/match/async/${taskId}/result`
  );
}

export async function cancelMatch(taskId: string) {
  return apiFetch<unknown>(`/api/v1/match/async/${taskId}`, { method: "DELETE" });
}

export async function startMatchStream(
  req: Record<string, unknown>,
  onMessage: (data: Record<string, unknown>) => void,
  onError?: (error: unknown) => void
): Promise<{ close: () => void }> {
  const base = await getEndpoint();
  const apiKey = await getApiKey();
  const abortController = new AbortController();

  const res = await fetch(`${base}/api/v1/match/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
    },
    body: JSON.stringify(req),
    signal: abortController.signal,
  });

  if (!res.ok) {
    throw await apiErrorFromResponse(res);
  }
  if (!res.body) {
    throw new Error(`Stream error: ${res.status} ${res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const pump = async () => {
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            try {
              const data = JSON.parse(trimmed.slice(6)) as Record<string, unknown>;
              onMessage(data);
              if (data.stage === "completed" || data.stage === "error") {
                abortController.abort();
                return;
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
    } catch (e) {
      onError?.(e);
    }
  };

  pump();

  return {
    close: () => abortController.abort(),
  };
}

export interface CoverageData {
  sensor_rect: { x: number; y: number; w: number; h: number };
  image_circle: { cx: number; cy: number; r: number };
  vignetting_regions: Array<{ points: Array<{ x: number; y: number }> }>;
  coverage_ratio: number;
  safe_zone: { x: number; y: number; w: number; h: number };
}

export async function generateCoverage(lensId: number, detectorId: number) {
  return apiFetch<CoverageData>("/api/v1/visualize/coverage", {
    method: "POST",
    body: JSON.stringify({ lens_id: lensId, detector_id: detectorId }),
  });
}

export interface MtfPoint {
  frequency_lpmm: number;
  mtf: number;
  is_nyquist: boolean;
}

export interface MtfData {
  lens_mtf50_lpmm: number;
  detector_nyquist_lpmm: number | null;
  points: MtfPoint[];
}

export async function generateMtf(lensId: number, detectorId: number) {
  return apiFetch<MtfData>("/api/v1/visualize/mtf", {
    method: "POST",
    body: JSON.stringify({ lens_id: lensId, detector_id: detectorId }),
  });
}

export interface CocApertureData {
  aperture: number;
  hyperfocal_m: number;
  near_limit_m: number;
  far_limit_m: number | null;
  dof_total_m: number | null;
}

export interface CocData {
  coc_mm: number;
  sensor_diag_mm: number;
  focus_distance_m: number;
  focal_length_mm: number;
  max_aperture: number;
  apertures: CocApertureData[];
}

export async function generateCoc(
  lensId: number,
  detectorId: number,
  focusDistanceM: number = 2.0
) {
  return apiFetch<CocData>("/api/v1/visualize/coc", {
    method: "POST",
    body: JSON.stringify({
      lens_id: lensId,
      detector_id: detectorId,
      focus_distance_m: focusDistanceM,
    }),
  });
}

export interface CatalogListParams {
  category?: string;
  mount?: string;
  data_source?: "seed" | "user" | "all";
  q?: string;
  offset?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export async function listLenses(params?: CatalogListParams) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.mount) qs.set("mount_type", params.mount);
  if (params?.data_source && params.data_source !== "all") qs.set("data_source", params.data_source);
  if (params?.q) qs.set("q", params.q);
  if (params?.offset != null) qs.set("skip", String(params.offset));
  if (params?.limit != null) qs.set("limit", String(params.limit));
  if (params?.sort_by) qs.set("sort_by", params.sort_by);
  if (params?.sort_order) qs.set("sort_order", params.sort_order);
  return apiFetch<ApiListResponse<CatalogLens>>(`/api/v1/catalog/lenses?${qs.toString()}`);
}

export async function listDetectors(params?: CatalogListParams) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.mount) qs.set("mount_type", params.mount);
  if (params?.data_source && params.data_source !== "all") qs.set("data_source", params.data_source);
  if (params?.q) qs.set("q", params.q);
  if (params?.offset != null) qs.set("skip", String(params.offset));
  if (params?.limit != null) qs.set("limit", String(params.limit));
  if (params?.sort_by) qs.set("sort_by", params.sort_by);
  if (params?.sort_order) qs.set("sort_order", params.sort_order);
  return apiFetch<ApiListResponse<CatalogDetector>>(`/api/v1/catalog/detectors?${qs.toString()}`);
}

export interface Manufacturer {
  id: number;
  name: string;
  name_en?: string | null;
  name_cn?: string | null;
  country?: string | null;
  website?: string | null;
  is_verified?: boolean | null;
  data_source?: string | null;
}

export async function listManufacturers() {
  return apiFetch<{ items: Manufacturer[] }>("/api/v1/catalog/manufacturers");
}

export async function createManufacturer(data: { name: string; name_en?: string; name_cn?: string }) {
  return apiFetch<Manufacturer>("/api/v1/catalog/manufacturers", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export type LensCreatePayload = Omit<Partial<CatalogLens>, "id" | "data_source" | "verified">;

export async function createLens(payload: LensCreatePayload) {
  return apiFetch<CatalogLens>("/api/v1/catalog/lenses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateLens(id: number, payload: LensCreatePayload) {
  return apiFetch<CatalogLens>(`/api/v1/catalog/lenses/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteLens(id: number) {
  return apiFetch<unknown>(`/api/v1/catalog/lenses/${id}`, { method: "DELETE" });
}

export type DetectorCreatePayload = Omit<Partial<CatalogDetector>, "id" | "data_source" | "verified">;

export async function createDetector(payload: DetectorCreatePayload) {
  return apiFetch<CatalogDetector>("/api/v1/catalog/detectors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateDetector(id: number, payload: DetectorCreatePayload) {
  return apiFetch<CatalogDetector>(`/api/v1/catalog/detectors/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteDetector(id: number) {
  return apiFetch<unknown>(`/api/v1/catalog/detectors/${id}`, { method: "DELETE" });
}

export interface ImportResult {
  kind: "lenses" | "detectors";
  inserted: number;
  skipped: number;
  errors: string[];
}

export async function importCatalog(file: File): Promise<ImportResult> {
  const base = await getEndpoint();
  const apiKey = await getApiKey();
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${base}/api/v1/catalog/import`, {
    method: "POST",
    headers: {
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
    },
    body: formData,
  });
  if (!res.ok) {
    throw await apiErrorFromResponse(res);
  }
  return res.json() as Promise<ImportResult>;
}

export async function exportReport(
  format: "pdf" | "excel" | "csv",
  requirements: object,
  results: object[],
  topK: number = 10,
  diagnostics?: object[],
  whatIfResults?: object[]
): Promise<Blob> {
  const base = await getEndpoint();
  const apiKey = await getApiKey();
  const res = await fetch(`${base}/api/v1/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
    },
    body: JSON.stringify({
      format, requirements, results, top_k: topK,
      diagnostics, what_if_results: whatIfResults,
    }),
  });
  if (!res.ok) {
    throw await apiErrorFromResponse(res);
  }
  return res.blob();
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

/* ─── Projects ─── */
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

/* ─── Knowledge Base ─── */
export interface KnowledgeFormula {
  id: string;
  name_cn: string;
  expression: string;
  latex?: string;
  params: Array<{ name: string; name_cn: string; unit: string; description: string }>;
  outputs: string[];
  principle: string;
  assumption: string;
  domain: string;
}

export interface KnowledgeConstraint {
  id: string;
  name_cn: string;
  principle: string;
  failure_explanation_tpl: string;
  suggestion: string;
  severity: string;
}

export async function listKnowledgeFormulas(domain?: string) {
  const qs = domain ? `?domain=${encodeURIComponent(domain)}` : "";
  return apiFetch<{ items: KnowledgeFormula[] }>(`/api/v1/knowledge/formulas${qs}`);
}

export async function listKnowledgeConstraints() {
  return apiFetch<{ items: KnowledgeConstraint[] }>("/api/v1/knowledge/constraints");
}

export async function knowledgeInfer(params: Record<string, unknown>, domain: string = "all") {
  return apiFetch<{ derived_params: Record<string, unknown>; trace_chain: Array<Record<string, unknown>> }>(
    "/api/v1/knowledge/infer",
    {
      method: "POST",
      body: JSON.stringify({ params, domain }),
    }
  );
}

import type { WorkbenchScene } from "../lab/workbenchTypes";

/* ─── Optics Lab ─── */
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

/* ─── Preset Configs ─── */
export interface PresetConfigItem {
  id: string;
  name_cn: string;
  name_en: string;
  domain: string;
  description: string;
  difficulty: string;
  params: Record<string, unknown>;
  lens_recommendations: Array<Record<string, unknown>>;
  detector_recommendations: Array<Record<string, unknown>>;
  notes: string;
  standards: string[];
}

export async function listPresets(domain?: string) {
  const qs = domain ? `?domain=${encodeURIComponent(domain)}` : "";
  return apiFetch<{ items: PresetConfigItem[] }>(`/api/v1/knowledge/presets${qs}`);
}

export async function getPreset(presetId: string) {
  return apiFetch<PresetConfigItem>(`/api/v1/knowledge/presets/${presetId}`);
}
