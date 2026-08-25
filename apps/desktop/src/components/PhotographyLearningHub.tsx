import { useState, useMemo, useEffect } from "react";
import { BookOpen, Lightbulb, Aperture, Camera, Eye, Ruler, Focus, HelpCircle } from "lucide-react";
import LearningQuiz from "./LearningQuiz";
import { useLearningProgress } from "../hooks/useLearningProgress";

interface Props {
  form: Record<string, unknown>;
}

type SectionId = "overview" | "focal" | "aperture" | "sensor" | "bokeh" | "quiz";

interface Section {
  id: SectionId;
  title: string;
  icon: React.ReactNode;
}

const SECTIONS: Section[] = [
  { id: "overview", title: "摄影系统概览", icon: <BookOpen size={14} /> },
  { id: "focal", title: "焦距与视角", icon: <Focus size={14} /> },
  { id: "aperture", title: "光圈与曝光", icon: <Aperture size={14} /> },
  { id: "sensor", title: "画幅的影响", icon: <Camera size={14} /> },
  { id: "bokeh", title: "景深与虚化", icon: <Eye size={14} /> },
];

function readStr(form: Record<string, unknown>, key: string, fallback = ""): string {
  const v = form[key];
  return typeof v === "string" ? v : fallback;
}

function getFocalFromRange(range: string): number {
  const map: Record<string, number> = {
    "wide": 24,
    "standard": 50,
    "portrait": 85,
    "tele": 135,
    "macro": 90,
    "ultra-wide": 16,
  };
  return map[range] ?? 50;
}

/** ─── Focal length & angle of view diagram ─── */
function FocalDiagram({ form }: { form: Record<string, unknown> }) {
  const focalRange = readStr(form, "focal_range", "standard");
  const focal = getFocalFromRange(focalRange);
  const sensor = 36; // full-frame width as reference
  const afov = (360 / Math.PI) * Math.atan(sensor / (2 * focal));

  const W = 320;
  const CX = 160;
  const CY = 120;
  const len = 100;
  const halfAngle = (afov * Math.PI) / 360;
  const x1 = CX - len * Math.sin(halfAngle);
  const x2 = CX + len * Math.sin(halfAngle);
  const y = CY - len * Math.cos(halfAngle);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox={`0 0 ${W} 180`} className="w-full max-w-xs h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Camera */}
          <rect x={CX - 12} y={CY - 8} width={24} height={16} fill="#475569" rx={2} />
          {/* View rays */}
          <line x1={CX} y1={CY} x2={x1} y2={y} stroke="#6366f1" strokeWidth={1.5} />
          <line x1={CX} y1={CY} x2={x2} y2={y} stroke="#6366f1" strokeWidth={1.5} />
          {/* Scene arc */}
          <path d={`M ${x1} ${y} Q ${CX} ${y - 20} ${x2} ${y}`} fill="rgba(99,102,241,0.1)" stroke="#6366f1" strokeWidth={1} />
          {/* Labels */}
          <text x={CX} y={CY + 32} textAnchor="middle" className="text-[10px] fill-slate-500">f = {focal} mm</text>
          <text x={CX} y={y - 8} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">视角 ≈ {afov.toFixed(1)}°</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        焦距越短，视角越宽，适合风景、建筑；焦距越长，视角越窄、压缩感越强，适合人像、体育。
      </p>
    </div>
  );
}

/** ─── Aperture diagram ─── */
function ApertureDiagram({ form }: { form: Record<string, unknown> }) {
  const aperture = readStr(form, "max_aperture", "2.8");
  const f = parseFloat(aperture) || 2.8;
  const diam = Math.max(10, 60 / f);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 160 160" className="w-40 h-40 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          <circle cx={80} cy={80} r={38} fill="none" stroke="#475569" strokeWidth={3} />
          <circle cx={80} cy={80} r={diam / 2} fill="rgba(99,102,241,0.2)" stroke="#6366f1" strokeWidth={2} />
          <text x={80} y={84} textAnchor="middle" className="text-xs font-bold fill-indigo-700 dark:fill-indigo-400">f/{f}</text>
        </svg>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-300">
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-xs text-slate-500">进光量</span>
          <span className="font-semibold">{f <= 2.8 ? "多" : f <= 5.6 ? "中等" : "少"}</span>
        </div>
        <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <span className="block text-xs text-slate-500">背景虚化</span>
          <span className="font-semibold">{f <= 2.8 ? "强" : f <= 5.6 ? "中等" : "弱"}</span>
        </div>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        光圈值 f/N 中，N 越小光圈越大。大光圈进光多、虚化强，但景深更浅；小光圈景深大，适合风光。
      </p>
    </div>
  );
}

