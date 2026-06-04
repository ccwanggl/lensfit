import { useState, useEffect } from "react";
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
} from "lucide-react";
import SensorCoveragePlot from "../components/SensorCoveragePlot";
import ScoreRadarChart from "../components/ScoreRadarChart";
import DomainForm from "../components/DomainForm";
import {
  Card,
  Button,
  Badge,
  ProgressBar,
  SectionHeader,
  EmptyState,
} from "../components/ui";
import { ResultCardSkeleton, CoverageSkeleton } from "../components/ui/Skeleton";
import { toast } from "../hooks/useToast";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import PhysicsTrace from "../components/PhysicsTrace";
import {
  generateCoverage,
  exportReport,
} from "../utils/api";

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
    <span className={`flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-lg text-[11px] font-extrabold ${colors[rank] || "bg-slate-100 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 dark:text-slate-500"}`}>
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
}: {
  result: UnifiedMatchResult;
  rank: number;
  isSelected: boolean;
  onClick: () => void;
}) {
  const scorePct = Math.min((result.score / 10) * 100, 100);
  const scoreColor = scorePct >= 80 ? "emerald" : scorePct >= 50 ? "amber" : "rose";

  return (
    <div
      onClick={onClick}
      className={`
        group relative flex items-start gap-3 p-4 rounded-xl cursor-pointer
        transition-all duration-200 ease-out
        ${isSelected
          ? "bg-indigo-50/70 dark:bg-indigo-900/30 border-2 border-indigo-300 dark:border-indigo-700 shadow-[0_2px_12px_rgba(99,102,241,0.12)]"
          : "bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 hover:border-indigo-200 hover:shadow-md hover:-translate-y-0.5"
        }
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
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">评分</span>
            <span className="text-base font-extrabold text-indigo-600 dark:text-indigo-400 tabular-nums">{result.score?.toFixed(2) || "-"}</span>
          </div>
        </div>

        <p className="text-xs text-slate-500 dark:text-slate-400 dark:text-slate-500 truncate mb-2.5">{result.detector_model || `探测器 #${result.detector_id}`}</p>

        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant={result.vignetting ? "warning" : "success"} size="sm">
            <span className="flex items-center gap-1">{result.vignetting ? Icons.alert : Icons.check} {result.vignetting ? "渐晕" : "无渐晕"}</span>
          </Badge>
          <Badge variant="neutral" size="sm">覆盖 {((result.coverage_ratio || 0) * 100).toFixed(0)}%</Badge>
        </div>

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
  label: string;
  value: string | number;
  unit?: string;
  highlight?: boolean;
}) {
  return (
    <div className={`flex items-center gap-3 p-3 rounded-[10px] transition-all duration-200 hover:shadow-sm ${
      highlight ? "bg-indigo-50/60 dark:bg-indigo-900/30 border border-indigo-100 dark:border-indigo-800/40" : "bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700"
    }`}>
      <div className={`flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg ${
        highlight ? "bg-indigo-100 dark:bg-indigo-800/40 text-indigo-600 dark:text-indigo-400" : "bg-slate-100 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 dark:text-slate-500"
      }`}>{icon}</div>
      <div className="min-w-0">
        <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{label}</p>
        <p className="text-sm font-bold text-slate-800 dark:text-slate-200 tabular-nums truncate">
          {value}{unit && <span className="text-[10px] font-medium text-slate-400 dark:text-slate-500 ml-1">{unit}</span>}
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

  const [selectedResult, setSelectedResult] = useState<UnifiedMatchResult | null>(null);
  const [coverageData, setCoverageData] = useState<unknown>(null);
  const [coverageLoading, setCoverageLoading] = useState(false);

  const {
    progress,
    stage,
    error,
    results,
    isLoading,
    start,
  } = useMatching({
    domain: "industrial",
    requirements: form,
    onSuccess: (matches) => {
      setSelectedResult(matches[0] ?? null);
    },
  });

  // Load coverage when result selected
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
    start();
  };

  const handleExport = async (format: "pdf" | "excel") => {
    if (results.length === 0) return;
    try {
      const blob = await exportReport(format, form, results, 20);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = format === "pdf" ? "lensfit-report.pdf" : "lensfit-report.xlsx";
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

  return (
    <div className="grid grid-cols-12 gap-5">
      {/* ── Left: Input Panel ── */}
      <div className="col-span-3">
        <Card padding="none" className="overflow-hidden">
          <div className="p-6">
            <SectionHeader title="选型参数" subtitle="配置您的光学系统需求" icon={Icons.search} />
            <form onSubmit={handleSubmit} className="space-y-4">
              <DomainForm
                domain="industrial"
                values={form}
                onChange={(name, value) => setForm((prev) => ({ ...prev, [name]: value }))}
                disabled={isLoading}
              />

              <div className="pt-2">
                <Button type="submit" variant="primary" size="lg" loading={isLoading} leftIcon={Icons.search} className="w-full">
                  {isLoading ? "计算中..." : "自动匹配"}
                </Button>
              </div>

              {isLoading && (
                <div className="space-y-2 pt-1">
                  <ProgressBar value={progress} color="indigo" label={stage || "准备中"} showValue />
                </div>
              )}
            </form>
          </div>
        </Card>
      </div>

      {/* ── Center: Results Panel ── */}
      <div className="col-span-5">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-6 flex-1 flex flex-col">
            <SectionHeader
              title="匹配结果"
              subtitle={results.length > 0 ? `共找到 ${results.length} 组匹配方案` : "等待参数输入"}
              icon={<AlertTriangle size={16} />}
              action={
                results.length > 0 && (
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" leftIcon={Icons.fileText} onClick={() => handleExport("pdf")}>PDF</Button>
                    <Button variant="outline" size="sm" leftIcon={Icons.table} onClick={() => handleExport("excel")}>Excel</Button>
                  </div>
                )
              }
            />

            {error && (
              <div className="mb-4 p-4 bg-rose-50 dark:bg-rose-900/20 border border-rose-100 dark:border-rose-800/30 rounded-xl flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5 text-rose-500 dark:text-rose-400">{Icons.alert}</div>
                <div>
                  <p className="text-sm font-semibold text-rose-700 dark:text-rose-300">发生错误</p>
                  <p className="text-xs text-rose-600 dark:text-rose-400 mt-0.5">{error}</p>
                </div>
              </div>
            )}

            {results.length === 0 && !isLoading && !error && (
              <div className="flex-1 flex items-center justify-center">
                <EmptyState icon={<Search size={24} />} title="等待匹配" description="在左侧配置参数后点击「自动匹配」，系统将为您推荐最优镜头与探测器组合" />
              </div>
            )}

            {/* Skeleton loading during match */}
            {isLoading && results.length === 0 && (
              <div className="space-y-2.5">
                <ResultCardSkeleton />
                <ResultCardSkeleton />
                <ResultCardSkeleton />
              </div>
            )}

            {results.length > 0 && (
              <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1 stagger-children">
                {results.slice(0, 20).map((r, i) => (
                  <ResultCard
                    key={`${r.lens_id}-${r.detector_id}`}
                    result={r}
                    rank={i + 1}
                    isSelected={selectedResult?.lens_id === r.lens_id && selectedResult?.detector_id === r.detector_id}
                    onClick={() => setSelectedResult(r)}
                  />
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* ── Right: Visualization Panel ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden">
          <div className="p-6">
            <SectionHeader title="可视化分析" subtitle="传感器与像圈覆盖关系" icon={Icons.image} />

            {coverageLoading ? (
              <CoverageSkeleton width={320} height={280} />
            ) : (
              <SensorCoveragePlot data={coverageData as { sensor_rect: { x: number; y: number; w: number; h: number }; image_circle: { cx: number; cy: number; r: number }; vignetting_regions: Array<{ points: Array<{ x: number; y: number }> }>; coverage_ratio: number; safe_zone: { x: number; y: number; w: number; h: number } } | null} width={320} height={280} />
            )}

            {selectedResult?.score_vector && (
              <div className="mt-5">
                <h3 className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">评分维度</h3>
                <ScoreRadarChart scoreVector={selectedResult.score_vector} size={220} />
              </div>
            )}

            {selectedResult?.derived && (
              <div className="mt-5 space-y-3">
                <h3 className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">光学参数</h3>
                {(() => {
                  const d = selectedResult.derived as Record<string, unknown>;
                  const cov = d.coverage as Record<string, unknown> | undefined;
                  const nq = d.nyquist as Record<string, unknown> | undefined;
                  return (
                    <>
                      <div className="grid grid-cols-2 gap-2.5">
                        {d.focal_length != null && (
                          <ParamCard icon={Icons.focus} label="估算焦距" value={d.focal_length as number} unit="mm" highlight />
                        )}
                        {d.magnification != null && (
                          <ParamCard icon={Icons.zoom} label="放大倍率" value={d.magnification as number} highlight />
                        )}
                        {d.pixel_accuracy_mm != null && (
                          <ParamCard icon={Icons.crosshair} label="像素精度" value={d.pixel_accuracy_mm as number} unit="mm/px" />
                        )}
                        {cov != null && (
                          <ParamCard icon={Icons.layers} label="覆盖比" value={`${(((cov.coverage_ratio as number) || 0) * 100).toFixed(0)}%`} highlight={((cov.coverage_ratio as number) || 0) >= 0.9} />
                        )}
                      </div>

                      {cov != null && (
                        <div className="mt-2 p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">渐晕风险</span>
                            <Badge variant={cov.vignetting ? "warning" : "success"} size="sm">
                              {cov.vignetting ? "有" : "无"}
                            </Badge>
                          </div>
                          <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                            <div className={`h-full rounded-full transition-all duration-500 ${
                              cov.vignetting
                                ? "bg-gradient-to-r from-amber-400 to-orange-400 w-3/4"
                                : "bg-gradient-to-r from-emerald-400 to-teal-400 w-full"
                            }`} />
                          </div>
                        </div>
                      )}

                      {nq != null && (
                        <div className="mt-3 grid grid-cols-2 gap-2.5">
                          <ParamCard icon={Icons.activity} label="奈奎斯特" value={nq.sensor_nyquist_lpmm as number} unit="lp/mm" />
                          <ParamCard icon={Icons.eye} label="光学极限" value={nq.optical_limit_lpmm as number} unit="lp/mm" />
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            )}

            {selectedResult?.derivation_chain && selectedResult.derivation_chain.length > 0 && (
              <PhysicsTrace traces={selectedResult.derivation_chain} />
            )}

            {!selectedResult && !coverageLoading && (
              <div className="mt-4 text-center py-8">
                <EmptyState icon={<Image size={24} />} title="选择匹配方案" description="点击左侧结果卡片查看覆盖图与详细参数" />
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
