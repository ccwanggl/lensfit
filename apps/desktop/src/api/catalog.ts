/** Catalog endpoints (`/api/v1/catalog/*`) — lenses, detectors, manufacturers, import. */

import { apiFetch, getEndpoint, getApiKey, apiErrorFromResponse } from "./client";
import type { ApiListResponse } from "./types";

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
