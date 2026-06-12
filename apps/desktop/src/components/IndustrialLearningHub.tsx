import { useState, useMemo } from "react";
import { BookOpen, Lightbulb, Activity, Eye, Focus, Layers, Maximize2, Ruler } from "lucide-react";

interface Props {
  form: Record<string, unknown>;
}

type SectionId = "overview" | "relationship" | "focal" | "pixel" | "dof" | "coverage";

interface Section {
  id: SectionId;
  title: string;
  icon: React.ReactNode;
}

const SECTIONS: Section[] = [
  { id: "overview", title: "工业视觉系统概览", icon: <BookOpen size={14} /> },
  { id: "relationship", title: "参数关系总图", icon: <Activity size={14} /> },
  { id: "focal", title: "焦距、视场与工作距离", icon: <Focus size={14} /> },
  { id: "pixel", title: "像素精度", icon: <Maximize2 size={14} /> },
  { id: "dof", title: "景深", icon: <Layers size={14} /> },
  { id: "coverage", title: "传感器覆盖", icon: <Eye size={14} /> },
];

function readNum(form: Record<string, unknown>, key: string, fallback = 0): number {
  const v = form[key];
  return typeof v === "number" ? v : fallback;
}

/** ─── Interactive relationship diagram ─── */
function RelationshipDiagram({ form }: { form: Record<string, unknown> }) {
  const wd = readNum(form, "working_distance_mm", 200);
  const tw = readNum(form, "target_width_mm", 50);
  const th = readNum(form, "target_height_mm", 40);
  const sensor = readNum(form, "sensor_size", 8.8);
  const pixel = readNum(form, "pixel_size_um", 3.45);

  const focal = (wd * sensor) / (tw + sensor);
  const beta = focal / (wd - focal);
  const pxAcc = pixel / (1000 * beta);

  const CX = 200;
  const CY = 160;
  const LENS_R = 18;
  const SCALE = 280 / wd;
  const objLeft = CX - (tw / 2) * SCALE;
  const objRight = CX + (tw / 2) * SCALE;
  const objTop = CY - (th / 2) * SCALE * 0.6;
  const objBottom = CY + (th / 2) * SCALE * 0.6;

  return (
    <div className="space-y-3">
      <svg viewBox="0 0 400 240" className="w-full h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        {/* Object */}
        <rect x={objLeft} y={objTop} width={objRight - objLeft} height={objBottom - objTop} fill="rgba(99,102,241,0.12)" stroke="#6366f1" strokeWidth={1.5} rx={2} />
        <text x={CX} y={objTop - 8} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">被测物（FOV）</text>

        {/* Lens */}
        <line x1={CX} y1={CY - 40} x2={CX} y2={CY + 40} stroke="#475569" strokeWidth={3} />
        <circle cx={CX} cy={CY} r={LENS_R} fill="rgba(71,85,105,0.1)" stroke="#475569" strokeWidth={1.5} />
        <text x={CX + 28} y={CY + 4} className="text-[10px] fill-slate-600 dark:fill-slate-400">镜头</text>

        {/* Sensor */}
        <rect x={CX + 20} y={CY - 30} width={8} height={60} fill="rgba(16,185,129,0.15)" stroke="#10b981" strokeWidth={1.5} />
        <text x={CX + 50} y={CY - 36} className="text-[10px] fill-emerald-600 dark:fill-emerald-400">传感器</text>

        {/* Rays */}
        <line x1={objLeft} y1={objTop} x2={CX} y2={CY - 30} stroke="#6366f1" strokeWidth={1} opacity={0.5} />
        <line x1={objLeft} y1={objBottom} x2={CX} y2={CY + 30} stroke="#6366f1" strokeWidth={1} opacity={0.5} />
        <line x1={objRight} y1={objTop} x2={CX} y2={CY - 30} stroke="#6366f1" strokeWidth={1} opacity={0.5} />
        <line x1={objRight} y1={objBottom} x2={CX} y2={CY + 30} stroke="#6366f1" strokeWidth={1} opacity={0.5} />

        {/* Dimensions */}
        <line x1={CX} y1={CY + 60} x2={objLeft} y2={CY + 60} stroke="#94a3b8" strokeWidth={1} strokeDasharray="3 2" markerStart="url(#arrow)" markerEnd="url(#arrow)" />
        <text x={(CX + objLeft) / 2} y={CY + 74} textAnchor="middle" className="text-[10px] fill-slate-500">WD ≈ {wd.toFixed(0)} mm</text>
      </svg>
      <div className="grid grid-cols-3 gap-2 text-xs text-slate-600 dark:text-slate-300">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500 dark:text-slate-400">推算焦距</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{focal.toFixed(1)} mm</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500 dark:text-slate-400">放大倍率 β</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{beta.toFixed(3)}×</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500 dark:text-slate-400">像素精度</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{pxAcc.toFixed(4)} mm/px</span>
        </div>
      </div>
    </div>
  );
}

