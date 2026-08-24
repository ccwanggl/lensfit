import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import {
  Monitor,
  Ruler,
  Maximize2,
  ArrowUpDown,
  Aperture,
  Plug,
  Search,
  FileText,
  Table2,
  CheckCircle2,
  AlertTriangle,
  Focus,
  ZoomIn,
  Crosshair,
  Activity,
  Eye,
  Layers,
  Image,
  Download,
  ArrowLeftRight,
  FolderPlus,
  BarChart3,
  Zap,
  ChevronUp,
  ChevronDown,
  BookOpen,
  GraduationCap,
} from "lucide-react";
import SensorCoveragePlot from "../components/SensorCoveragePlot";
import ScoreRadarChart from "../components/ScoreRadarChart";
import MatchExplanation from "../components/MatchExplanation";
import DomainForm from "../components/DomainForm";
import {
  Button,
  Badge,
  SectionHeader,
  EmptyState,
} from "../components/ui";
import { ResultCardSkeleton, CoverageSkeleton } from "../components/ui/Skeleton";
import { toast } from "../hooks/useToast";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import PhysicsTrace from "../components/PhysicsTrace";
import CompareView from "../components/CompareView";
import CompareParetoToolbar, { computeParetoFrontier } from "../components/CompareParetoToolbar";
import DiagnosticsPanel from "../components/DiagnosticsPanel";
import WhatIfPanel from "../components/WhatIfPanel";
import GlossaryTooltip from "../components/GlossaryTooltip";
import SaveToProjectDialog from "../components/SaveToProjectDialog";
import KnowledgePanel from "../components/KnowledgePanel";
import IndustrialLearningHub from "../components/IndustrialLearningHub";
import type { PresetConfigItem } from "../utils/api";
import {
  generateCoverage,
  exportReport,
  startMatchStream,
} from "../utils/api";
import { useDomainMatching } from "../stores/matchingStore";
import {
  DomainPageShell,
  DomainFormPanel,
  DomainResultsPanel,
  DomainDetailPanel,
} from "../components/domain";

/* ─── Icons map (lucide-react) ─── */
const Icons = {
  sensor: <Monitor size={16} />,
  pixel: <Ruler size={16} />,
  target: <Maximize2 size={16} />,
  distance: <ArrowUpDown size={16} />,
  lens: <Aperture size={16} />,
  plug: <Plug size={16} />,
  search: <Search size={16} />,
  download: <Download size={14} />,
  fileText: <FileText size={14} />,
  table: <Table2 size={14} />,
  check: <CheckCircle2 size={12} />,
  alert: <AlertTriangle size={12} />,
  focus: <Focus size={14} />,
  zoom: <ZoomIn size={14} />,
  crosshair: <Crosshair size={14} />,
  activity: <Activity size={14} />,
  eye: <Eye size={14} />,
  layers: <Layers size={14} />,
  image: <Image size={16} />,
};

/* ─── Score Rank Badge ─── */
function RankBadge({ rank }: { rank: number }) {
  const colors: Record<number, string> = {
    1: "bg-gradient-to-br from-amber-300 to-amber-500 text-white shadow-[0_2px_6px_rgba(245,158,11,0.4)]",
    2: "bg-gradient-to-br from-slate-300 to-slate-400 text-white shadow-[0_2px_6px_rgba(148,163,184,0.4)]",
    3: "bg-gradient-to-br from-orange-300 to-orange-400 text-white shadow-[0_2px_6px_rgba(251,146,60,0.4)]",
  };
  return (
    <span className={`flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-lg text-xs font-extrabold ${colors[rank] || "bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300"}`}>
      {rank}
    </span>
  );
}

