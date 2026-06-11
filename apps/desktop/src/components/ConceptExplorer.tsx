import { useState, useCallback } from "react";
import { Eye, Maximize, Focus, Layers, Info } from "lucide-react";

/* ═════════════════════════════════════════════════════════════════
   Diagram 1: Thin Lens Ray Tracer
   ═════════════════════════════════════════════════════════════════ */

function ThinLensDiagram() {
  const SVG_W = 560;
  const SVG_H = 300;
  const CX = SVG_W / 2;
  const CY = SVG_H / 2;
  const SCALE = 4; // px per mm
  const f = 50; // focal length (mm)

  const [objectX, setObjectX] = useState(CX - 150); // object position in px

  // Convert px to optical coordinates (mm from lens center)
  const u_mm = (CX - objectX) / SCALE; // object distance
  const v_mm = u_mm > f ? (f * u_mm) / (u_mm - f) : 0; // image distance
  const imageX = CX + v_mm * SCALE;
  const magnification = v_mm / u_mm;
  const objectH = 30; // px
  const imageH = objectH * magnification;

  const handleDrag = useCallback((e: React.MouseEvent<SVGGElement>) => {
    const svg = e.currentTarget.ownerSVGElement;
    if (!svg) return;
    // const rect = svg.getBoundingClientRect();
    const startX = e.clientX;
    const startObjX = objectX;

    const onMove = (ev: MouseEvent) => {
      const dx = ev.clientX - startX;
      let nx = startObjX + dx;
      // clamp: object must be left of lens, and u > f + small margin
      nx = Math.min(CX - (f + 5) * SCALE, Math.max(20, nx));
      setObjectX(nx);
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }, [objectX]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Info size={12} />
        <span>拖动物体（红色箭头）改变物距，观察像的位置变化</span>
      </div>
      <svg viewBox={`0 0 ${SVG_W} ${SVG_H}`} className="w-full h-64 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700 select-none">
        {/* Optical axis */}
        <line x1="0" y1={CY} x2={SVG_W} y2={CY} stroke="currentColor" className="text-slate-300 dark:text-slate-600" strokeWidth={1} strokeDasharray="4 4" />

        {/* Focal points */}
        <circle cx={CX - f * SCALE} cy={CY} r={3} fill="#6366f1" />
        <text x={CX - f * SCALE} y={CY + 16} textAnchor="middle" fontSize="10" fill="#6366f1" className="dark:fill-indigo-400">F</text>
        <circle cx={CX + f * SCALE} cy={CY} r={3} fill="#6366f1" />
        <text x={CX + f * SCALE} y={CY + 16} textAnchor="middle" fontSize="10" fill="#6366f1" className="dark:fill-indigo-400">F'</text>

        {/* Lens */}
        <line x1={CX} y1={CY - 60} x2={CX} y2={CY + 60} stroke="currentColor" className="text-slate-700 dark:text-slate-300" strokeWidth={3} />
        <text x={CX} y={CY - 70} textAnchor="middle" fontSize="10" fill="currentColor" className="text-slate-500 dark:text-slate-400">透镜</text>

        {/* Object (draggable) */}
        <g style={{ cursor: "ew-resize" }} onMouseDown={handleDrag}>
          <line x1={objectX} y1={CY} x2={objectX} y2={CY - objectH} stroke="#ef4444" strokeWidth={2} />
          <polygon points={`${objectX-5},${CY-objectH} ${objectX+5},${CY-objectH} ${objectX},${CY-objectH-10}`} fill="#ef4444" />
          <text x={objectX} y={CY + 16} textAnchor="middle" fontSize="10" fill="#ef4444">物</text>
        </g>

        {/* Image */}
        {u_mm > f && Number.isFinite(v_mm) && (
          <>
            <line x1={imageX} y1={CY} x2={imageX} y2={CY + imageH} stroke="#10b981" strokeWidth={2} />
            <polygon points={`${imageX-5},${CY+imageH} ${imageX+5},${CY+imageH} ${imageX},${CY+imageH+10}`} fill="#10b981" />
            <text x={imageX} y={CY - 10} textAnchor="middle" fontSize="10" fill="#10b981">像</text>
          </>
        )}
        {u_mm <= f && (
          <text x={CX + 80} y={CY - 20} fontSize="11" fill="#f59e0b">虚像（同侧，放大镜模式）</text>
        )}

        {/* Rays */}
        {u_mm > f && (
          <>
            {/* Ray 1: parallel to axis → through F' */}
            <line x1={objectX} y1={CY - objectH} x2={CX} y2={CY - objectH} stroke="#6366f1" strokeWidth={1} opacity={0.5} />
            <line x1={CX} y1={CY - objectH} x2={imageX} y2={CY + imageH} stroke="#6366f1" strokeWidth={1} opacity={0.5} />

            {/* Ray 2: through center (straight) */}
            <line x1={objectX} y1={CY - objectH} x2={imageX} y2={CY + imageH} stroke="#8b5cf6" strokeWidth={1} opacity={0.5} strokeDasharray="4 2" />

            {/* Ray 3: through F → parallel */}
            <line x1={objectX} y1={CY - objectH} x2={CX - f * SCALE} y2={CY} stroke="#06b6d4" strokeWidth={1} opacity={0.5} />
            <line x1={CX - f * SCALE} y1={CY} x2={CX + (imageX - CX) * 2} y2={CY - objectH} stroke="#06b6d4" strokeWidth={1} opacity={0.5} />
          </>
        )}

        {/* Labels */}
        <text x="10" y={SVG_H - 10} fontSize="10" fill="currentColor" className="text-slate-400 dark:text-slate-500">f = 50mm（固定）</text>
      </svg>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-2">
        <MetricCard label="物距 u" value={`${u_mm.toFixed(1)} mm`} />
        <MetricCard label="像距 v" value={u_mm > f ? `${v_mm.toFixed(1)} mm` : "∞（虚像）"} />
        <MetricCard label="放大倍率 β" value={u_mm > f ? `${magnification.toFixed(3)}` : "—"} />
      </div>
    </div>
  );
}

/* ═════════════════════════════════════════════════════════════════
   Diagram 2: Sensor Coverage Visualizer
   ═════════════════════════════════════════════════════════════════ */

function CoverageDiagram() {
  const [sensorW, setSensorW] = useState(60); // px half-width
  const [sensorH, setSensorH] = useState(45); // px half-height
  const [imageCircle, setImageCircle] = useState(80); // px radius

  const sensorDiag = Math.sqrt(sensorW ** 2 + sensorH ** 2);
  const coverage = sensorDiag === 0 ? 0 : Math.min(1, (imageCircle / sensorDiag) ** 2);
  const fullyCovered = imageCircle >= sensorDiag;
  const cornerDist = Math.sqrt(sensorW ** 2 + sensorH ** 2);
  const cornerCovered = cornerDist <= imageCircle;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Info size={12} />
        <span>拖动滑块改变传感器尺寸和像圈大小，观察覆盖关系</span>
      </div>

      <svg viewBox="0 0 300 240" className="w-full h-52 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700">
        {/* Image circle */}
        <circle cx="150" cy="120" r={imageCircle} fill={fullyCovered ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)"} stroke={fullyCovered ? "#10b981" : "#f59e0b"} strokeWidth={2} />
        <text x="150" y={120 - imageCircle - 6} textAnchor="middle" fontSize="10" fill={fullyCovered ? "#10b981" : "#f59e0b"}>像圈</text>

        {/* Sensor rectangle */}
        <rect
          x={150 - sensorW}
          y={120 - sensorH}
          width={sensorW * 2}
          height={sensorH * 2}
          fill={fullyCovered ? "rgba(99,102,241,0.2)" : cornerCovered ? "rgba(245,158,11,0.2)" : "rgba(239,68,68,0.2)"}
          stroke={fullyCovered ? "#6366f1" : cornerCovered ? "#f59e0b" : "#ef4444"}
          strokeWidth={2}
        />
        <text x={150} y={120 + sensorH + 14} textAnchor="middle" fontSize="10" fill="#6366f1">传感器</text>

        {/* Center dot */}
        <circle cx="150" cy="120" r={2} fill="currentColor" className="text-slate-400" />
      </svg>

      {/* Controls */}
      <div className="space-y-2">
        <SliderControl label="传感器半宽" value={sensorW} min={10} max={120} unit="px" onChange={setSensorW} />
        <SliderControl label="传感器半高" value={sensorH} min={10} max={100} unit="px" onChange={setSensorH} />
        <SliderControl label="像圈半径" value={imageCircle} min={20} max={140} unit="px" onChange={setImageCircle} />
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-2">
        <MetricCard
          label="覆盖比"
          value={`${(coverage * 100).toFixed(1)}%`}
          color={fullyCovered ? "text-emerald-600 dark:text-emerald-400" : cornerCovered ? "text-amber-600 dark:text-amber-400" : "text-rose-600 dark:text-rose-400"}
        />
        <MetricCard
          label="状态"
          value={fullyCovered ? "完全覆盖 ✅" : cornerCovered ? "轻微渐晕 ⚠️" : "严重暗角 ❌"}
          color={fullyCovered ? "text-emerald-600 dark:text-emerald-400" : cornerCovered ? "text-amber-600 dark:text-amber-400" : "text-rose-600 dark:text-rose-400"}
        />
      </div>
    </div>
  );
}

