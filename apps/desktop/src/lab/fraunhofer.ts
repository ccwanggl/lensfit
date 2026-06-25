import type { WorkbenchScene } from "./workbenchTypes";

export interface IntensitySample {
  y_mm: number;
  intensity: number;
}

export interface FraunhoferResult {
  available: boolean;
  samples: IntensitySample[];
}

function parsePresetParams(scene: WorkbenchScene) {
  const source = scene.components.find((c) => c.category === "source");
  const aperture = scene.components.find((c) => c.category === "aperture");
  const screen = scene.components.find((c) => c.category === "screen");
  if (!source || !aperture || !screen) return null;

  const wavelengthMm = Number(source.params.wavelength_nm ?? 550) / 1e6;
  const slitWidthMm = Number(aperture.params.slit_width_um ?? 50) / 1000;
  const slitSeparationMm =
    aperture.params.slit_separation_um != null
      ? Number(aperture.params.slit_separation_um) / 1000
      : null;
  const apertureX = aperture.transform.x_mm - source.transform.x_mm;
  const screenX = screen.transform.x_mm - source.transform.x_mm;
  const screenDistanceMm = Math.max(0.1, screenX - apertureX);

  return {
    wavelengthMm,
    slitWidthMm,
    slitSeparationMm,
    screenDistanceMm,
    apertureY: aperture.transform.y_mm - source.transform.y_mm,
    screenY: screen.transform.y_mm - source.transform.y_mm,
    isDoubleSlit: aperture.spec_id === "double-slit",
  };
}

function sinc(x: number): number {
  if (Math.abs(x) < 1e-12) return 1;
  return Math.sin(x) / x;
}

function sampleRange(params: NonNullable<ReturnType<typeof parsePresetParams>>) {
  const { wavelengthMm, slitWidthMm, screenDistanceMm } = params;
  // Central maximum width for the single-slit envelope.
  const centralWidthMm = (2 * wavelengthMm * screenDistanceMm) / slitWidthMm;
  // Show enough of the pattern to see several minima, but cap the range so
  // extremely narrow slits do not produce an unreasonably wide plot.
  const halfRange = Math.min(Math.max(centralWidthMm * 2, 10), 200);
  return { yMin: -halfRange, yMax: halfRange };
}

export function computeFraunhoferIntensity(
  scene?: WorkbenchScene
): FraunhoferResult {
  const params = scene ? parsePresetParams(scene) : null;
  if (!params) {
    return { available: false, samples: [] };
  }

  const {
    wavelengthMm,
    slitWidthMm,
    slitSeparationMm,
    screenDistanceMm,
    screenY,
    isDoubleSlit,
  } = params;

  const { yMin, yMax } = sampleRange(params);
  const sampleCount = 1201;
  const samples: IntensitySample[] = [];
  let maxIntensity = 0;

  for (let i = 0; i < sampleCount; i++) {
    const t = i / (sampleCount - 1);
    const y = yMin + (yMax - yMin) * t - screenY;
    const theta = Math.atan2(y, screenDistanceMm);
    const sinTheta = Math.sin(theta);

    const beta = (Math.PI * slitWidthMm * sinTheta) / wavelengthMm;
    const envelope = sinc(beta) ** 2;

    let intensity = envelope;
    if (isDoubleSlit && slitSeparationMm && slitSeparationMm > 0) {
      const alpha = (Math.PI * slitSeparationMm * sinTheta) / wavelengthMm;
      intensity *= Math.cos(alpha) ** 2;
    }

    samples.push({ y_mm: y + screenY, intensity });
    if (intensity > maxIntensity) maxIntensity = intensity;
  }

  if (maxIntensity > 0) {
    for (const s of samples) {
      s.intensity /= maxIntensity;
    }
  }

  return { available: true, samples };
}
