import { useEffect, useMemo, useRef, useState } from "react";
import { computeFraunhoferIntensity } from "./fraunhofer";
import type { WorkbenchScene } from "./workbenchTypes";

interface BreadboardRayCanvasProps {
  scene?: WorkbenchScene;
}

interface ComponentInfo {
  x: number;
  y: number;
  wavelengthNm: number;
  slitWidthUm?: number;
  slitSeparationUm?: number;
  screenX: number;
  screenY: number;
}

function wavelengthToRgb(wavelengthNm: number): [number, number, number] {
  const nm = Math.max(380, Math.min(700, wavelengthNm));
  let r = 0;
  let g = 0;
  let b = 0;
  if (nm >= 380 && nm < 440) {
    r = -(nm - 440) / (440 - 380);
    g = 0;
    b = 1;
  } else if (nm >= 440 && nm < 490) {
    r = 0;
    g = (nm - 440) / (490 - 440);
    b = 1;
  } else if (nm >= 490 && nm < 510) {
    r = 0;
    g = 1;
    b = -(nm - 510) / (510 - 490);
  } else if (nm >= 510 && nm < 580) {
    r = (nm - 510) / (580 - 510);
    g = 1;
    b = 0;
  } else if (nm >= 580 && nm < 645) {
    r = 1;
    g = -(nm - 645) / (645 - 580);
    b = 0;
  } else {
    r = 1;
    g = 0;
    b = 0;
  }
  const f =
    nm < 420 ? 0.3 + (0.7 * (nm - 380)) / 40 :
    nm > 700 ? 0.3 + (0.7 * (780 - nm)) / 80 :
    1;
  const toByte = (v: number) =>
    Math.round(Math.max(0, Math.min(255, v * 255 * f)));
  return [toByte(r), toByte(g), toByte(b)];
}

function wavelengthToColor(wavelengthNm: number): string {
  const [r, g, b] = wavelengthToRgb(wavelengthNm);
  return `rgb(${r}, ${g}, ${b})`;
}

function parseScene(scene?: WorkbenchScene): ComponentInfo | null {
  if (!scene) return null;
  const source = scene.components.find((c) => c.category === "source");
  const aperture = scene.components.find((c) => c.category === "aperture");
  const screen = scene.components.find((c) => c.category === "screen");
  if (!source || !aperture || !screen) return null;

  const wavelengthNm = Number(source.params.wavelength_nm ?? 550);
  const slitWidthUm =
    aperture.params.slit_width_um != null
      ? Number(aperture.params.slit_width_um)
      : undefined;
  const slitSeparationUm =
    aperture.params.slit_separation_um != null
      ? Number(aperture.params.slit_separation_um)
      : undefined;

  return {
    x: aperture.transform.x_mm - source.transform.x_mm,
    y: aperture.transform.y_mm - source.transform.y_mm,
    wavelengthNm,
    slitWidthUm,
    slitSeparationUm,
    screenX: screen.transform.x_mm - source.transform.x_mm,
    screenY: screen.transform.y_mm - source.transform.y_mm,
  };
}

