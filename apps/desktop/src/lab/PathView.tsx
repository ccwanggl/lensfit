import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { conceptLink, obsidianUrlFor } from "./knowledgeLinks";
import { useReportProgress } from "./reportProgress";
import {
  BookOpen,
  Briefcase,
  CheckCircle2,
  FlaskConical,
  GraduationCap,
  LayoutGrid,
  Loader2,
  Lock,
  Milestone,
  X,
} from "lucide-react";
import {
  getCurriculumGraph,
  type CurriculumNode,
  type CurriculumNodeKind,
} from "../utils/api";
import { useLabStore } from "../stores/labStore";
import { useAppStore, type AppTabId } from "../stores/appStore";
import QuizPanel from "./QuizPanel";

/* ─── Lock logic (exported for tests) ─── */

export interface LockInfo {
  locked: boolean;
  /** Titles of the direct prerequisites that are not completed yet. */
  missing: string[];
}

/**
 * A node is unlocked when all its direct prerequisites are completed.
 * Transitive blocking surfaces naturally: an incomplete prerequisite is
 * listed as missing, and that prerequisite shows its own missing list.
 */
export function computeLocks(
  nodes: CurriculumNode[],
  completed: ReadonlySet<string>
): Map<string, LockInfo> {
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const locks = new Map<string, LockInfo>();
  for (const node of nodes) {
    const missing = node.prerequisites
      .filter((id) => !completed.has(id))
      .map((id) => byId.get(id)?.title ?? id);
    locks.set(node.id, { locked: missing.length > 0, missing });
  }
  return locks;
}

/* ─── Layering ─── */

const MODULE_ORDER = [
  "10-foundations",
  "20-geometric-optics",
  "30-wave-optics",
  "40-spectroscopy",
  "50-optical-design",
  "practice",
];

const MODULE_LABELS: Record<string, string> = {
  "10-foundations": "光学基础",
  "20-geometric-optics": "几何光学",
  "30-wave-optics": "波动光学",
  "40-spectroscopy": "光谱学",
  "50-optical-design": "光学设计",
  practice: "实践场",
};

const KIND_META: Record<CurriculumNodeKind, { label: string; icon: React.ReactNode }> = {
  concept: { label: "概念", icon: <BookOpen size={13} /> },
  experiment: { label: "实验", icon: <FlaskConical size={13} /> },
  preset: { label: "面包板", icon: <LayoutGrid size={13} /> },
  practice: { label: "实践", icon: <Briefcase size={13} /> },
  assessment: { label: "测验", icon: <GraduationCap size={13} /> },
};

export default function PathView() {
  const activeQuizId = useLabStore((s) => s.activeQuizId);
  const setActiveQuizId = useLabStore((s) => s.setActiveQuizId);
  const { data, isLoading, error } = useQuery({
    queryKey: ["curriculum-graph"],
    queryFn: getCurriculumGraph,
  });

  const layers = useMemo(() => {
    const nodes = data?.nodes ?? [];
    const groups = new Map<string, CurriculumNode[]>();
    for (const node of nodes) {
      const list = groups.get(node.module) ?? [];
      list.push(node);
      groups.set(node.module, list);
    }
    return MODULE_ORDER.filter((m) => groups.has(m)).map((m) => ({
      module: m,
      nodes: groups.get(m)!,
    }));
  }, [data]);

  // 完成集合来自 curriculum graph 合并的真实学习者状态
  // （GET /api/v1/curriculum/graph 的节点 status，由 learning_records 合并）。
  // 锁定逻辑（computeLocks）与阶段 1 相同，只换了数据源。
  const completed = useMemo(
    () =>
      new Set(
        (data?.nodes ?? [])
          .filter((n) => n.status === "completed")
          .map((n) => n.id)
      ),
    [data]
  );
  const locks = useMemo(
    () => computeLocks(data?.nodes ?? [], completed),
    [data, completed]
  );

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-indigo-500" size={32} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
        加载学习路径失败：{error.message}
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto rounded-[14px] border border-slate-200/60 bg-white/80 p-4 shadow-sm dark:border-slate-700/60 dark:bg-slate-800/80">
      <div className="mb-3 flex items-center gap-2">
        <Milestone size={18} className="text-indigo-500" />
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">学习路径</h2>
        <span className="text-xs text-slate-400">完成先修节点后解锁后续内容</span>
      </div>

      {/* 测验面板：点击 assessment 节点后在路径视图内打开 */}
      {activeQuizId && (
        <div className="mb-4">
          <div className="mb-2 flex justify-end">
            <button
              onClick={() => setActiveQuizId(null)}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-500 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700"
              aria-label="关闭测验"
            >
              <X size={12} />
              关闭测验
            </button>
          </div>
          <QuizPanel quizId={activeQuizId} />
        </div>
      )}

      <div className="space-y-4">
        {layers.map(({ module, nodes }) => (
          <section key={module}>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              {MODULE_LABELS[module] ?? module}
              {module !== "practice" && (
                <span className="ml-1 font-normal normal-case text-slate-400">{module}</span>
              )}
            </h3>
            <ol className="space-y-1.5">
              {nodes.map((node) => (
                <PathNodeRow key={node.id} node={node} lock={locks.get(node.id)} />
              ))}
            </ol>
          </section>
        ))}
      </div>
    </div>
  );
}