/** ─── Sensor format diagram ─── */
function SensorDiagram({ form }: { form: Record<string, unknown> }) {
  const fmt = readStr(form, "format", "FF");
  const sizes: Record<string, { w: number; h: number; label: string }> = {
    "FF": { w: 36, h: 24, label: "全画幅 36×24 mm" },
    "APS-C": { w: 23.5, h: 15.6, label: "APS-C 约 23.5×15.6 mm" },
    "M43": { w: 17.3, h: 13, label: "M43 17.3×13 mm" },
  };
  const s = sizes[fmt] ?? sizes["FF"];
  const scale = 4;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 200 160" className="w-full max-w-xs h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Full frame reference */}
          <rect x={20} y={30} width={36 * scale} height={24 * scale} fill="rgba(203,213,225,0.2)" stroke="#94a3b8" strokeWidth={1} />
          <text x={20} y={24} className="text-[9px] fill-slate-400">全画幅参考</text>
          {/* Selected format */}
          <rect x={20} y={30} width={s.w * scale} height={s.h * scale} fill="rgba(99,102,241,0.2)" stroke="#6366f1" strokeWidth={2} />
          <text x={20 + s.w * scale / 2} y={30 + s.h * scale / 2 + 3} textAnchor="middle" className="text-[9px] fill-indigo-700 dark:fill-indigo-400">{s.label}</text>
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        画幅越大，同样焦距下视角越广、景深越浅、高感越好；画幅越小，便携性更好，但等效焦距会“变长”。
      </p>
    </div>
  );
}

/** ─── Depth of field / bokeh diagram ─── */
function BokehDiagram({ form }: { form: Record<string, unknown> }) {
  const aperture = readStr(form, "max_aperture", "2.8");
  const f = parseFloat(aperture) || 2.8;
  const focalRange = readStr(form, "focal_range", "standard");
  const focal = getFocalFromRange(focalRange);

  const dofWidth = Math.max(40, 200 / f + 1000 / focal);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center">
        <svg viewBox="0 0 320 120" className="w-full max-w-sm h-auto rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
          {/* Axis */}
          <line x1={20} y1={60} x2={300} y2={60} stroke="#cbd5e1" strokeWidth={1} />
          {/* Focus plane */}
          <line x1={160} y1={30} x2={160} y2={90} stroke="#6366f1" strokeWidth={2} strokeDasharray="4 2" />
          <text x={160} y={105} textAnchor="middle" className="text-[10px] fill-indigo-600 dark:fill-indigo-400">对焦面</text>
          {/* DOF range */}
          <rect x={160 - dofWidth / 2} y={45} width={dofWidth} height={30} fill="rgba(16,185,129,0.15)" stroke="#10b981" strokeWidth={1} rx={4} />
          <text x={160} y={64} textAnchor="middle" className="text-[10px] fill-emerald-700 dark:fill-emerald-400">清晰范围</text>
          {/* Bokeh circles */}
          <circle cx={80} cy={60} r={80 / f} fill="rgba(99,102,241,0.15)" />
          <circle cx={240} cy={60} r={80 / f} fill="rgba(99,102,241,0.15)" />
        </svg>
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/40 p-3 rounded-lg border border-slate-100 dark:border-slate-700/60">
        光圈越大、焦距越长、对焦距离越近，景深越浅，背景越容易虚化。人像摄影常用大光圈长焦来突出主体。
      </p>
    </div>
  );
}