/** ─── Focal / FOV interactive diagram ─── */
function FocalDiagram({ form }: { form: Record<string, unknown> }) {
  const wd = readNum(form, "working_distance_mm", 200);
  const tw = readNum(form, "target_width_mm", 50);
  const sensor = readNum(form, "sensor_size", 8.8);
  const focal = (wd * sensor) / (tw + sensor);

  const W = 360;
  const H = 200;
  const CX = 180;
  const CY = 100;
  const SCALE = 240 / wd;
  const objLeft = CX - (tw / 2) * SCALE;
  const objRight = CX + (tw / 2) * SCALE;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-300">
        <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-indigo-500" />目标宽度 {tw} mm</div>
        <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-500" />传感器 {sensor} mm</div>
        <div className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-slate-500" />焦距 {focal.toFixed(1)} mm</div>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        {/* Optical axis */}
        <line x1={40} y1={CY} x2={320} y2={CY} stroke="#cbd5e1" strokeWidth={1} strokeDasharray="4 2" />
        {/* Object */}
        <line x1={objLeft} y1={CY - 30} x2={objRight} y2={CY - 30} stroke="#6366f1" strokeWidth={2} />
        <line x1={objLeft} y1={CY - 30} x2={objLeft} y2={CY} stroke="#6366f1" strokeWidth={1} />
        <line x1={objRight} y1={CY - 30} x2={objRight} y2={CY} stroke="#6366f1" strokeWidth={1} />
        <text x={(objLeft + objRight) / 2} y={CY - 38} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">物方视场 {tw} mm</text>
        {/* Lens */}
        <line x1={CX} y1={CY - 35} x2={CX} y2={CY + 35} stroke="#475569" strokeWidth={3} />
        {/* Sensor */}
        <rect x={CX + 6} y={CY - 25} width={6} height={50} fill="#10b981" fillOpacity={0.2} stroke="#10b981" strokeWidth={1.5} />
        {/* Chief rays */}
        <line x1={objLeft} y1={CY - 30} x2={CX} y2={CY} stroke="#6366f1" strokeWidth={1} opacity={0.5} />
        <line x1={objRight} y1={CY - 30} x2={CX} y2={CY} stroke="#6366f1" strokeWidth={1} opacity={0.5} />
        <line x1={CX} y1={CY} x2={CX + 12} y2={CY - 25} stroke="#10b981" strokeWidth={1} opacity={0.5} />
        <line x1={CX} y1={CY} x2={CX + 12} y2={CY + 25} stroke="#10b981" strokeWidth={1} opacity={0.5} />
        {/* Labels */}
        <text x={CX} y={CY + 56} textAnchor="middle" className="text-[10px] fill-slate-500">WD {wd.toFixed(0)} mm</text>
        <text x={CX + 38} y={CY - 34} className="text-[10px] fill-emerald-600 dark:fill-emerald-400">像高 ≈ {sensor.toFixed(1)} mm</text>
      </svg>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        薄透镜公式告诉我们：在固定工作距离下，想看得越宽（FOV 越大），所需焦距越短；想放大细节（FOV 越小），焦距越长。传感器尺寸越大，同样焦距下视野越广。
      </p>
    </div>
  );
}

/** ─── Pixel accuracy diagram ─── */
function PixelDiagram({ form }: { form: Record<string, unknown> }) {
  const pixel = readNum(form, "pixel_size_um", 3.45);
  const tw = readNum(form, "target_width_mm", 50);
  const sensor = readNum(form, "sensor_size", 8.8);
  const wd = readNum(form, "working_distance_mm", 200);
  const focal = (wd * sensor) / (tw + sensor);
  const beta = focal / (wd - focal);
  const pxAcc = pixel / (1000 * beta);

  const cols = 12;
  const rows = 8;
  const cell = 18;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 240 160" className="w-full max-w-xs h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Pixel grid */}
          {Array.from({ length: cols }).map((_, c) =>
            Array.from({ length: rows }).map((_, r) => (
              <rect
                key={`${c}-${r}`}
                x={20 + c * cell}
                y={20 + r * cell}
                width={cell - 1}
                height={cell - 1}
                fill={(c + r) % 2 === 0 ? "rgba(99,102,241,0.15)" : "rgba(99,102,241,0.08)"}
                stroke="rgba(99,102,241,0.2)"
              />
            ))
          )}
          {/* Highlight one pixel and its physical projection */}
          <rect x={20 + 4 * cell} y={20 + 3 * cell} width={cell - 1} height={cell - 1} fill="rgba(245,158,11,0.3)" stroke="#f59e0b" strokeWidth={2} />
          <text x={20 + 4 * cell + cell / 2} y={20 + 3 * cell + cell / 2 + 3} textAnchor="middle" className="text-[8px] fill-amber-700 dark:fill-amber-400">1 px</text>
          <line x1={20 + 4 * cell + cell / 2} y1={20 + 3 * cell + cell} x2={20 + 4 * cell + cell / 2} y2={150} stroke="#f59e0b" strokeWidth={1} strokeDasharray="2 2" />
          <text x={20 + 4 * cell + cell / 2 + 4} y={146} className="text-[9px] fill-amber-600 dark:fill-amber-400">≈ {pxAcc.toFixed(3)} mm</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        像素精度 = 像元尺寸 ÷ 放大倍率。像元越小、放大倍率越大，每个像素代表的物理尺寸就越小，系统能分辨的细节就越多。
      </p>
    </div>
  );
}