/* ═════════════════════════════════════════════════════════════════
   Diagram 3: Nyquist / Aliasing Visualizer
   ═════════════════════════════════════════════════════════════════ */

function NyquistDiagram() {
  const [pixelSize, setPixelSize] = useState(3.45);
  const [mtf50, setMtf50] = useState(80);

  const nyquist = 1000 / (2 * pixelSize);
  const oversampling = mtf50 / nyquist;
  const bars = 40;

  // Generate pattern: optical signal vs sampled signal
  const opticalFreq = mtf50 / 2; // spatial frequency in the scene
  // const samplingFreq = nyquist;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Info size={12} />
        <span>调整像元尺寸和镜头 MTF50，观察奈奎斯特采样关系</span>
      </div>

      {/* Sliders */}
      <div className="space-y-2">
        <SliderControl label="像元尺寸" value={pixelSize} min={0.8} max={10} step={0.1} unit="μm" onChange={setPixelSize} />
        <SliderControl label="镜头 MTF50" value={mtf50} min={10} max={200} step={5} unit="lp/mm" onChange={setMtf50} />
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-2">
        <MetricCard label="奈奎斯特频率" value={`${nyquist.toFixed(1)} lp/mm`} />
        <MetricCard label="过采样率" value={oversampling.toFixed(2)} color={oversampling >= 0.5 && oversampling <= 1.2 ? "text-emerald-600 dark:text-emerald-400" : oversampling < 0.5 ? "text-rose-600 dark:text-rose-400" : "text-amber-600 dark:text-amber-400"} />
        <MetricCard
          label="匹配状态"
          value={oversampling >= 0.5 && oversampling <= 1.2 ? "理想 ✅" : oversampling < 0.5 ? "欠采样 ❌" : "过采样 ⚠️"}
          color={oversampling >= 0.5 && oversampling <= 1.2 ? "text-emerald-600 dark:text-emerald-400" : oversampling < 0.5 ? "text-rose-600 dark:text-rose-400" : "text-amber-600 dark:text-amber-400"}
        />
      </div>

      {/* Visualization */}
      <svg viewBox="0 0 400 120" className="w-full h-28 bg-white dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700">
        {/* Optical signal (high freq) */}
        <g transform="translate(0, 30)">
          <text x="5" y="-8" fontSize="9" fill="#6366f1">光学信号（镜头能分辨的频率）</text>
          {Array.from({ length: bars }).map((_, i) => {
            const v = Math.sin((i / bars) * Math.PI * 2 * (opticalFreq / 20)) > 0 ? 1 : 0;
            return <rect key={i} x={10 + i * 9.5} y={v ? 0 : 10} width={8} height={10} fill="#6366f1" opacity={0.6} />;
          })}
        </g>

        {/* Sampling grid */}
        <g transform="translate(0, 65)">
          <text x="5" y="-8" fontSize="9" fill="#f59e0b">传感器采样（像素）</text>
          {Array.from({ length: Math.floor(bars * (pixelSize / 10)) }).map((_, i) => {
            const srcIdx = Math.floor(i * (bars / Math.floor(bars * (pixelSize / 10))));
            const v = Math.sin((srcIdx / bars) * Math.PI * 2 * (opticalFreq / 20)) > 0 ? 1 : 0;
            return <rect key={i} x={10 + i * (380 / Math.floor(bars * (pixelSize / 10)))} y={v ? 0 : 10} width={(380 / Math.floor(bars * (pixelSize / 10))) - 1} height={10} fill="#f59e0b" opacity={0.7} />;
          })}
        </g>

        {/* Aliasing indicator */}
        {oversampling < 0.5 && (
          <text x="200" y="110" textAnchor="middle" fontSize="10" fill="#ef4444">⚠️ 混叠警告：镜头分辨率超过传感器奈奎斯特极限</text>
        )}
      </svg>
    </div>
  );
}

