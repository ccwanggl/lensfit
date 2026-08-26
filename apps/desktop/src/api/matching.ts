/** Matching & calculation endpoints (`/calculate`, `/match/*`). */

import { apiFetch, getEndpoint, getApiKey, apiErrorFromResponse } from "./client";

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
