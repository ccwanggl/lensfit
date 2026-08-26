/** Learning content & assessment quiz endpoints (content contract v1, `/api/v1/content/*`). */

import { apiFetch } from "./client";

/* ─── Concepts ─── */
export interface ContentConcept {
  id: string;
  title: string;
  module: string;
  difficulty: string;
  prerequisites: string[];
  linked_experiments: string[];
  status: string;
}

export interface ContentConceptDetail extends ContentConcept {
  body: string;
}

export async function listContentConcepts() {
  return apiFetch<{
    items: ContentConcept[];
    errors: { path: string; error: string }[];
  }>("/api/v1/content/concepts");
}

export async function getContentConcept(id: string) {
  return apiFetch<ContentConceptDetail>(
    `/api/v1/content/concepts/${encodeURIComponent(id)}`
  );
}

/* ─── Assessment quizzes (phase 3) ─── */
export interface QuizQuestion {
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface ContentQuiz {
  id: string;
  title: string;
  module: string;
  concepts: string[];
  pass_score: number;
  questions: QuizQuestion[];
}

export async function listContentQuizzes(concept?: string) {
  const qs = concept ? `?concept=${encodeURIComponent(concept)}` : "";
  return apiFetch<{ items: ContentQuiz[]; errors: { path: string; error: string }[] }>(
    `/api/v1/content/quizzes${qs}`
  );
}

export async function getContentQuiz(quizId: string) {
  return apiFetch<ContentQuiz>(
    `/api/v1/content/quizzes/${encodeURIComponent(quizId)}`
  );
}