/** ─── Depth of field diagram ─── */
function DOFDiagram({ form }: { form: Record<string, unknown> }) {
  const focal = readNum(form, "focal_length_mm", 25);
  const fNum = readNum(form, "f_number", 2.8) || 2.8;
  const coc = 0.03;
  const focus = readNum(form, "working_distance_mm", 200);
  const H = (focal ** 2) / (fNum * coc) + focal;
  const near = (H * focus) / (H + focus);
  const far = focus >= H ? Infinity : (H * focus) / (H - focus);

  const W = 400;
  const CX = 80;
  const CY = 100;
  const SCALE = 0.35;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
          <span className="block text-[10px] text-slate-500">超焦距 H</span>
          <span className="font-mono font-semibold">{H.toFixed(0)} mm</span>
        </div>
        <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
          <span className="block text-[10px] text-slate-500">近端</span>
          <span className="font-mono font-semibold">{near.toFixed(0)} mm</span>
        </div>
        <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
          <span className="block text-[10px] text-slate-500">远端</span>
          <span className="font-mono font-semibold">{Number.isFinite(far) ? `${far.toFixed(0)} mm` : "∞"}</span>
        </div>
      </div>
      <svg viewBox={`0 0 ${W} 160`} className="w-full h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        {/* Axis */}
        <line x1={30} y1={CY} x2={380} y2={CY} stroke="#cbd5e1" strokeWidth={1} strokeDasharray="4 2" />
        {/* Lens */}
        <line x1={CX} y1={CY - 30} x2={CX} y2={CY + 30} stroke="#475569" strokeWidth={3} />
        {/* Focus plane */}
        <line x1={CX + focus * SCALE} y1={CY - 25} x2={CX + focus * SCALE} y2={CY + 25} stroke="#6366f1" strokeWidth={2} strokeDasharray="4 2" />
        <text x={CX + focus * SCALE} y={CY + 42} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">对焦面 {focus.toFixed(0)} mm</text>
        {/* DOF range */}
        <rect x={CX + near * SCALE} y={CY - 10} width={(Number.isFinite(far) ? far * SCALE : 300) - near * SCALE} height={20} fill="rgba(16,185,129,0.15)" stroke="#10b981" strokeWidth={1} rx={2} />
        <text x={CX + near * SCALE + 40} y={CY + 4} className="text-[10px] fill-emerald-700 dark:fill-emerald-400">清晰范围（景深）</text>
      </svg>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        景深是画面中看起来清晰的深度范围。光圈越小（F 值越大）、焦距越短、对焦距离越远，景深越大。工业测量中，过浅的景深会导致被测面偏离焦点时模糊。
      </p>
    </div>
  );
}

/** ─── Sensor coverage diagram ─── */
function CoverageDiagram({ form }: { form: Record<string, unknown> }) {
  const sensor = readNum(form, "sensor_size", 8.8);
  const imageCircle = 11.0; // default illustrative value
  const ratio = Math.min(1, (imageCircle / sensor) ** 2);

  const CX = 120;
  const CY = 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 240 200" className="w-full max-w-xs h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Image circle */}
          <circle cx={CX} cy={CY} r={imageCircle * 8} fill="rgba(99,102,241,0.08)" stroke="#6366f1" strokeWidth={1.5} />
          <text x={CX} y={CY - imageCircle * 8 - 8} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">像圈 {imageCircle} mm</text>
          {/* Sensor rect */}
          <rect x={CX - (sensor * 8) / 2} y={CY - (sensor * 8) / 2} width={sensor * 8} height={sensor * 8} fill="rgba(16,185,129,0.2)" stroke="#10b981" strokeWidth={2} rx={2} />
          <text x={CX} y={CY + 4} textAnchor="middle" className="text-[10px] fill-emerald-700 dark:fill-emerald-400">传感器 {sensor} mm</text>
        </svg>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
          <span className="block text-[10px] text-slate-500">覆盖比例</span>
          <span className="font-mono font-semibold">{(ratio * 100).toFixed(0)}%</span>
        </div>
        <div className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
          <span className="block text-[10px] text-slate-500">状态</span>
          <span className={`font-semibold ${ratio >= 1 ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"}`}>
            {ratio >= 1 ? "无暗角" : "可能暗角"}
          </span>
        </div>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        镜头能均匀成像的圆形区域叫像圈。像圈必须覆盖传感器对角线，否则四角光线不足，产生渐晕。传感器越大，需要镜头的像圈也越大。
      </p>
    </div>
  );
}

