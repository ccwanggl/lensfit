import { useState, useMemo, useEffect } from "react";
import { BookOpen, Lightbulb, Microscope, Focus, Eye, Waves, Ruler, HelpCircle } from "lucide-react";
import LearningQuiz from "./LearningQuiz";
import { useLearningProgress } from "../hooks/useLearningProgress";

interface Props {
  form: Record<string, unknown>;
}

type SectionId = "overview" | "na" | "resolution" | "magnification" | "sampling" | "quiz";

interface Section {
  id: SectionId;
  title: string;
  icon: React.ReactNode;
}

const SECTIONS: Section[] = [
  { id: "overview", title: "显微系统概览", icon: <BookOpen size={14} /> },
  { id: "na", title: "数值孔径 NA", icon: <Focus size={14} /> },
  { id: "resolution", title: "分辨率极限", icon: <Eye size={14} /> },
  { id: "magnification", title: "放大倍率", icon: <Microscope size={14} /> },
  { id: "sampling", title: "奈奎斯特采样", icon: <Waves size={14} /> },
];

function readNum(form: Record<string, unknown>, key: string, fallback = 0): number {
  const v = form[key];
  return typeof v === "number" ? v : fallback;
}

/** ─── NA cone diagram ─── */
function NADiagram({ form }: { form: Record<string, unknown> }) {
  const na = readNum(form, "objective_na", 0.65);
  const theta = Math.asin(Math.min(na, 0.99));

  const CX = 120;
  const CY = 140;
  const len = 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 240 160" className="w-full max-w-xs h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Sample plane */}
          <line x1={20} y1={CY} x2={220} y2={CY} stroke="#475569" strokeWidth={2} />
          <text x={120} y={CY + 20} textAnchor="middle" className="text-[10px] fill-slate-500">样品面</text>
          {/* Cone */}
          <path d={`M ${CX} ${CY} L ${CX - len * Math.sin(theta)} ${CY - len * Math.cos(theta)} A ${len} ${len} 0 0 1 ${CX + len * Math.sin(theta)} ${CY - len * Math.cos(theta)} Z`} fill="rgba(99,102,241,0.15)" stroke="#6366f1" strokeWidth={1.5} />
          {/* Angle arc */}
          <path d={`M ${CX} ${CY - 30} A 30 30 0 0 1 ${CX + 30 * Math.sin(theta)} ${CY - 30 * Math.cos(theta)}`} fill="none" stroke="#f59e0b" strokeWidth={1.5} />
          <text x={CX + 40} y={CY - 20} className="text-[10px] fill-amber-600 dark:fill-amber-400">θ</text>
          {/* NA label */}
          <text x={CX} y={CY - len - 10} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">NA = sin(θ) = {na.toFixed(2)}</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        数值孔径 NA = n·sin(θ)。NA 越大，物镜收集光线的锥角越大，分辨率越高，但景深也越浅。
      </p>
    </div>
  );
}

/** ─── Resolution limit diagram ─── */
function ResolutionDiagram({ form }: { form: Record<string, unknown> }) {
  const na = readNum(form, "objective_na", 0.65);
  const wavelength = readNum(form, "wavelength_nm", 550);
  const d = 0.61 * wavelength / (na * 1000); // in μm

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">波长</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{wavelength.toFixed(0)} nm</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">分辨率极限</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{d.toFixed(2)} μm</span>
        </div>
      </div>
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 280 120" className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Two adjacent dots representing resolvable detail */}
          <circle cx={120} cy={60} r={Math.max(2, d * 3)} fill="#6366f1" opacity={0.7} />
          <circle cx={180} cy={60} r={Math.max(2, d * 3)} fill="#6366f1" opacity={0.7} />
          <text x={150} y={95} textAnchor="middle" className="text-[10px] fill-slate-500">刚好可分辨的两点</text>
          <line x1={120} y1={60} x2={180} y2={60} stroke="#f59e0b" strokeWidth={1} strokeDasharray="2 2" />
          <text x={150} y={35} textAnchor="middle" className="text-[10px] fill-amber-600 dark:fill-amber-400">d = 0.61λ/NA</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        瑞利判据：两点间距小于 d 时无法区分。提高 NA 或使用更短波长（如蓝光/紫外）可提高分辨率。
      </p>
    </div>
  );
}

