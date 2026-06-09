/** API client for LensFit engine.
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
  try {
    const base = await getEndpoint();
    const res = await fetch(`${base}/health`);
    if (res.ok) {
      const data = (await res.json()) as { api_key?: string };
      _cachedApiKey = data.api_key ?? null;
    }
  } catch {
    // ignore
  }
  return _cachedApiKey;
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
    throw new Error(`API error: ${res.status} ${res.statusText}`);
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

  if (!res.ok || !res.body) {
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

export async function generateCoverage(lensId: number, detectorId: number) {
  return apiFetch<unknown>("/api/v1/visualize/coverage", {
    method: "POST",
    body: JSON.stringify({ lens_id: lensId, detector_id: detectorId }),
  });
}

export async function listLenses(params?: {
  category?: string;
  mount?: string;
  focal_min?: number;
  focal_max?: number;
  limit?: number;
}) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.mount) qs.set("mount", params.mount);
  if (params?.focal_min != null) qs.set("focal_min", String(params.focal_min));
  if (params?.focal_max != null) qs.set("focal_max", String(params.focal_max));
  if (params?.limit != null) qs.set("limit", String(params.limit));
  return apiFetch<ApiListResponse<CatalogLens>>(`/api/v1/catalog/lenses?${qs.toString()}`);
}

export async function listDetectors(params?: {
  category?: string;
  sensor_format?: string;
  mount?: string;
  limit?: number;
}) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.sensor_format) qs.set("sensor_format", params.sensor_format);
  if (params?.mount) qs.set("mount", params.mount);
  if (params?.limit != null) qs.set("limit", String(params.limit));
  return apiFetch<ApiListResponse<CatalogDetector>>(`/api/v1/catalog/detectors?${qs.toString()}`);
}

export async function exportReport(
  format: "pdf" | "excel",
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
    throw new Error(`Export error: ${res.status} ${res.statusText}`);
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
    throw new Error(`Report error: ${res.status} ${res.statusText}`);
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