/** ─── Section content renderer ─── */
function SectionContent({ section, form }: { section: SectionId; form: Record<string, unknown> }) {
  switch (section) {
    case "overview":
      return (
        <div className="space-y-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
          <p>
            工业视觉系统的核心任务是让相机“看清”被测物体，并把图像交给算法处理。一个完整的选型过程需要同时考虑
            <strong>光学</strong>、<strong>机械</strong>和<strong>电子</strong>三方面的约束。
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { title: "传感器", desc: "决定感光面积和像素数量。尺寸越大，进光量越多；像素越小，细节越丰富。" },
              { title: "镜头", desc: "决定视角、放大倍率和景深。焦距、光圈、像圈是主要参数。" },
              { title: "工作距离", desc: "镜头前端到被测面的距离。它直接决定所需焦距和可拍摄范围。" },
              { title: "接口", desc: "C-mount、F-mount 等机械接口必须匹配，否则无法安装或合焦。" },
            ].map((item) => (
              <div key={item.title} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
                <p className="font-semibold text-slate-800 dark:text-slate-100 mb-1">{item.title}</p>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/15 border border-amber-100 dark:border-amber-800/20 text-xs text-amber-800 dark:text-amber-300">
            <Lightbulb size={14} className="shrink-0 mt-0.5" />
            <p>选型时没有唯一正确答案。通常需要在分辨率、景深、成本、安装空间之间做权衡。下面的章节会告诉你每个参数如何影响最终结果。</p>
          </div>
        </div>
      );
    case "relationship":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            工业视觉中最常用的关系链是：<strong>工作距离 WD</strong> → <strong>视场 FOV</strong> → <strong>焦距 f</strong> → <strong>放大倍率 β</strong> → <strong>像素精度</strong>。
            修改左侧表单中的任意一个参数，下图和三个关键指标都会实时更新。
          </p>
          <RelationshipDiagram form={form} />
        </div>
      );
    case "focal":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            薄透镜成像公式 <span className="font-mono text-indigo-600 dark:text-indigo-400">f = (WD × s) / (FOV + s)</span> 是工业选型的起点。
            它说明焦距由工作距离、目标宽度和传感器宽度共同决定。
          </p>
          <FocalDiagram form={form} />
        </div>
      );
    case "pixel":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            像素精度衡量“一个像素代表多少实际物理尺寸”。例如 5 μm/px 意味着每个像素对应 5 微米。精度越高，能检测的缺陷越小，但对镜头和照明要求也越高。
          </p>
          <PixelDiagram form={form} />
        </div>
      );
    case "dof":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            景深决定被测物体在前后移动时仍能保持清晰的范围。工业检测中，如果物体平面不完全平整或定位有误差，就需要更大的景深。
          </p>
          <DOFDiagram form={form} />
        </div>
      );
    case "coverage":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            即使焦距和分辨率都满足，如果镜头的像圈盖不住传感器，图像四角也会变暗。大靶面相机必须搭配大像圈镜头。
          </p>
          <CoverageDiagram form={form} />
        </div>
      );
    default:
      return null;
  }
}

export default function IndustrialLearningHub({ form }: Props) {
  const [activeSection, setActiveSection] = useState<SectionId>("overview");

  const currentSection = useMemo(() => SECTIONS.find((s) => s.id === activeSection)!, [activeSection]);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen size={16} className="text-indigo-500" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">工业视觉学习指南</h3>
      </div>

      {/* Section nav */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {SECTIONS.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeSection === section.id
                ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-800/30"
                : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
          >
            {section.icon}
            {section.title}
          </button>
        ))}
      </div>

      {/* Content card */}
      <div className="flex-1 min-h-0 overflow-y-auto pr-1">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 shadow-sm space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-700">
            <span className="text-indigo-500">{currentSection.icon}</span>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100">{currentSection.title}</h4>
          </div>
          <SectionContent section={activeSection} form={form} />
        </div>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed flex items-start gap-2">
          <Ruler size={14} className="shrink-0 mt-0.5" />
          提示：修改左侧表单参数，本面板中的公式、图表和指标会同步变化。试着调整“工作距离”或“目标宽度”，观察焦距和像素精度如何改变。
        </p>
      </div>
    </div>
  );
}
