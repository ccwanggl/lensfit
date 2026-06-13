import { useState, useMemo, useEffect } from "react";
import { BookOpen, Lightbulb, Radio, Thermometer, Eye, Ruler, HelpCircle } from "lucide-react";
import LearningQuiz from "./LearningQuiz";
import { useLearningProgress } from "../hooks/useLearningProgress";

interface Props {
  form: Record<string, unknown>;
}

type SectionId = "overview" | "bands" | "fov" | "resolution" | "sensitivity" | "quiz";

interface Section {
  id: SectionId;
  title: string;
  icon: React.ReactNode;
}

const SECTIONS: Section[] = [
  { id: "overview", title: "红外成像概览", icon: <BookOpen size={14} /> },
  { id: "bands", title: "红外波段", icon: <Radio size={14} /> },
  { id: "fov", title: "视场与焦距", icon: <Eye size={14} /> },
  { id: "resolution", title: "空间分辨率", icon: <Ruler size={14} /> },
  { id: "sensitivity", title: "热灵敏度", icon: <Thermometer size={14} /> },
];

function readNum(form: Record<string, unknown>, key: string, fallback = 0): number {
  const v = form[key];
  return typeof v === "number" ? v : fallback;
}

function readStr(form: Record<string, unknown>, key: string, fallback = ""): string {
  const v = form[key];
  return typeof v === "string" ? v : fallback;
}

function getBandInfo(band: string): { min: number; max: number; color: string } {
  switch (band) {
    case "swir": return { min: 0.9, max: 1.7, color: "#6366f1" };
    case "mwir": return { min: 3, max: 5, color: "#f59e0b" };
    case "lwir": return { min: 8, max: 14, color: "#ef4444" };
    default: return { min: 8, max: 14, color: "#ef4444" };
  }
}

/** ─── IR bands diagram ─── */
function BandsDiagram({ form }: { form: Record<string, unknown> }) {
  const band = readStr(form, "band", "lwir");
  const info = getBandInfo(band);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 360 120" className="w-full max-w-md h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Spectrum bar */}
          <defs>
            <linearGradient id="irGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="40%" stopColor="#10b981" />
              <stop offset="70%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
          </defs>
          <rect x={30} y={50} width={300} height={20} fill="url(#irGradient)" rx={4} />
          {/* Labels */}
          <text x={80} y={45} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">SWIR</text>
          <text x={170} y={45} textAnchor="middle" className="text-[10px] fill-emerald-600 dark:fill-emerald-400">MWIR</text>
          <text x={260} y={45} textAnchor="middle" className="text-[10px] fill-rose-600 dark:fill-rose-400">LWIR</text>
          <text x={30} y={90} className="text-[9px] fill-slate-500">0.9 μm</text>
          <text x={330} y={90} textAnchor="end" className="text-[9px] fill-slate-500">14 μm</text>
          {/* Selected band marker */}
          <line x1={30 + ((info.min - 0.9) / 13.1) * 300} y1={40} x2={30 + ((info.max - 0.9) / 13.1) * 300} y2={40} stroke={info.color} strokeWidth={3} strokeLinecap="round" />
          <text x={30 + ((info.min + info.max) / 2 - 0.9) / 13.1 * 300} y={32} textAnchor="middle" className="text-[10px] font-semibold" style={{ fill: info.color }}>当前选择</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        SWIR 用于硅片检测；MWIR 用于高温目标；LWIR 用于常温体温/热成像。波段决定了探测器材料、镜头镀膜和应用场景。
      </p>
    </div>
  );
}

/** ─── FOV / focal diagram ─── */
function FOVDiagram({ form }: { form: Record<string, unknown> }) {
  const fov = readNum(form, "fov_deg", 30);
  const wd = readNum(form, "working_distance_m", 5);

  const W = 320;
  const CX = 160;
  const CY = 120;
  const len = 90;
  const halfRad = (fov * Math.PI) / 360;
  const x1 = CX - len * Math.sin(halfRad);
  const x2 = CX + len * Math.sin(halfRad);
  const y = CY - len * Math.cos(halfRad);
  const groundWidth = 2 * wd * Math.tan(halfRad);

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">视场角</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{fov.toFixed(1)}°</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">地面覆盖宽度</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{groundWidth.toFixed(2)} m</span>
        </div>
      </div>
      <div className="flex items-center justify-center">
        <svg viewBox={`0 0 ${W} 170`} className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Camera */}
          <rect x={CX - 10} y={CY - 6} width={20} height={12} fill="#475569" rx={2} />
          {/* FOV rays */}
          <line x1={CX} y1={CY} x2={x1} y2={y} stroke="#6366f1" strokeWidth={1.5} />
          <line x1={CX} y1={CY} x2={x2} y2={y} stroke="#6366f1" strokeWidth={1.5} />
          {/* Ground line */}
          <line x1={x1} y1={y} x2={x2} y2={y} stroke="#10b981" strokeWidth={2} />
          <text x={CX} y={y + 16} textAnchor="middle" className="text-[10px] fill-emerald-600 dark:fill-emerald-400">地面覆盖</text>
          <text x={CX} y={CY + 28} textAnchor="middle" className="text-[10px] fill-slate-500">WD {wd.toFixed(1)} m</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        视场角越大，单个画面覆盖的地面范围越广；焦距越短，视场角越大。红外监控常需要权衡覆盖范围与目标分辨率。
      </p>
    </div>
  );
}

