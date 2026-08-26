/** Visualization endpoints (`/api/v1/visualize/*`). */

import { apiFetch } from "./client";

export interface CoverageData {
  sensor_rect: { x: number; y: number; w: number; h: number };
  image_circle: { cx: number; cy: number; r: number };
  vignetting_regions: Array<{ points: Array<{ x: number; y: number }> }>;
  coverage_ratio: number;
  safe_zone: { x: number; y: number; w: number; h: number };
}

export async function generateCoverage(lensId: number, detectorId: number) {
  return apiFetch<CoverageData>("/api/v1/visualize/coverage", {
    method: "POST",
    body: JSON.stringify({ lens_id: lensId, detector_id: detectorId }),
  });
}

export interface MtfPoint {
  frequency_lpmm: number;
  mtf: number;
  is_nyquist: boolean;
}

export interface MtfData {
  lens_mtf50_lpmm: number;
  detector_nyquist_lpmm: number | null;
  points: MtfPoint[];
}

export async function generateMtf(lensId: number, detectorId: number) {
  return apiFetch<MtfData>("/api/v1/visualize/mtf", {
    method: "POST",
    body: JSON.stringify({ lens_id: lensId, detector_id: detectorId }),
  });
}

export interface CocApertureData {
  aperture: number;
  hyperfocal_m: number;
  near_limit_m: number;
  far_limit_m: number | null;
  dof_total_m: number | null;
}

export interface CocData {
  coc_mm: number;
  sensor_diag_mm: number;
  focus_distance_m: number;
  focal_length_mm: number;
  max_aperture: number;
  apertures: CocApertureData[];
}

export async function generateCoc(
  lensId: number,
  detectorId: number,
  focusDistanceM: number = 2.0
) {
  return apiFetch<CocData>("/api/v1/visualize/coc", {
    method: "POST",
    body: JSON.stringify({
      lens_id: lensId,
      detector_id: detectorId,
      focus_distance_m: focusDistanceM,
    }),
  });
}