function PathNodeRow({
  node,
  lock,
}: {
  node: CurriculumNode;
  lock?: LockInfo;
}) {
  const openExperimentFromTutorial = useLabStore((s) => s.openExperimentFromTutorial);
  const openConceptFromPath = useLabStore((s) => s.openConceptFromPath);
  const setActiveQuizId = useLabStore((s) => s.setActiveQuizId);
  const setActiveTab = useAppStore((s) => s.setActiveTab);
  const reportProgress = useReportProgress();

  const locked = (lock?.locked ?? false) && node.status !== "completed";
  const isCompleted = node.status === "completed";
  const kind = KIND_META[node.kind];

  const handleClick = () => {
    if (locked) return;
    if (node.kind === "assessment") {
      // 测验在路径视图内打开，不切换视图
      setActiveQuizId(node.ref);
      return;
    }
    setActiveQuizId(null);
    if (node.kind === "concept") {
      const entry = conceptLink(node.ref);
      if (entry) {
        reportProgress("concept", node.ref, "viewed");
        window.open(obsidianUrlFor(entry, node.ref), "_blank", "noreferrer");
      } else {
        openConceptFromPath(node.ref);
      }
    } else if (node.kind === "practice") {
      setActiveTab(node.ref as AppTabId);
    } else {
      // experiment / preset 都在学习中心沙盘打开
      openExperimentFromTutorial(node.ref);
    }
  };

  return (
    <li>
      <button
        onClick={handleClick}
        disabled={locked}
        title={locked ? `需要先完成：${lock!.missing.join("、")}` : node.title}
        className={`flex w-full items-center gap-3 rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
          locked
            ? "cursor-not-allowed border-slate-200 bg-slate-50 text-slate-400 dark:border-slate-700 dark:bg-slate-900/50 dark:text-slate-500"
            : isCompleted
              ? "border-emerald-200 bg-emerald-50/60 text-slate-700 hover:border-emerald-300 dark:border-emerald-800/40 dark:bg-emerald-900/20 dark:text-slate-300"
              : "border-slate-200 bg-white text-slate-700 hover:border-indigo-200 hover:bg-indigo-50/50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-indigo-800/40 dark:hover:bg-indigo-900/20"
        }`}
      >
        <span
          className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
            locked
              ? "bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500"
              : isCompleted
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400"
                : "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400"
          }`}
        >
          {kind.icon}
          {kind.label}
        </span>
        <span className="min-w-0 flex-1 truncate font-medium">{node.title}</span>
        {isCompleted && (
          <CheckCircle2 size={16} className="shrink-0 text-emerald-500" aria-label="已完成" />
        )}
        {locked && (
          <span className="flex shrink-0 items-center gap-1 text-xs text-slate-400 dark:text-slate-500">
            <Lock size={12} />
            需先完成：{lock!.missing.join("、")}
          </span>
        )}
      </button>
    </li>
  );
}
