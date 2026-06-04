import { useEffect, useRef } from "react";
import { useTheme } from "../hooks/useTheme";

interface CoverageData {
  sensor_rect: { x: number; y: number; w: number; h: number };
  image_circle: { cx: number; cy: number; r: number };
  vignetting_regions: Array<{ points: Array<{ x: number; y: number }> }>;
  coverage_ratio: number;
  safe_zone: { x: number; y: number; w: number; h: number };
}

interface Props {
  data: CoverageData | null;
  width?: number;
  height?: number;
}

/** Theme-aware palette for canvas rendering. */
function getPalette(isDark: boolean) {
  return {
    bg: isDark ? "#0f172a" : "#f8fafc",
    grid: isDark ? "#1e293b" : "#e2e8f0",
    text: isDark ? "#94a3b8" : "#64748b",
    ringText: isDark ? "#e2e8f0" : "#334155",
    ringBg: isDark ? "#1e293b" : "#e2e8f0",
    cross: isDark ? "rgba(148,163,184,0.3)" : "rgba(148,163,184,0.4)",
  };
}

export default function SensorCoveragePlot({ data, width = 320, height = 280 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const palette = getPalette(isDark);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const W = width;
    const H = height;
    const pad = 32;
    const plotW = W - pad * 2;
    const plotH = H - pad * 2;

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Background with subtle grid
    ctx.fillStyle = palette.bg;
    ctx.fillRect(0, 0, W, H);

    // Grid dots
    ctx.fillStyle = palette.grid;
    for (let gx = pad; gx < W - pad; gx += 16) {
      for (let gy = pad; gy < H - pad; gy += 16) {
        ctx.beginPath();
        ctx.arc(gx, gy, 0.8, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Compute scale
    const maxDim = Math.max(
      Math.abs(data.sensor_rect.x) + data.sensor_rect.w / 2,
      Math.abs(data.sensor_rect.y) + data.sensor_rect.h / 2,
      data.image_circle.r
    ) * 2.6;

    const scale = Math.min(plotW, plotH) / maxDim;
    const cx = W / 2;
    const cy = H / 2;

    // ── Draw Image Circle ──
    const circleR = data.image_circle.r * scale;

    // Circle glow
    const glowGrad = ctx.createRadialGradient(cx, cy, circleR * 0.3, cx, cy, circleR * 1.2);
    glowGrad.addColorStop(0, "rgba(99, 102, 241, 0.04)");
    glowGrad.addColorStop(1, "rgba(99, 102, 241, 0)");
    ctx.fillStyle = glowGrad;
    ctx.fillRect(0, 0, W, H);

    // Circle fill
    ctx.beginPath();
    ctx.arc(cx, cy, circleR, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(99, 102, 241, 0.06)";
    ctx.fill();

    // Circle stroke (dashed)
    ctx.beginPath();
    ctx.arc(cx, cy, circleR, 0, Math.PI * 2);
    ctx.strokeStyle = "#818cf8";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // ── Draw Sensor Rect ──
    const sx = cx + data.sensor_rect.x * scale;
    const sy = cy + data.sensor_rect.y * scale;
    const sw = data.sensor_rect.w * scale;
    const sh = data.sensor_rect.h * scale;

    // Sensor fill
    ctx.fillStyle = "rgba(16, 185, 129, 0.08)";
    ctx.fillRect(sx, sy, sw, sh);

    // Sensor stroke
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 2;
    ctx.strokeRect(sx, sy, sw, sh);

    // Sensor corner markers
    const mk = 4;
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1.5;
    [
      [sx, sy],
      [sx + sw, sy],
      [sx, sy + sh],
      [sx + sw, sy + sh],
    ].forEach(([px, py]) => {
      ctx.beginPath();
      ctx.moveTo(px - mk, py);
      ctx.lineTo(px + mk, py);
      ctx.moveTo(px, py - mk);
      ctx.lineTo(px, py + mk);
      ctx.stroke();
    });

    // ── Draw Safe Zone ──
    if (data.safe_zone) {
      const zx = cx + data.safe_zone.x * scale;
      const zy = cy + data.safe_zone.y * scale;
      const zw = data.safe_zone.w * scale;
      const zh = data.safe_zone.h * scale;

      ctx.fillStyle = "rgba(16, 185, 129, 0.04)";
      ctx.fillRect(zx, zy, zw, zh);
      ctx.strokeStyle = "rgba(16, 185, 129, 0.3)";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(zx, zy, zw, zh);
      ctx.setLineDash([]);
    }

    // ── Draw Vignetting Regions ──
    data.vignetting_regions.forEach((region) => {
      ctx.beginPath();
      region.points.forEach((p, i) => {
        const px = cx + p.x * scale;
        const py = cy + p.y * scale;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.fillStyle = "rgba(244, 63, 94, 0.15)";
      ctx.fill();
      ctx.strokeStyle = "rgba(244, 63, 94, 0.5)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // ── Draw Center Cross ──
    ctx.strokeStyle = palette.cross;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(cx - 6, cy);
    ctx.lineTo(cx + 6, cy);
    ctx.moveTo(cx, cy - 6);
    ctx.lineTo(cx, cy + 6);
    ctx.stroke();

    // ── Legend ──
    const lx = pad;
    const ly = H - pad + 4;
    const lh = 14;

    const legendItems = [
      { color: "#818cf8", label: "像圈", dash: true },
      { color: "#10b981", label: "传感器" },
      { color: "rgba(244, 63, 94, 0.5)", label: "渐晕区" },
    ];

    legendItems.forEach((item, i) => {
      const ix = lx + i * 70;
      ctx.beginPath();
      ctx.moveTo(ix, ly + lh / 2);
      ctx.lineTo(ix + 12, ly + lh / 2);
      ctx.strokeStyle = item.color;
      ctx.lineWidth = 2;
      if (item.dash) ctx.setLineDash([4, 2]);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = palette.text;
      ctx.font = "500 10px Inter, sans-serif";
      ctx.fillText(item.label, ix + 16, ly + lh / 2 + 3.5);
    });

    // ── Coverage Ring Indicator ──
    const ringCX = W - pad - 20;
    const ringCY = pad + 20;
    const ringR = 16;
    const ratio = Math.min(Math.max(data.coverage_ratio || 0, 0), 1);
    const endAngle = -Math.PI / 2 + ratio * Math.PI * 2;

    // Ring bg
    ctx.beginPath();
    ctx.arc(ringCX, ringCY, ringR, 0, Math.PI * 2);
    ctx.strokeStyle = palette.ringBg;
    ctx.lineWidth = 3;
    ctx.stroke();

    // Ring progress
    ctx.beginPath();
    ctx.arc(ringCX, ringCY, ringR, -Math.PI / 2, endAngle);
    const ringGrad = ctx.createLinearGradient(ringCX - ringR, ringCY - ringR, ringCX + ringR, ringCY + ringR);
    if (ratio >= 0.9) {
      ringGrad.addColorStop(0, "#10b981");
      ringGrad.addColorStop(1, "#14b8a6");
    } else if (ratio >= 0.7) {
      ringGrad.addColorStop(0, "#f59e0b");
      ringGrad.addColorStop(1, "#f97316");
    } else {
      ringGrad.addColorStop(0, "#f43f5e");
      ringGrad.addColorStop(1, "#e11d48");
    }
    ctx.strokeStyle = ringGrad;
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.stroke();

    // Ring text
    ctx.fillStyle = palette.ringText;
    ctx.font = "bold 9px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(`${(ratio * 100).toFixed(0)}%`, ringCX, ringCY);

    ctx.textAlign = "start";
    ctx.textBaseline = "alphabetic";
  }, [data, width, height, palette]);

  if (!data) {
    return (
      <div
        className="flex flex-col items-center justify-center rounded-[14px] border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/40"
        style={{ width, height }}
      >
        <div className="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-slate-300 dark:text-slate-500 mb-3">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
            <circle cx="9" cy="9" r="2" />
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
          </svg>
        </div>
        <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">选择镜头和探测器后显示覆盖图</span>
      </div>
    );
  }

  return (
    <div className="relative rounded-[14px] border border-slate-200 dark:border-slate-700 overflow-hidden bg-white dark:bg-slate-900 shadow-sm">
      <canvas
        ref={canvasRef}
        style={{ width, height }}
        className="block"
      />
    </div>
  );
}