/* ─── Result Card ─── */
function ResultCard({
  result,
  rank,
  isSelected,
  onClick,
  compareMode,
  isCompareSelected,
  onToggleCompare,
}: {
  result: UnifiedMatchResult;
  rank: number;
  isSelected: boolean;
  onClick: () => void;
  compareMode?: boolean;
  isCompareSelected?: boolean;
  onToggleCompare?: () => void;
}) {
  const scorePct = Math.min(result.score * 100, 100);
  const scoreColor = scorePct >= 80 ? "emerald" : scorePct >= 50 ? "amber" : "rose";

  const handleActivate = () => {
    if (compareMode) {
      onToggleCompare?.();
    } else {
      onClick();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleActivate}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handleActivate();
        }
      }}
      className={`
        group relative flex items-start gap-3 p-4 rounded-xl
        transition-all duration-200 ease-out
        ${isSelected && !compareMode
          ? "bg-indigo-50/70 dark:bg-indigo-900/30 border-2 border-indigo-300 dark:border-indigo-700 shadow-[0_2px_12px_rgba(99,102,241,0.12)]"
          : isCompareSelected
          ? "bg-indigo-50/50 dark:bg-indigo-900/20 border-2 border-indigo-200 dark:border-indigo-800 shadow-sm"
          : "bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 hover:border-indigo-200 hover:shadow-md hover:-translate-y-0.5"
        }
        ${compareMode ? "cursor-pointer" : "cursor-pointer"}
      `}
    >
      <div className={`absolute left-0 top-3 bottom-3 w-[3px] rounded-r-full transition-all duration-200 ${
        isSelected ? "bg-indigo-500" :
        scorePct >= 80 ? "bg-emerald-400 group-hover:bg-emerald-500" :
        scorePct >= 50 ? "bg-amber-400 group-hover:bg-amber-500" :
        "bg-rose-400 group-hover:bg-rose-500"
      }`} />

      <RankBadge rank={rank} />

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">{result.lens_model || `镜头 #${result.lens_id}`}</h4>
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">评分</span>
            <span className="text-base font-extrabold text-indigo-600 dark:text-indigo-400 tabular-nums">{result.score?.toFixed(2) || "-"}</span>
          </div>
        </div>

        <p className="text-xs text-slate-600 dark:text-slate-400 truncate mb-2.5">{result.detector_model || `探测器 #${result.detector_id}`}</p>

        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant={result.vignetting ? "warning" : "success"} size="sm">
            <span className="flex items-center gap-1">{result.vignetting ? Icons.alert : Icons.check} {result.vignetting ? "渐晕" : "无渐晕"}</span>
          </Badge>
          <Badge variant="neutral" size="sm">覆盖 {((result.coverage_ratio || 0) * 100).toFixed(0)}%</Badge>
        </div>

        {result.reason && (
          <p className={`mt-2 text-xs leading-relaxed ${
            result.reason.startsWith("✓") ? "text-emerald-600 dark:text-emerald-400" :
            result.reason.startsWith("⚠") ? "text-amber-600 dark:text-amber-400" :
            "text-slate-600 dark:text-slate-300"
          }`}>
            {result.reason}
          </p>
        )}

        {compareMode && (
          <div className="flex-shrink-0 flex items-center">
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              isCompareSelected
                ? "bg-indigo-500 border-indigo-500"
                : "border-slate-300 dark:border-slate-600 group-hover:border-indigo-300"
            }`}>
              {isCompareSelected && <CheckCircle2 size={12} className="text-white" />}
            </div>
          </div>
        )}

        <div className="mt-2.5">
          <div className="w-full h-1 bg-slate-100 dark:bg-slate-700/50 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-700 ease-out ${
              scoreColor === "emerald" ? "bg-gradient-to-r from-emerald-400 to-teal-400" :
              scoreColor === "amber" ? "bg-gradient-to-r from-amber-400 to-orange-400" :
              "bg-gradient-to-r from-rose-400 to-pink-400"
            }`} style={{ width: `${scorePct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Derived Param Card ─── */
function ParamCard({
  icon,
  label,
  value,
  unit,
  highlight = false,
}: {
  icon: React.ReactNode;
  label: React.ReactNode;
  value: string | number;
  unit?: string;
  highlight?: boolean;
}) {
  return (
    <div className={`flex items-center gap-3 p-3 rounded-[10px] transition-all duration-200 hover:shadow-sm ${
      highlight ? "bg-indigo-50/60 dark:bg-indigo-900/30 border border-indigo-100 dark:border-indigo-800/40" : "bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700"
    }`}>
      <div className={`flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg ${
        highlight ? "bg-indigo-100 dark:bg-indigo-800/40 text-indigo-600 dark:text-indigo-400" : "bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300"
      }`}>{icon}</div>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</p>
        <p className="text-sm font-bold text-slate-800 dark:text-slate-200 tabular-nums truncate">
          {value}{unit && <span className="text-xs font-medium text-slate-500 dark:text-slate-400 ml-1">{unit}</span>}
        </p>
      </div>
    </div>
  );
}

const INDUSTRIAL_DEFAULTS: Record<string, unknown> = {
  sensor_size: "2/3",
  pixel_size_um: 3.45,
  target_width_mm: 50,
  target_height_mm: 40,
  working_distance_mm: 200,
  lens_type: "FA",
  interface: "C-mount",
};

export default function IndustrialPage() {
  const [form, setForm] = useState<Record<string, unknown>>({ ...INDUSTRIAL_DEFAULTS });

  const [coverageData, setCoverageData] = useState<unknown>(null);
  const [coverageLoading, setCoverageLoading] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const [compareSelection, setCompareSelection] = useState<UnifiedMatchResult[]>([]);
  const [paretoOnly, setParetoOnly] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [whatIfExpanded, setWhatIfExpanded] = useState(false);

  const {
    hasSearched,
    results,
    selectedResult,
    rightTab,
    setResults,
    setSelectedResult,
    setHasSearched,
    setRightTab,
  } = useDomainMatching("industrial");

  const handleMatchSuccess = useCallback((matches: UnifiedMatchResult[]) => {
    setResults(matches);
    setCompareMode(false);
    setCompareSelection([]);
    setParetoOnly(false);
  }, [setResults]);

  const {
    progress,
    stage,
    error,
    isLoading,
    diagnostics,
    start,
  } = useMatching({
    domain: "industrial",
    requirements: form,
    onSuccess: handleMatchSuccess,
  });
  const [whatIfResults, setWhatIfResults] = useState<UnifiedMatchResult[]>([]);
  const [whatIfRunning, setWhatIfRunning] = useState(false);
  const whatIfCloseRef = useRef<(() => void) | null>(null);

  const paretoResults = useMemo(() => computeParetoFrontier(results), [results]);
  const displayResults = useMemo(() => {
    return paretoOnly ? paretoResults : results;
  }, [results, paretoResults, paretoOnly]);

  useEffect(() => {
    return () => {
      whatIfCloseRef.current?.();
      whatIfCloseRef.current = null;
    };
  }, []);

  const handleWhatIf = useCallback(async (requirements: Record<string, unknown>) => {
    if (whatIfCloseRef.current) {
      whatIfCloseRef.current();
      whatIfCloseRef.current = null;
    }
    setWhatIfRunning(true);
    try {
      const { close } = await startMatchStream(
        { domain: "industrial", requirements },
        (data) => {
          const stage = String(data.stage ?? "");
          if (stage === "completed") {
            const matches = (data.results as UnifiedMatchResult[]) ?? [];
            setWhatIfResults(matches);
            setWhatIfRunning(false);
          } else if (stage === "error") {
            setWhatIfRunning(false);
          }
        },
        () => {
          setWhatIfRunning(false);
        }
      );
      whatIfCloseRef.current = close;
    } catch {
      setWhatIfRunning(false);
    }
  }, []);

  useEffect(() => {
    if (!selectedResult) {
      setCoverageData(null);
      setCoverageLoading(false);
      return;
    }
    setCoverageLoading(true);
    let cancelled = false;
    generateCoverage(selectedResult.lens_id, selectedResult.detector_id)
      .then((data) => { if (!cancelled) { setCoverageData(data); setCoverageLoading(false); } })
      .catch((e) => { if (!cancelled) { console.error("Coverage error:", e); setCoverageLoading(false); } });
    return () => { cancelled = true; };
  }, [selectedResult]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSelectedResult(null);
    setCompareMode(false);
    setCompareSelection([]);
    setParetoOnly(false);
    setHasSearched(true);
    start();
  };

  const toggleCompare = (r: UnifiedMatchResult) => {
    setCompareSelection((prev) => {
      const exists = prev.find((x) => x.lens_id === r.lens_id && x.detector_id === r.detector_id);
      if (exists) {
        return prev.filter((x) => x.lens_id !== r.lens_id || x.detector_id !== r.detector_id);
      }
      if (prev.length >= 4) {
        toast("warning", "最多对比 4 个方案", "请先取消已选方案再添加");
        return prev;
      }
      return [...prev, r];
    });
  };

  const handleExport = async (format: "pdf" | "excel" | "csv") => {
    if (results.length === 0) return;
    try {
      const blob = await exportReport(
        format, form, results, 20,
        diagnostics ?? undefined,
        whatIfResults.length > 0 ? whatIfResults : undefined
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const extMap: Record<string, string> = { pdf: "pdf", excel: "xlsx", csv: "csv" };
      a.download = `optibench-report.${extMap[format]}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast("success", "导出成功", `${format.toUpperCase()} 报告已下载`);
    } catch (e) {
      console.error("Export failed:", e);
      toast("error", "导出失败", "无法生成报告，请重试");
    }
  };

  const leftPanel = (
    <DomainFormPanel
      title="选型参数"
      subtitle="配置您的光学系统需求"
      icon={Icons.search}
      domain="industrial"
      onPresetSelect={(preset: PresetConfigItem) => {
        setForm((prev) => ({ ...prev, ...preset.params }));
      }}
      onSubmit={handleSubmit}
      isLoading={isLoading}
      progress={progress}
      stage={stage}
      submitIcon={Icons.search}
    >
      <DomainForm
        domain="industrial"
        values={form}
        onChange={(name, value) => setForm((prev) => ({ ...prev, [name]: value }))}
        disabled={isLoading}
      />
    </DomainFormPanel>
  );

  const resultsAction = results.length > 0 ? (
    <div className="flex items-center gap-2">
      <CompareParetoToolbar
        compareMode={compareMode}
        onCompareModeChange={(v) => {
          setCompareMode(v);
          if (!v) setCompareSelection([]);
        }}
        paretoOnly={paretoOnly}
        onParetoChange={setParetoOnly}
        selectionCount={compareSelection.length}
        onClearSelection={() => setCompareSelection([])}
      />
      {compareMode && compareSelection.length >= 2 && (
        <Button variant="primary" size="sm" leftIcon={<ArrowLeftRight size={14} />} onClick={() => setSelectedResult(null)}>开始对比</Button>
      )}
      {!compareMode && (
        <div className="flex items-center gap-1">
          <button title="导出 PDF" aria-label="导出 PDF" onClick={() => handleExport("pdf")} className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors">
            <FileText size={14} />
          </button>
          <button title="导出 Excel" aria-label="导出 Excel" onClick={() => handleExport("excel")} className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors">
            <Table2 size={14} />
          </button>
          <button title="导出 CSV" aria-label="导出 CSV" onClick={() => handleExport("csv")} className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors">
            {Icons.table}
          </button>
          <button title="保存到项目" aria-label="保存到项目" onClick={() => setSaveDialogOpen(true)} className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors">
            <FolderPlus size={14} />
          </button>
        </div>
      )}
    </div>
  ) : undefined;

  const centerPanel = (
    <DomainResultsPanel
      title="匹配结果"
      subtitle={displayResults.length > 0 ? `共找到 ${displayResults.length} 组匹配方案${paretoOnly ? "（Pareto 前沿）" : ""}` : "等待参数输入"}
      icon={<AlertTriangle size={16} />}
      action={resultsAction}
    >
      {error && (
        <div className="mb-4 p-4 bg-rose-50 dark:bg-rose-900/20 border border-rose-100 dark:border-rose-800/30 rounded-xl flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5 text-rose-500 dark:text-rose-400">{Icons.alert}</div>
          <div>
            <p className="text-sm font-semibold text-rose-700 dark:text-rose-300">发生错误</p>
            <p className="text-xs text-rose-600 dark:text-rose-400 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {displayResults.length === 0 && !isLoading && !error && (
        <div className="flex-1">
          {!hasSearched ? (
            <div className="h-full flex items-center justify-center">
              <EmptyState icon={<Search size={24} />} title="等待匹配" description="在左侧配置参数后点击「自动匹配」，系统将为您推荐最优镜头与探测器组合" />
            </div>
          ) : diagnostics && diagnostics.length > 0 ? (
            <DiagnosticsPanel
              diagnostics={diagnostics}
              onAdjustParam={(name, value) => {
                setForm((prev) => ({ ...prev, [name]: value }));
                toast("info", "参数已调整", `${name} 已设为 ${String(value)}，请重新匹配`);
              }}
            />
          ) : paretoOnly ? (
            <div className="h-full flex items-center justify-center">
              <EmptyState icon={<Layers size={24} />} title="Pareto 前沿为空" description="当前结果中没有被支配关系明显的领先方案，请关闭 Pareto 过滤查看全部" />
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <EmptyState icon={<Search size={24} />} title="未找到匹配方案" description="系统未找到符合条件的镜头与探测器组合，请尝试放宽参数" />
            </div>
          )}
        </div>
      )}

      {results.length > 0 && (
        <div className="mb-3">
          <button
            onClick={() => setWhatIfExpanded((v) => !v)}
            className="w-full flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-700 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Zap size={12} className="text-amber-500" />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">参数灵敏度分析</span>
              <span className="text-xs text-slate-500 dark:text-slate-400">点击展开调整参数并查看影响</span>
            </div>
            {whatIfExpanded ? <ChevronUp size={12} className="text-slate-400" /> : <ChevronDown size={12} className="text-slate-400" />}
          </button>
          {whatIfExpanded && (
            <div className="mt-2">
              <WhatIfPanel
                form={form}
                onChange={(key, value) => {
                  setForm((prev) => ({ ...prev, [key]: value }));
                }}
                onRunWhatIf={handleWhatIf}
                baselineResults={results}
                whatIfResults={whatIfResults}
                isRunning={whatIfRunning}
              />
            </div>
          )}
        </div>
      )}

      {isLoading && results.length === 0 && (
        <div className="space-y-2.5">
          <ResultCardSkeleton />
          <ResultCardSkeleton />
          <ResultCardSkeleton />
        </div>
      )}

      {displayResults.length > 0 && (
        <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1 stagger-children">
          {displayResults.slice(0, 20).map((r, i) => (
            <ResultCard
              key={`${r.lens_id}-${r.detector_id}`}
              result={r}
              rank={i + 1}
              isSelected={selectedResult?.lens_id === r.lens_id && selectedResult?.detector_id === r.detector_id}
              onClick={() => setSelectedResult(r)}
              compareMode={compareMode}
              isCompareSelected={compareSelection.some((x) => x.lens_id === r.lens_id && x.detector_id === r.detector_id)}
              onToggleCompare={() => toggleCompare(r)}
            />
          ))}
        </div>
      )}
    </DomainResultsPanel>
  );

  const compareView = (
    <>
      <SectionHeader title="方案对比" subtitle={`已选中 ${compareSelection.length} 个方案`} icon={<ArrowLeftRight size={16} />} />
      <CompareView results={compareSelection} />
    </>
  );

  const vizTab = (
    <div className="space-y-5">
      {selectedResult && (
        <MatchExplanation result={selectedResult} domain="industrial" />
      )}
      {coverageLoading ? (
        <CoverageSkeleton width={320} height={280} />
      ) : (
        <SensorCoveragePlot data={coverageData as { sensor_rect: { x: number; y: number; w: number; h: number }; image_circle: { cx: number; cy: number; r: number }; vignetting_regions: Array<{ points: Array<{ x: number; y: number }> }>; coverage_ratio: number; safe_zone: { x: number; y: number; w: number; h: number } } | null} width={320} height={280} />
      )}

      {selectedResult?.score_vector && (
        <div>
          <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">评分维度</h3>
          <ScoreRadarChart scoreVector={selectedResult.score_vector} size={220} />
        </div>
      )}

      {selectedResult?.derived && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">光学参数</h3>
          {(() => {
            const d = selectedResult.derived as Record<string, unknown>;
            const cov = d.coverage as Record<string, unknown> | undefined;
            const nq = d.nyquist as Record<string, unknown> | undefined;
            return (
              <>
                <div className="grid grid-cols-2 gap-2.5">
                  {d.focal_length != null && (
                    <ParamCard icon={Icons.focus} label={<GlossaryTooltip term="focal_length">估算焦距</GlossaryTooltip>} value={d.focal_length as number} unit="mm" highlight />
                  )}
                  {d.magnification != null && (
                    <ParamCard icon={Icons.zoom} label={<GlossaryTooltip term="magnification">放大倍率</GlossaryTooltip>} value={d.magnification as number} highlight />
                  )}
                  {d.pixel_accuracy_mm != null && (
                    <ParamCard icon={Icons.crosshair} label={<GlossaryTooltip term="pixel_accuracy_mm">像素精度</GlossaryTooltip>} value={d.pixel_accuracy_mm as number} unit="mm/px" />
                  )}
                  {cov != null && (
                    <ParamCard icon={Icons.layers} label={<GlossaryTooltip term="coverage_ratio">覆盖比</GlossaryTooltip>} value={`${(((cov.coverage_ratio as number) || 0) * 100).toFixed(0)}%`} highlight={((cov.coverage_ratio as number) || 0) >= 0.9} />
                  )}
                </div>

                {cov != null && (
                  <div className="mt-2 p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"><GlossaryTooltip term="vignetting">渐晕风险</GlossaryTooltip></span>
                      <Badge variant={cov.vignetting ? "warning" : "success"} size="sm">{cov.vignetting ? "有" : "无"}</Badge>
                    </div>
                    <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-500 ${cov.vignetting ? "bg-gradient-to-r from-amber-400 to-orange-400 w-3/4" : "bg-gradient-to-r from-emerald-400 to-teal-400 w-full"}`} />
                    </div>
                  </div>
                )}

                {nq != null && (
                  <div className="mt-3 grid grid-cols-2 gap-2.5">
                    <ParamCard icon={Icons.activity} label={<GlossaryTooltip term="nyquist_limit">奈奎斯特</GlossaryTooltip>} value={nq.sensor_nyquist_lpmm as number} unit="lp/mm" />
                    <ParamCard icon={Icons.eye} label={<GlossaryTooltip term="resolution">光学极限</GlossaryTooltip>} value={nq.optical_limit_lpmm as number} unit="lp/mm" />
                  </div>
                )}
              </>
            );
          })()}
        </div>
      )}

      {!selectedResult && !coverageLoading && (
        <div className="text-center py-8">
          <EmptyState icon={<Image size={24} />} title="选择匹配方案" description="点击左侧结果卡片查看覆盖图与详细参数" />
        </div>
      )}
    </div>
  );

  const traceTab = (
    <div>
      {selectedResult?.derivation_chain && selectedResult.derivation_chain.length > 0 ? (
        <PhysicsTrace traces={selectedResult.derivation_chain} />
      ) : (
        <div className="text-center py-8">
          <EmptyState icon={<Activity size={24} />} title="推导链" description="选择一个匹配方案查看光学计算推导过程" />
        </div>
      )}
    </div>
  );

  const rightPanel = (
    <DomainDetailPanel
      title="可视化分析"
      subtitle="覆盖图、评分维度与推导链"
      icon={<BarChart3 size={16} />}
      activeTab={rightTab}
      onTabChange={setRightTab}
      theme="indigo"
      isCompareActive={compareMode && compareSelection.length >= 2}
      compareView={compareView}
      tabs={[
        { key: "viz", label: "可视化", icon: <BarChart3 size={13} /> },
        { key: "trace", label: "推导链", icon: <Activity size={13} /> },
        { key: "knowledge", label: "知识库", icon: <BookOpen size={13} /> },
        { key: "learning", label: "学习指导", icon: <GraduationCap size={13} /> },
      ]}
      viz={vizTab}
      trace={traceTab}
      knowledge={
        <KnowledgePanel
          form={form}
          domain="industrial"
          activeTab="formulas"
          selectedResult={selectedResult}
        />
      }
      learning={<IndustrialLearningHub form={form} />}
    />
  );

  return (
    <>
      <DomainPageShell
        left={leftPanel}
        center={centerPanel}
        right={rightPanel}
      />
      <SaveToProjectDialog
        isOpen={saveDialogOpen}
        onClose={() => setSaveDialogOpen(false)}
        lensId={selectedResult?.lens_id}
        detectorId={selectedResult?.detector_id}
        matchResultSnapshot={selectedResult ?? undefined}
      />
    </>
  );
}