export function BreadboardRayCanvas({ scene }: BreadboardRayCanvasProps) {
  const info = useMemo(() => parseScene(scene), [scene]);
  const intensity = useMemo(
    () => computeFraunhoferIntensity(scene),
    [scene]
  );
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [raysPerSlit, setRaysPerSlit] = useState(60);
  const [showBlocked, setShowBlocked] = useState(true);
  const [showIntensity, setShowIntensity] = useState(true);
  const [hover, setHover] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container || !info) return;

    const dpr = window.devicePixelRatio || 1;
    const cssWidth = container.clientWidth;
    const cssHeight = 384;
    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);
    canvas.style.width = `${cssWidth}px`;
    canvas.style.height = `${cssHeight}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    const padding = { left: 40, right: showIntensity ? 80 : 40, top: 24, bottom: 24 };
    const drawWidth = cssWidth - padding.left - padding.right;
    const drawHeight = cssHeight - padding.top - padding.bottom;

    // Fixed horizontal range so that moving the screen only moves the screen
    // line and changes ray lengths; the aperture/source sizes stay constant.
    const SCENE_X_MIN = -50;
    const SCENE_X_MAX = 3050;
    const xScale = drawWidth / (SCENE_X_MAX - SCENE_X_MIN);

    // Schematic visual scale: real slits are microns and geometric rays are
    // nearly parallel. We exaggerate the whole aperture geometry (slit width
    // and separation) proportionally so the blocking effect remains visible.
    const FAN_ANGLE = Math.PI / 6; // ±30°
    const fanHalfY = info.x * Math.tan(FAN_ANGLE) * 1.05;

    let visualScale = 80;
    const actualHalfWidth = ((info.slitWidthUm ?? 50) / 1000) / 2;
    const actualHalfSep = ((info.slitSeparationUm ?? 0) / 1000) / 2;
    const requiredExtent =
      actualHalfSep > 0
        ? actualHalfSep * visualScale + actualHalfWidth * visualScale
        : actualHalfWidth * visualScale;
    if (requiredExtent > fanHalfY * 0.6) {
      visualScale =
        (fanHalfY * 0.6) /
        (actualHalfSep + actualHalfWidth || actualHalfWidth);
    }
    const minVisualHalf = 0.3;

    // Build visually-scaled openings. Both slit width and slit separation are
    // scaled by the same factor so the proportions look consistent.
    const visualOpenings: Array<{ y0: number; y1: number }> = [];
    if (actualHalfSep > 0) {
      const half = Math.max(minVisualHalf, actualHalfWidth * visualScale);
      const sep = actualHalfSep * visualScale;
      visualOpenings.push(
        { y0: info.y - sep - half, y1: info.y - sep + half },
        { y0: info.y + sep - half, y1: info.y + sep + half }
      );
    } else {
      const half = Math.max(minVisualHalf, actualHalfWidth * visualScale);
      visualOpenings.push({ y0: info.y - half, y1: info.y + half });
    }

    const toCanvasX = (x: number) => padding.left + (x - SCENE_X_MIN) * xScale;

    // Geometry Y scale: the real layout is extremely flat (micron slits vs
    // millimeter distances). We auto-exaggerate Y just enough so the fan of
    // rays and the aperture plate fit nicely in the canvas.
    const geometryYScale = (drawHeight / 2) / (fanHalfY * 1.15);
    const toCanvasY = (y: number) =>
      padding.top + drawHeight / 2 - y * geometryYScale;

    // Intensity is mapped independently so the entire Fraunhofer pattern
    // (including dark fringes) always fits in the vertical drawing area.
    const intensityToCanvasY = (() => {
      if (intensity.samples.length === 0)
        return () => padding.top + drawHeight / 2;
      const yMin = intensity.samples[0].y_mm;
      const yMax = intensity.samples[intensity.samples.length - 1].y_mm;
      const range = yMax - yMin || 1;
      return (y_mm: number) =>
        padding.top + ((yMax - y_mm) / range) * drawHeight;
    })();

    ctx.clearRect(0, 0, cssWidth, cssHeight);

    // Background grid
    ctx.strokeStyle = "rgba(148, 163, 184, 0.15)";
    ctx.lineWidth = 1;
    const xGridStep = 500;
    for (let gx = Math.ceil(SCENE_X_MIN / xGridStep) * xGridStep; gx <= SCENE_X_MAX; gx += xGridStep) {
      ctx.beginPath();
      ctx.moveTo(toCanvasX(gx), padding.top);
      ctx.lineTo(toCanvasX(gx), cssHeight - padding.bottom);
      ctx.stroke();
    }

    // Optical axis
    ctx.strokeStyle = "rgba(148, 163, 184, 0.4)";
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(toCanvasX(SCENE_X_MIN), toCanvasY(0));
    ctx.lineTo(toCanvasX(SCENE_X_MAX), toCanvasY(0));
    ctx.stroke();
    ctx.setLineDash([]);

    const rayColor = wavelengthToColor(info.wavelengthNm);
    const blockedColor = "rgba(239, 68, 68, 0.25)";

    const sourceX = 0;
    const sourceY = 0;

    // Draw source
    ctx.fillStyle = rayColor;
    ctx.beginPath();
    ctx.arc(toCanvasX(sourceX), toCanvasY(sourceY), 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(226, 232, 240, 0.8)";
    ctx.font = "11px sans-serif";
    ctx.fillText("光源", toCanvasX(sourceX) - 12, toCanvasY(sourceY) + 20);

    // Draw blocker / aperture tall enough to intercept the whole fan.
    const blockerTop = info.y - fanHalfY;
    const blockerBottom = info.y + fanHalfY;
    ctx.fillStyle = "rgba(30, 41, 59, 0.9)";
    const ax = toCanvasX(info.x);
    const ayTop = toCanvasY(blockerTop);
    const ayBottom = toCanvasY(blockerBottom);
    ctx.fillRect(ax - 4, ayTop, 8, ayBottom - ayTop);

    // Slit openings (clear the blocker and add a bright edge).
    visualOpenings.forEach((op) => {
      const oy0 = toCanvasY(op.y1);
      const oy1 = toCanvasY(op.y0);
      ctx.clearRect(ax - 5, oy0, 10, oy1 - oy0);
      ctx.strokeStyle = "rgba(226, 232, 240, 0.6)";
      ctx.beginPath();
      ctx.moveTo(ax - 4, oy0);
      ctx.lineTo(ax + 4, oy0);
      ctx.moveTo(ax - 4, oy1);
      ctx.lineTo(ax + 4, oy1);
      ctx.stroke();
    });
    ctx.fillStyle = "rgba(226, 232, 240, 0.8)";
    ctx.fillText("光阑", ax - 12, ayBottom + 16);

    // Draw screen
    const sx = toCanvasX(info.screenX);
    ctx.strokeStyle = "rgba(226, 232, 240, 0.8)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(sx, padding.top);
    ctx.lineTo(sx, cssHeight - padding.bottom);
    ctx.stroke();
    ctx.fillStyle = "rgba(226, 232, 240, 0.8)";
    ctx.fillText("屏幕", sx - 12, cssHeight - padding.bottom + 16);

    // Draw rays as an angular fan from the source. Rays that hit the blocker
    // are truncated at the aperture plane; rays that pass through a visual
    // slit continue to the screen.
    const angleStep = (FAN_ANGLE * 2) / Math.max(1, raysPerSlit);

    ctx.lineWidth = 1;

    for (let i = 0; i <= raysPerSlit; i++) {
      const angle = -FAN_ANGLE + i * angleStep;
      const tanA = Math.tan(angle);

      // Intersection with the aperture plane.
      const apertureY = sourceY + tanA * (info.x - sourceX);

      const isTransmitted = visualOpenings.some(
        (op) => apertureY >= op.y0 && apertureY <= op.y1
      );

      if (isTransmitted) {
        ctx.strokeStyle = rayColor;
        ctx.globalAlpha = 0.45;
        const screenY = sourceY + tanA * (info.screenX - sourceX);
        ctx.beginPath();
        ctx.moveTo(toCanvasX(sourceX), toCanvasY(sourceY));
        ctx.lineTo(toCanvasX(info.screenX), toCanvasY(screenY));
        ctx.stroke();
      } else if (showBlocked) {
        ctx.strokeStyle = blockedColor;
        ctx.globalAlpha = 0.55;
        ctx.beginPath();
        ctx.moveTo(toCanvasX(sourceX), toCanvasY(sourceY));
        ctx.lineTo(toCanvasX(info.x), toCanvasY(apertureY));
        ctx.stroke();
      }
    }

    ctx.globalAlpha = 1;

    // Draw the calculated intensity pattern on/around the screen.
    if (showIntensity && intensity.samples.length > 0) {
      const samples = intensity.samples;
      const [rr, gg, bb] = wavelengthToRgb(info.wavelengthNm);
      const peak = intensity.peakIntensity;

      // 1) Color the screen itself according to the intensity distribution.
      //    The peak brightness is scaled by slit width so narrowing the slit
      //    visibly dims the central maximum.
      const screenStripW = 6;
      for (let i = 0; i < samples.length - 1; i++) {
        const s0 = samples[i];
        const s1 = samples[i + 1];
        const cy0 = intensityToCanvasY(s0.y_mm);
        const cy1 = intensityToCanvasY(s1.y_mm);
        const avg = ((s0.intensity + s1.intensity) / 2) * peak;
        ctx.fillStyle = `rgba(${rr}, ${gg}, ${bb}, ${avg * 0.95})`;
        ctx.fillRect(
          sx - screenStripW / 2,
          Math.min(cy0, cy1),
          screenStripW,
          Math.max(1, Math.abs(cy1 - cy0))
        );
      }

      // 2) Mini sideways profile bar to the right of the screen.
      const gap = 10;
      const barW = 50;
      const barX = sx + gap;

      // Dark background so zero-intensity (dark fringes) reads as black.
      ctx.fillStyle = "rgba(2, 6, 23, 0.85)";
      ctx.fillRect(barX, padding.top, barW, drawHeight);

      for (let i = 0; i < samples.length - 1; i++) {
        const s0 = samples[i];
        const s1 = samples[i + 1];
        const cy0 = intensityToCanvasY(s0.y_mm);
        const cy1 = intensityToCanvasY(s1.y_mm);
        const avg = ((s0.intensity + s1.intensity) / 2) * peak;
        const w = avg * barW;
        ctx.fillStyle = `rgba(${rr}, ${gg}, ${bb}, ${0.2 + avg * 0.8})`;
        ctx.fillRect(barX, Math.min(cy0, cy1), Math.max(1, w), Math.max(1, Math.abs(cy1 - cy0)));
      }

      // Border and label
      ctx.strokeStyle = "rgba(226, 232, 240, 0.4)";
      ctx.lineWidth = 1;
      ctx.strokeRect(barX, padding.top, barW, drawHeight);
      ctx.fillStyle = "rgba(226, 232, 240, 0.8)";
      ctx.font = "10px sans-serif";
      ctx.fillText("相对强度", barX, padding.top - 6);
    }

    // Hover crosshair
    if (hover) {
      ctx.strokeStyle = "rgba(255, 255, 255, 0.5)";
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(hover.x, padding.top);
      ctx.lineTo(hover.x, cssHeight - padding.bottom);
      ctx.moveTo(padding.left, hover.y);
      ctx.lineTo(cssWidth - padding.right, hover.y);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }, [info, raysPerSlit, showBlocked, showIntensity, intensity, hover]);

  if (!info) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border border-slate-200 bg-slate-950 text-sm text-slate-400 dark:border-slate-700">
        <p>请选择有效的面包板实验以查看光路</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200/60 bg-slate-50/60 p-2 text-xs dark:border-slate-700/60 dark:bg-slate-800/60">
        <label className="flex items-center gap-2">
          <span className="text-slate-600 dark:text-slate-400">光线密度</span>
          <input
            type="range"
            min={10}
            max={180}
            step={5}
            value={raysPerSlit}
            onChange={(e) => setRaysPerSlit(Number(e.target.value))}
            className="accent-indigo-500"
          />
          <span className="w-6 text-right font-mono text-slate-700 dark:text-slate-300">
            {raysPerSlit}
          </span>
        </label>
        <label className="flex cursor-pointer items-center gap-1.5 text-slate-600 dark:text-slate-400">
          <input
            type="checkbox"
            checked={showBlocked}
            onChange={(e) => setShowBlocked(e.target.checked)}
            className="accent-indigo-500"
          />
          显示被遮挡光线
        </label>
        <label className="flex cursor-pointer items-center gap-1.5 text-slate-600 dark:text-slate-400">
          <input
            type="checkbox"
            checked={showIntensity}
            onChange={(e) => setShowIntensity(e.target.checked)}
            className="accent-indigo-500"
          />
          屏幕强度条
        </label>
      </div>

      <div
        ref={containerRef}
        className="relative w-full overflow-hidden rounded-lg border border-slate-200 bg-slate-950 dark:border-slate-700"
      >
        <canvas
          ref={canvasRef}
          className="block h-96 w-full cursor-crosshair"
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            setHover({ x: e.clientX - rect.left, y: e.clientY - rect.top });
          }}
          onMouseLeave={() => setHover(null)}
        />
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400">
        提示：光路图为示意性绘制，狭缝和光线均经过视觉放大；强度条按夫琅禾费公式计算，且中央亮纹亮度会随缝宽减小而降低。
      </p>
    </div>
  );
}
