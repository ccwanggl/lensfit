/** Learner progress endpoints (`/api/v1/learning/progress`). */

import { apiFetch } from "./client";

export type LearningProgressStatus = "viewed" | "completed" | "scored";

export interface LearningProgressItem {
  learner_id: string;
  item_kind: string;
  item_id: string;
  status: string;
  score: number | null;
  updated_at: string | null;
}

export async function getLearningProgress(itemKind?: string) {
  const qs = itemKind ? `?item_kind=${encodeURIComponent(itemKind)}` : "";
  return apiFetch<{ items: LearningProgressItem[] }>(
    `/api/v1/learning/progress${qs}`
  );
}

export async function putLearningProgress(record: {
  item_kind: string;
  item_id: string;
  status: LearningProgressStatus;
  score?: number | null;
}) {
  return apiFetch<LearningProgressItem>("/api/v1/learning/progress", {
    method: "PUT",
    body: JSON.stringify(record),
  });
}
