/** Knowledge base & preset endpoints (`/api/v1/knowledge/*`). */

import { apiFetch } from "./client";

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