/** ─── Spatial resolution diagram ─── */
function ResolutionDiagram({ form }: { form: Record<string, unknown> }) {
  const pixel = readNum(form, "pixel_size_um", 17);
  const sensorFormat = readStr(form, "sensor_format", "1/2");
  const fov = readNum(form, "fov_deg", 30);

  // simplified sensor width in mm by format
  const sensorWidths: Record<string, number> = {
    "1/4": 3.2, "1/3": 4.8, "1/2": 6.4, "2/3": 8.8, "1": 12.8,
  };
  const sensorW = sensorWidths[sensorFormat] ?? 6.4;
  const resolutionW = Math.round(sensorW * 1000 / pixel);
  const groundRes = (2 * Math.tan((fov * Math.PI) / 360) * 5 * 1000) / resolutionW; // cm/px at 5m

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">图像分辨率</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{resolutionW} px</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">目标分辨率（5m处）</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{groundRes.toFixed(1)} cm/px</span>
        </div>
      </div>
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 280 120" className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {Array.from({ length: 10 }).map((_, c) =>
            Array.from({ length: 6 }).map((_, r) => (
              <rect
                key={`${c}-${r}`}
                x={20 + c * 24}
                y={20 + r * 14}
                width={22}
                height={12}
                fill={(c + r) % 2 === 0 ? "rgba(99,102,241,0.2)" : "rgba(99,102,241,0.08)"}
                stroke="rgba(99,102,241,0.3)"
              />
            ))
          )}
          <text x={140} y={110} textAnchor="middle" className="text-[10px] fill-slate-500">红外探测器像素阵列</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        空间分辨率决定系统能分辨的最小目标尺寸。像元越小、视场角越小、工作距离越近，空间分辨率越高。
      </p>
    </div>
  );
}

/** ─── Sensitivity diagram ─── */
function SensitivityDiagram({ form }: { form: Record<string, unknown> }) {
  const band = readStr(form, "band", "lwir");
  const netd = band === "lwir" ? 50 : 100; // illustrative

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 280 120" className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Temperature scale */}
          <rect x={40} y={50} width={200} height={20} fill="url(#tempGradient)" rx={4} />
          <defs>
            <linearGradient id="tempGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="50%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
          </defs>
          <text x={40} y={90} className="text-[9px] fill-slate-500">低温</text>
          <text x={240} y={90} textAnchor="end" className="text-[9px] fill-slate-500">高温</text>
          {/* NETD marker */}
          <line x1={130} y1={40} x2={150} y2={40} stroke="#f59e0b" strokeWidth={2} />
          <text x={140} y={35} textAnchor="middle" className="text-[10px] fill-amber-600 dark:fill-amber-400">可分辨温差 ≈ {netd} mK</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        NETD（噪声等效温差）表示热像仪能分辨的最小温度差。NETD 越小，对温度差异越敏感。LWIR 系统通常用于常温目标检测。
      </p>
    </div>
  );
}

function SectionContent({ section, form }: { section: SectionId; form: Record<string, unknown> }) {
  switch (section) {
    case "overview":
      return (
        <div className="space-y-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
          <p>
            红外成像系统通过探测物体发出的热辐射成像。它由<strong>红外镜头</strong>、<strong>探测器</strong>、<strong>信号处理电路</strong>和<strong>机械结构</strong>组成。
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { title: "波段", desc: "决定探测器材料和应用场景。SWIR/MWIR/LWIR 对应不同波长范围。" },
              { title: "镜头", desc: "需要针对红外波段镀膜，普通可见光镜头无法使用。" },
              { title: "探测器", desc: "像元尺寸和阵列规模决定空间分辨率。LWIR 常用非制冷微测辐射热计。" },
              { title: "NETD", desc: "热灵敏度指标。值越小，越能分辨微弱温度差异。" },
            ].map((item) => (
              <div key={item.title} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
                <p className="font-semibold text-slate-800 dark:text-slate-100 mb-1">{item.title}</p>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/15 border border-amber-100 dark:border-amber-800/20 text-xs text-amber-800 dark:text-amber-300">
            <Lightbulb size={14} className="shrink-0 mt-0.5" />
            <p>红外选型需要同时考虑波段透射、空间分辨率和热灵敏度。不同波段的大气透过率也不同，会影响远距离成像效果。</p>
          </div>
        </div>
      );
    case "bands":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            红外按波长分为 SWIR、MWIR、LWIR。波段选择决定了能看到什么、用什么探测器。
          </p>
          <BandsDiagram form={form} />
        </div>
      );
    case "fov":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            视场角决定单个画面能覆盖多大范围。在监控和巡检场景中，需要权衡覆盖范围与目标分辨率。
          </p>
          <FOVDiagram form={form} />
        </div>
      );
    case "resolution":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            空间分辨率与像元尺寸、传感器尺寸、视场角和工作距离有关。像元越小、视场越窄，分辨率越高。
          </p>
          <ResolutionDiagram form={form} />
        </div>
      );
    case "sensitivity":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            热灵敏度 NETD 表示系统能分辨的最小温度差。对于热成像应用，NETD 是关键指标。
          </p>
          <SensitivityDiagram form={form} />
        </div>
      );
    default:
      return null;
  }
}