/** ─── Magnification diagram ─── */
function MagnificationDiagram({ form }: { form: Record<string, unknown> }) {
  const mag = readNum(form, "magnification", 20);
  const pixel = readNum(form, "pixel_size_um", 3.45);
  const pxAcc = pixel / (1000 * mag);

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">总放大倍率</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{mag.toFixed(0)}×</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">像素精度</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{pxAcc.toFixed(4)} mm/px</span>
        </div>
      </div>
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 320 120" className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Object */}
          <rect x={30} y={45} width={40} height={30} fill="rgba(16,185,129,0.2)" stroke="#10b981" strokeWidth={1.5} />
          <text x={50} y={95} textAnchor="middle" className="text-[10px] fill-emerald-600 dark:fill-emerald-400">实物</text>
          {/* Arrow */}
          <path d="M 80 60 L 130 60" stroke="#94a3b8" strokeWidth={1.5} markerEnd="url(#arrow)" />
          <text x={105} y={52} textAnchor="middle" className="text-[10px] fill-slate-500">β = {mag}×</text>
          {/* Image */}
          <rect x={150} y={30} width={40 * mag / 10} height={60} fill="rgba(99,102,241,0.2)" stroke="#6366f1" strokeWidth={1.5} />
          <text x={150 + 20 * mag / 10} y={105} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">像</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        显微镜总放大倍率由物镜和传感器共同决定。倍率越大，细节越大，但视野越小、景深越浅。
      </p>
    </div>
  );
}

/** ─── Nyquist sampling diagram ─── */
function SamplingDiagram({ form }: { form: Record<string, unknown> }) {
  const pixel = readNum(form, "pixel_size_um", 3.45);
  const na = readNum(form, "objective_na", 0.65);
  const wavelength = readNum(form, "wavelength_nm", 550);

  const fn = 1000 / (2 * pixel);
  const opticalLimit = 1000 * na / (0.61 * wavelength);
  const ratio = opticalLimit / fn;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">传感器奈奎斯特</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{fn.toFixed(1)} lp/mm</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">光学分辨率</span>
          <span className="font-mono font-semibold text-indigo-700 dark:text-indigo-400">{opticalLimit.toFixed(1)} lp/mm</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-[10px] text-slate-500">过采样比</span>
          <span className={`font-mono font-semibold ${ratio >= 1 ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"}`}>{ratio.toFixed(2)}×</span>
        </div>
      </div>
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 300 120" className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Fine signal */}
          {Array.from({ length: 40 }).map((_, i) => (
            <rect key={i} x={20 + i * 6} y={35 + (i % 2) * 15} width={3} height={3} fill="#6366f1" opacity={0.6} />
          ))}
          <text x={150} y={28} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">光学细节</text>
          {/* Pixel grid */}
          {Array.from({ length: 12 }).map((_, i) => (
            <rect key={i} x={20 + i * 22} y={75} width={18} height={18} fill="none" stroke="#10b981" strokeWidth={1} />
          ))}
          <text x={150} y={110} textAnchor="middle" className="text-[10px] fill-emerald-600 dark:fill-emerald-400">像素采样</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        光学分辨率应高于传感器奈奎斯特频率的一半，否则会出现混叠。通常建议过采样比 ≥ 1。
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
            显微成像系统由<strong>光源</strong>、<strong>样品台</strong>、<strong>物镜</strong>、<strong>镜筒/相机适配器</strong>和<strong>相机</strong>组成。核心是物镜的数值孔径和相机的像素匹配。
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { title: "物镜 NA", desc: "决定分辨率和进光量，是显微镜最重要的参数。" },
              { title: "放大倍率", desc: "由物镜标称倍率、镜筒倍率和相机传感器尺寸共同决定。" },
              { title: "照明波长", desc: "波长越短，衍射极限分辨率越高。" },
              { title: "相机像素", desc: "像素必须足够小，以匹配光学系统的分辨率。" },
            ].map((item) => (
              <div key={item.title} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
                <p className="font-semibold text-slate-800 dark:text-slate-100 mb-1">{item.title}</p>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/15 border border-amber-100 dark:border-amber-800/20 text-xs text-amber-800 dark:text-amber-300">
            <Lightbulb size={14} className="shrink-0 mt-0.5" />
            <p>显微镜选型的关键是匹配：物镜 NA 决定光学分辨率，相机像素必须足够小以记录这些细节，否则高 NA 的优势会被浪费。</p>
          </div>
        </div>
      );
    case "na":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            数值孔径 NA 衡量物镜收集光线的能力。NA 越大，分辨率越高，但工作距离通常越短、景深越浅。
          </p>
          <NADiagram form={form} />
        </div>
      );
    case "resolution":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            瑞利判据给出显微镜能分辨的最小间距：d = 0.61λ/NA。
          </p>
          <ResolutionDiagram form={form} />
        </div>
      );
    case "magnification":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            放大倍率 β = 像高/物高。它决定物体在传感器上成像的大小，也影响每个像素对应的物理尺寸。
          </p>
          <MagnificationDiagram form={form} />
        </div>
      );
    case "sampling":
      return (
        <div className="space-y-4">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            根据奈奎斯特-香农采样定理，相机的像素尺寸必须足够小，使得其奈奎斯特频率高于光学系统的分辨率极限。
          </p>
          <SamplingDiagram form={form} />
        </div>
      );
    default:
      return null;
  }
}

