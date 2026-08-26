/** Domain discovery endpoints (`/api/v1/domains`). */

import { apiFetch } from "./client";

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
