/** API client core for OptiBench engine.
 *
 * In Tauri desktop mode, the endpoint is discovered dynamically from the
 * Rust sidecar supervisor. In web/dev mode it falls back to localhost.
 *
 * Split out of `utils/api.ts` (slice A of the frontend megafile refactor
 * plan); the domain modules next to this file build on `apiFetch`.
 */

let _cachedEndpoint: string | null = null;
let _cachedApiKey: string | null = null;

export async function getEndpoint(): Promise<string> {
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

export async function getApiKey(): Promise<string | null> {
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

export async function apiErrorFromResponse(res: Response): Promise<ApiError> {
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
export async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
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