const QUIZ_QUESTIONS = [
  {
    question: "数值孔径 NA 主要影响显微镜的哪项性能？",
    options: ["色彩还原", "分辨率和集光能力", "存储容量", "机械稳定性"],
    correctIndex: 1,
    explanation: "NA = n·sin(θ)，它决定物镜收集光线的锥角，从而影响分辨率和亮度。NA 越大，分辨率越高。",
  },
  {
    question: "根据瑞利判据，提高分辨率最有效的方法是？",
    options: ["增加放大倍率", "增大 NA 或缩短波长", "使用更大传感器", "提高 ISO"],
    correctIndex: 1,
    explanation: "瑞利判据 d = 0.61λ/NA。增大 NA 或使用更短波长（如蓝光/紫外）可以缩小可分辨间距。",
  },
  {
    question: "奈奎斯特采样定理要求传感器采样频率至少为光学信号最高频率的多少倍？",
    options: ["0.5 倍", "1 倍", "2 倍", "4 倍"],
    correctIndex: 2,
    explanation: "为避免混叠，采样频率必须至少是信号最高频率的 2 倍，即过采样比通常建议 ≥ 1。",
  },
  {
    question: "在显微镜中，放大倍率越大，以下哪项通常会变小？",
    options: ["景深和视野", "数值孔径", "工作距离和分辨率", "进光量"],
    correctIndex: 0,
    explanation: "放大倍率越大，视野越小，景深也越浅，但能观察到的细节更大。",
  },
];

function QuizContent({ onComplete }: { onComplete: (score: number) => void }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
        完成以下小测验，检验你对显微成像核心概念的理解。
      </p>
      <LearningQuiz title="显微镜知识测验" questions={QUIZ_QUESTIONS} quizId="microscope-quiz" onComplete={onComplete} />
    </div>
  );
}

export default function MicroscopeLearningHub({ form }: Props) {
  const [activeSection, setActiveSection] = useState<SectionId>("overview");
  const { getDomainProgress, markSectionViewed, markQuizCompleted } = useLearningProgress();
  const progress = getDomainProgress("microscope");

  useEffect(() => {
    if (activeSection !== "quiz") {
      markSectionViewed("microscope", activeSection);
    }
  }, [activeSection, markSectionViewed]);

  const currentSection = useMemo(() => SECTIONS.find((s) => s.id === activeSection), [activeSection]);

  const totalSections = SECTIONS.length;
  const viewedCount = SECTIONS.filter((s) => progress.sectionsViewed.includes(s.id)).length;
  const quizCompleted = progress.quizzesCompleted.includes("microscope-quiz");
  const progressValue = Math.round(((viewedCount + (quizCompleted ? 1 : 0)) / (totalSections + 1)) * 100);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen size={16} className="text-indigo-500" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">显微镜学习指南</h3>
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
            <QuizContent onComplete={(score) => markQuizCompleted("microscope", "microscope-quiz", score)} />
          ) : (
            <SectionContent section={activeSection} form={form} />
          )}
        </div>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed flex items-start gap-2">
          <Ruler size={14} className="shrink-0 mt-0.5" />
          提示：修改左侧表单中的 NA、放大倍率、波长、像元尺寸，上方图表与指标会实时更新。
        </p>
      </div>
    </div>
  );
}
