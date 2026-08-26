/** Report export endpoint (`POST /api/v1/export`). */

import { getEndpoint, getApiKey, apiErrorFromResponse } from "./client";

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