const QUIZ_QUESTIONS = [
  {
    question: "红外成像中，LWIR 波段通常用于检测什么类型的目标？",
    options: ["高温火焰", "常温人体/热目标", "硅片内部缺陷", "短距离光纤通信"],
    correctIndex: 1,
    explanation: "LWIR（长波红外，8–14 μm）主要用于常温目标热成像，如人体、建筑热损耗检测。",
  },
  {
    question: "IFOV（瞬时视场角）越小，通常意味着什么？",
    options: ["覆盖范围越广", "空间分辨率越高", "热灵敏度越好", "帧率越高"],
    correctIndex: 1,
    explanation: "IFOV 越小，单个像素对应的地物尺寸越小，空间分辨率越高，适合远距离小目标检测。",
  },
  {
    question: "NETD 是衡量红外系统哪方面性能的指标？",
    options: ["空间分辨率", "热灵敏度", "帧率", "波段范围"],
    correctIndex: 1,
    explanation: "NETD（噪声等效温差）表示系统能分辨的最小温度差，值越小热灵敏度越好。",
  },
  {
    question: "红外镜头与普通可见光镜头的主要区别是什么？",
    options: ["焦距更长", "需要针对红外波段镀膜", "光圈更大", "重量更轻"],
    correctIndex: 1,
    explanation: "红外镜头需要在特定波段具有高透过率，因此镀膜和玻璃材料都与可见光镜头不同。",
  },
];

function QuizContent({ onComplete }: { onComplete: (score: number) => void }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
        完成以下小测验，检验你对红外成像核心概念的理解。
      </p>
      <LearningQuiz title="红外成像知识测验" questions={QUIZ_QUESTIONS} quizId="infrared-quiz" onComplete={onComplete} />
    </div>
  );
}

export default function InfraredLearningHub({ form }: Props) {
  const [activeSection, setActiveSection] = useState<SectionId>("overview");
  const { getDomainProgress, markSectionViewed, markQuizCompleted } = useLearningProgress();
  const progress = getDomainProgress("infrared");

  useEffect(() => {
    if (activeSection !== "quiz") {
      markSectionViewed("infrared", activeSection);
    }
  }, [activeSection, markSectionViewed]);

  const currentSection = useMemo(() => SECTIONS.find((s) => s.id === activeSection), [activeSection]);

  const totalSections = SECTIONS.length;
  const viewedCount = SECTIONS.filter((s) => progress.sectionsViewed.includes(s.id)).length;
  const quizCompleted = progress.quizzesCompleted.includes("infrared-quiz");
  const progressValue = Math.round(((viewedCount + (quizCompleted ? 1 : 0)) / (totalSections + 1)) * 100);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen size={16} className="text-indigo-500" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">红外成像学习指南</h3>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between text-[10px] text-slate-500 dark:text-slate-400 mb-1">
          <span>学习进度</span>
          <span>{progressValue}%</span>
        </div>
        <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 transition-all"
            style={{ width: `${progressValue}%` }}
          />
        </div>
      </div>

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
        <button
          onClick={() => setActiveSection("quiz")}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            activeSection === "quiz"
              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800/30"
              : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
          }`}
        >
          <HelpCircle size={14} />
          测验
          {quizCompleted && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />}
        </button>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto pr-1">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 shadow-sm space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-700">
            {currentSection ? (
              <>
                <span className="text-indigo-500">{currentSection.icon}</span>
                <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100">{currentSection.title}</h4>
              </>
            ) : (
              <>
                <span className="text-emerald-500"><HelpCircle size={14} /></span>
                <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100">知识测验</h4>
              </>
            )}
          </div>
          {activeSection === "quiz" ? (
            <QuizContent onComplete={(score) => markQuizCompleted("infrared", "infrared-quiz", score)} />
          ) : (
            <SectionContent section={activeSection} form={form} />
          )}
        </div>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed flex items-start gap-2">
          <Ruler size={14} className="shrink-0 mt-0.5" />
          提示：修改左侧表单中的波段、视场角、工作距离、像元尺寸，上方图表与指标会实时更新。
        </p>
      </div>
    </div>
  );
}
