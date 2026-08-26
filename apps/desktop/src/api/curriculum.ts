/** Curriculum learning-path graph endpoint (`GET /api/v1/curriculum/graph`). */

import { apiFetch } from "./client";

export type CurriculumNodeKind = "concept" | "experiment" | "preset" | "practice" | "assessment";

export interface CurriculumNode {
  id: string;
  kind: CurriculumNodeKind;
  ref: string;
  title: string;
  module: string;
  prerequisites: string[];
  status: string;
}

export interface CurriculumEdge {
  from_id: string;
  to_id: string;
}

export async function getCurriculumGraph() {
  return apiFetch<{ nodes: CurriculumNode[]; edges: CurriculumEdge[] }>(
    "/api/v1/curriculum/graph"
  );
}