/* ═════════════════════════════════════════════════════════════════
   Shared UI Components
   ═════════════════════════════════════════════════════════════════ */

function MetricCard({ label, value, color = "text-slate-700 dark:text-slate-200" }: { label: string; value: string; color?: string }) {
  return (
    <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
      <p className="text-[10px] text-slate-500 dark:text-slate-400 uppercase">{label}</p>
      <p className={`text-sm font-mono font-bold ${color}`}>{value}</p>
    </div>
  );
}

function SliderControl({ label, value, min, max, step = 1, unit, onChange }: {
  label: string; value: number; min: number; max: number; step?: number; unit: string; onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-0.5">
        <span className="text-xs text-slate-600 dark:text-slate-300">{label}</span>
        <span className="text-xs font-mono text-slate-500 dark:text-slate-400">{value.toFixed(step < 1 ? 1 : 0)} {unit}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full appearance-none cursor-pointer accent-indigo-500"
      />
    </div>
  );
}

/* ═════════════════════════════════════════════════════════════════
   Main Explorer Component
   ═════════════════════════════════════════════════════════════════ */

const DIAGRAMS = [
  { id: "lens", label: "薄透镜光路", icon: <Focus size={14} />, component: ThinLensDiagram },
  { id: "coverage", label: "像圈覆盖", icon: <Maximize size={14} />, component: CoverageDiagram },
  { id: "nyquist", label: "奈奎斯特采样", icon: <Layers size={14} />, component: NyquistDiagram },
] as const;

export default function ConceptExplorer() {
  const [active, setActive] = useState<string>("lens");
  const Diagram = DIAGRAMS.find((d) => d.id === active)?.component ?? ThinLensDiagram;

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-lg bg-violet-50 dark:bg-violet-900/30 flex items-center justify-center text-violet-600 dark:text-violet-400">
          <Eye size={16} />
        </div>
        <div>
          <h2 className="text-sm font-bold text-slate-900 dark:text-slate-100">概念图解</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">交互式光学原理可视化</p>
        </div>
      </div>

      {/* Diagram selector */}
      <div className="flex gap-1.5 mb-4">
        {DIAGRAMS.map((d) => (
          <button
            key={d.id}
            onClick={() => setActive(d.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              active === d.id
                ? "bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-400 border border-violet-200 dark:border-violet-800/40"
                : "bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700"
            }`}
          >
            {d.icon}
            {d.label}
          </button>
        ))}
      </div>

      {/* Diagram area */}
      <div className="flex-1 min-h-0 overflow-y-auto pr-1">
        <Diagram />
      </div>
    </div>
  );
}