function SectionContent({ section, form }: { section: SectionId; form: Record<string, unknown> }) {
  switch (section) {
    case "overview":
      return (
        <div className="space-y-3 text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
          <p>
            摄影系统的核心是让相机在特定场景下拍出符合创作意图的照片。关键选择包括<strong>机身画幅</strong>、<strong>镜头焦距</strong>、<strong>最大光圈</strong>和<strong>卡口系统</strong>。
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { title: "画幅", desc: "决定视角、景深和高感表现，也影响整套系统的体积和重量。" },
              { title: "焦距", desc: "决定取景范围和透视关系。短焦宽广，长焦压缩。" },
              { title: "光圈", desc: "控制进光量和景深。大光圈虚化强，小光圈清晰范围大。" },
              { title: "卡口", desc: "决定可用的镜头群。不同品牌卡口互不兼容。" },
            ].map((item) => (
              <div key={item.title} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/60">
                <p className="font-semibold text-slate-800 dark:text-slate-100 mb-1">{item.title}</p>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/15 border border-amber-100 dark:border-amber-800/20 text-xs text-amber-800 dark:text-amber-300">
            <Lightbulb size={14} className="shrink-0 mt-0.5" />
            <p>不同拍摄用途对参数优先级不同：人像偏重虚化，风景偏重广角和景深，体育偏重长焦和对焦速度。</p>
          </div>
        </div>
      );
    case "focal":
      return (
        <div className="space-y-3">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            焦距是镜头光学中心到成像面的距离。它直接决定视角和透视感。
          </p>
          <FocalDiagram form={form} />
        </div>
      );
    case "aperture":
      return (
        <div className="space-y-3">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            光圈是镜头中允许光线通过的孔径。f 值越小，孔径越大。
          </p>
          <ApertureDiagram form={form} />
        </div>
      );
    case "sensor":
      return (
        <div className="space-y-3">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            画幅是传感器物理尺寸。它影响视角、景深和机身体积。
          </p>
          <SensorDiagram form={form} />
        </div>
      );
    case "bokeh":
      return (
        <div className="space-y-3">
          <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            景深是照片中看起来清晰的纵深范围。光圈、焦距和对焦距离共同决定景深。
          </p>
          <BokehDiagram form={form} />
        </div>
      );
    default:
      return null;
  }
}

const QUIZ_QUESTIONS = [
  {
    question: "在传感器尺寸相同的情况下，焦距越短，视角会怎么变化？",
    options: ["视角越窄", "视角越宽", "视角不变", "景深越浅"],
    correctIndex: 1,
    explanation: "焦距与视角成反比：焦距越短，视角越宽，适合拍摄风景、建筑等大场景。",
  },
  {
    question: "光圈值 f/1.4 与 f/5.6 相比，哪个光圈孔径更大、进光更多？",
    options: ["f/1.4", "f/5.6", "一样大", "取决于焦距"],
    correctIndex: 0,
    explanation: "f 值越小，光圈孔径越大，进光量越多，背景虚化也越强。",
  },
  {
    question: "全画幅相机相比 APS-C 相机，在相同焦距下通常有什么特点？",
    options: ["视角更窄", "景深更浅、高感更好", "体积更小", "像素一定更多"],
    correctIndex: 1,
    explanation: "画幅越大，同样焦距下视角越广、景深越浅，且单个像素面积通常更大，高感表现更好。",
  },
  {
    question: "以下哪种组合最容易获得浅景深、背景虚化效果？",
    options: ["广角 + 小光圈 + 远距离", "长焦 + 大光圈 + 近距离", "短焦 + 小光圈 + 远距离", "标准镜头 + 中等光圈"],
    correctIndex: 1,
    explanation: "长焦、大光圈、近距离对焦都会让景深变浅，从而增强背景虚化。",
  },
];

function QuizContent({ onComplete }: { onComplete: (score: number) => void }) {
  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
        完成以下小测验，检验你对摄影系统核心概念的理解。
      </p>
      <LearningQuiz title="摄影知识测验" questions={QUIZ_QUESTIONS} quizId="photography-quiz" onComplete={onComplete} />
    </div>
  );
}

export default function PhotographyLearningHub({ form }: Props) {
  const [activeSection, setActiveSection] = useState<SectionId>("overview");
  const { getDomainProgress, markSectionViewed, markQuizCompleted } = useLearningProgress();
  const progress = getDomainProgress("photography");

  useEffect(() => {
    if (activeSection !== "quiz") {
      markSectionViewed("photography", activeSection);
    }
  }, [activeSection, markSectionViewed]);

  const currentSection = useMemo(() => SECTIONS.find((s) => s.id === activeSection), [activeSection]);

  const totalSections = SECTIONS.length;
  const viewedCount = SECTIONS.filter((s) => progress.sectionsViewed.includes(s.id)).length;
  const quizCompleted = progress.quizzesCompleted.includes("photography-quiz");
  const progressValue = Math.round(((viewedCount + (quizCompleted ? 1 : 0)) / (totalSections + 1)) * 100);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen size={16} className="text-indigo-500" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">摄影学习指南</h3>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
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

      <div className="flex flex-wrap gap-1.5 mb-3">
        {SECTIONS.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
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
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
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
        <div className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 shadow-sm space-y-3">
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
            <QuizContent onComplete={(score) => markQuizCompleted("photography", "photography-quiz", score)} />
          ) : (
            <SectionContent section={activeSection} form={form} />
          )}
        </div>
      </div>

      <div className="mt-4 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60">
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed flex items-start gap-2">
          <Ruler size={14} className="shrink-0 mt-0.5" />
          提示：修改左侧表单中的画幅、焦距范围、最大光圈等参数，上方图表会同步变化，帮助你理解它们对画面的影响。
        </p>
      </div>
    </div>
  );
}
