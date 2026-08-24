import { useState, useMemo, useCallback, useEffect } from "react";
import {
  Camera,
  Aperture,
  Ruler,
  Eye,
  DollarSign,
  Tag,
  Plug,
  Search,
  Star,
  Image,
  BarChart3,
  Activity,
  BookOpen,
  GraduationCap,
} from "lucide-react";
import { Input, Badge, EmptyState } from "../components/ui";
import { listLenses, listDetectors } from "../utils/api";
import { toast } from "../hooks/useToast";
import LensImage from "../components/LensImage";
import PhysicsTrace from "../components/PhysicsTrace";
import KnowledgePanel from "../components/KnowledgePanel";
import PhotographyLearningHub from "../components/PhotographyLearningHub";
import ScoreRadarChart from "../components/ScoreRadarChart";
import MtfCurve from "../components/MtfCurve";
import CocChart from "../components/CocChart";
import ExportActions from "../components/ExportActions";
import MatchExplanation from "../components/MatchExplanation";
import SensorCoveragePlot from "../components/SensorCoveragePlot";
import DiagnosticsPanel from "../components/DiagnosticsPanel";
import CompareView from "../components/CompareView";
import CompareParetoToolbar, { computeParetoFrontier } from "../components/CompareParetoToolbar";
import { type InputChangeEvent } from "../components/ui/Input";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import { useParamHint } from "../hooks/useParamHint";
import type { CatalogLens, CatalogDetector, PresetConfigItem } from "../utils/api";
import { generateMtf, generateCoc, generateCoverage, type MtfData, type CocData, type CoverageData } from "../utils/api";
import { useDomainMatching } from "../stores/matchingStore";
import {
  DomainPageShell,
  DomainFormPanel,
  DomainResultsPanel,
  DomainDetailPanel,
} from "../components/domain";

interface PhotoRequest {
  format: string;
  lens_type: string;
  focal_range: string;
  max_aperture: string;
  purpose: string;
  brand: string;
  mount: string;
  budget: number;
}

const FORMATS = [
  { value: "all", label: "全部画幅" },
  { value: "FF", label: "全画幅 (FF)" },
  { value: "APS-C", label: "APS-C" },
  { value: "M43", label: "M43" },
];

const LENS_TYPES = [
  { value: "all", label: "全部类型" },
  { value: "prime", label: "定焦" },
  { value: "zoom", label: "变焦" },
];

const FOCAL_RANGES = [
  { value: "all", label: "全部焦距", min: 0, max: 9999 },
  { value: "ultrawide", label: "超广角 <16mm", min: 0, max: 16 },
  { value: "wide", label: "广角 16-35mm", min: 16, max: 35 },
  { value: "standard", label: "标准 35-85mm", min: 35, max: 85 },
  { value: "portrait", label: "人像 85-135mm", min: 85, max: 135 },
  { value: "tele", label: "长焦 135-300mm", min: 135, max: 300 },
  { value: "supertele", label: "超长焦 >300mm", min: 300, max: 9999 },
];

const APERTURES = [
  { value: "all", label: "全部光圈" },
  { value: "1.2", label: "f/1.2 或更大" },
  { value: "1.4", label: "f/1.4 或更大" },
  { value: "1.8", label: "f/1.8 或更大" },
  { value: "2.8", label: "f/2.8 或更大" },
  { value: "4.0", label: "f/4 或更大" },
];

const PURPOSES = [
  { value: "all", label: "全部用途" },
  { value: "portrait", label: "人像" },
  { value: "landscape", label: "风景" },
  { value: "street", label: "街拍" },
  { value: "macro", label: "微距" },
  { value: "sports", label: "体育/野生动物" },
  { value: "video", label: "视频" },
];

const BRANDS = [
  { value: "all", label: "全部品牌" },
  { value: "Canon", label: "Canon" },
  { value: "Sony", label: "Sony" },
  { value: "Nikon", label: "Nikon" },
  { value: "Sigma", label: "Sigma" },
  { value: "Tamron", label: "Tamron" },
  { value: "Fujifilm", label: "Fujifilm" },
];

const MOUNTS = [
  { value: "all", label: "全部卡口" },
  { value: "RF", label: "Canon RF" },
  { value: "EF", label: "Canon EF" },
  { value: "E-mount", label: "Sony E" },
  { value: "Z-mount", label: "Nikon Z" },
  { value: "X-mount", label: "Fujifilm X" },
  { value: "L-mount", label: "L-mount" },
];

function LensCard({
  lens,
  rank,
  isSelected,
  onClick,
  score,
}: {
  lens: CatalogLens;
  rank: number;
  isSelected: boolean;
  onClick: () => void;
  score: number;
}) {
  const isZoom = lens.focal_length_min !== lens.focal_length_max && lens.focal_length_min != null;
  const focalDisplay = isZoom
    ? `${lens.focal_length_min}-${lens.focal_length_max}mm`
    : `${lens.focal_length_mm}mm`;

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      }}
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
        isSelected ? "bg-indigo-500" : score >= 0.8 ? "bg-emerald-400" : score >= 0.5 ? "bg-amber-400" : "bg-rose-400"
      }`} />

      <span className={`flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-lg text-[11px] font-extrabold ${
        rank === 1 ? "bg-gradient-to-br from-amber-300 to-amber-500 text-white shadow-[0_2px_6px_rgba(245,158,11,0.4)]" :
        rank === 2 ? "bg-gradient-to-br from-slate-300 to-slate-400 text-white shadow-[0_2px_6px_rgba(148,163,184,0.4)]" :
        rank === 3 ? "bg-gradient-to-br from-orange-300 to-orange-400 text-white shadow-[0_2px_6px_rgba(251,146,60,0.4)]" :
        "bg-slate-100 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400"
      }`}>{rank}</span>

      <div className="flex-shrink-0">
        <LensImage
          model={lens.model}
          focal={focalDisplay}
          aperture={String(lens.max_aperture)}
          brand=""
          imageUrl={lens.image_url}
          size="sm"
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">{lens.model}</h4>
          <span className="text-base font-extrabold text-indigo-600 dark:text-indigo-400 tabular-nums">{(score * 100).toFixed(0)}</span>
        </div>
        <div className="flex items-center gap-2 flex-wrap text-xs text-slate-500 dark:text-slate-400 mb-2">
          <Badge variant="neutral" size="sm">{focalDisplay}</Badge>
          <Badge variant="neutral" size="sm">f/{lens.max_aperture}</Badge>
          <Badge variant="neutral" size="sm">{lens.mount_type}</Badge>
        </div>
        <div className="mt-2 text-xs font-semibold text-slate-700 dark:text-slate-300">
          ${lens.price_usd.toFixed(0)}
        </div>
      </div>
    </div>
  );
}

export default function PhotographyPage() {
  const { hint, expanded } = useParamHint();
  const [form, setForm] = useState<PhotoRequest>({
    format: "all",
    lens_type: "all",
    focal_range: "all",
    max_aperture: "all",
    purpose: "portrait",
    brand: "all",
    mount: "all",
    budget: 3000,
  });

  const {
    hasSearched,
    results,
    selectedResult: selectedMatch,
    rightTab,
    catalogs,
    setResults,
    setSelectedResult,
    setHasSearched,
    setRightTab,
    setCatalogs,
  } = useDomainMatching("photography");

  const { lensMap, detMap } = catalogs;

  const [mtfData, setMtfData] = useState<MtfData | null>(null);
  const [cocData, setCocData] = useState<CocData | null>(null);
  const [coverageData, setCoverageData] = useState<CoverageData | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareSelection, setCompareSelection] = useState<UnifiedMatchResult[]>([]);
  const [paretoOnly, setParetoOnly] = useState(false);

  const backendRequirements = useMemo(() => {
    const range = FOCAL_RANGES.find((r) => r.value === form.focal_range);
    return {
      purpose: form.purpose === "all" ? "portrait" : form.purpose,
      sensor_format: form.format === "all" ? "FF" : form.format,
      lens_type: form.lens_type,
      mount: form.mount,
      budget_usd: form.budget,
      max_aperture: form.max_aperture === "all" ? 2.8 : parseFloat(form.max_aperture),
      brand: form.brand,
      focal_range_min: range?.min,
      focal_range_max: range?.max,
    };
  }, [form]);

  const handleMatchSuccess = useCallback((matches: UnifiedMatchResult[]) => {
    setResults(matches);
  }, [setResults]);

  const { isLoading, progress, stage, diagnostics, start } = useMatching({
    domain: "photography",
    requirements: backendRequirements,
    onSuccess: handleMatchSuccess,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    setSelectedResult(null);

    try {
      const [lensData, detData] = await Promise.all([
        listLenses({ limit: 100 }),
        listDetectors({ limit: 100 }),
      ]);

      const lm = new Map<number, CatalogLens>();
      for (const l of lensData.items || []) lm.set(l.id, l);

      const dm = new Map<number, CatalogDetector>();
      for (const d of detData.items || []) dm.set(d.id, d);

      setCatalogs({ lensMap: lm, detMap: dm });

      start();
    } catch (e) {
      console.error("Load photo data failed:", e);
      toast("error", "数据加载失败", "无法获取摄影镜头数据");
    }
  };

  const enrichedResults = useMemo(() => {
    return results
      .map((r) => ({ match: r, lens: lensMap.get(r.lens_id) }))
      .filter((item): item is { match: UnifiedMatchResult; lens: CatalogLens } => !!item.lens);
  }, [results, lensMap]);

  const selectedLens = selectedMatch ? lensMap.get(selectedMatch.lens_id) : undefined;
  const selectedDet = selectedMatch ? detMap.get(selectedMatch.detector_id) : undefined;

  const paretoResults = useMemo(() => computeParetoFrontier(enrichedResults.map((e) => e.match)), [enrichedResults]);
  const [showAllResults, setShowAllResults] = useState(false);
  const displayResults = useMemo(() => {
    if (!paretoOnly) return enrichedResults;
    const paretoSet = new Set(paretoResults.map((r) => `${r.lens_id}-${r.detector_id}`));
    return enrichedResults.filter((e) => paretoSet.has(`${e.match.lens_id}-${e.match.detector_id}`));
  }, [enrichedResults, paretoResults, paretoOnly]);

  const isCompareSelected = (r: UnifiedMatchResult) =>
    compareSelection.some((x) => x.lens_id === r.lens_id && x.detector_id === r.detector_id);

  const toggleCompare = (r: UnifiedMatchResult) => {
    setCompareSelection((prev) => {
      const exists = prev.some((x) => x.lens_id === r.lens_id && x.detector_id === r.detector_id);
      if (exists) return prev.filter((x) => !(x.lens_id === r.lens_id && x.detector_id === r.detector_id));
      if (prev.length >= 4) {
        toast("warning", "最多对比 4 个方案", "请先取消已选方案再添加");
        return prev;
      }
      return [...prev, r];
    });
  };

  useEffect(() => {
    if (!selectedMatch || !selectedLens || !selectedDet) {
      setMtfData(null);
      setCocData(null);
      setCoverageData(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const [mtf, coc, coverage] = await Promise.all([
          generateMtf(selectedLens.id, selectedDet.id),
          generateCoc(selectedLens.id, selectedDet.id),
          generateCoverage(selectedLens.id, selectedDet.id),
        ]);
        if (!cancelled) {
          setMtfData(mtf);
          setCocData(coc);
          setCoverageData(coverage);
        }
      } catch (e) {
        if (!cancelled) {
          setMtfData(null);
          setCocData(null);
          setCoverageData(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedMatch, selectedLens, selectedDet]);

  const compatibleCameras = useMemo(() => {
    if (!selectedLens) return [];
    return Array.from(detMap.values()).filter(
      (c) => c.mount_type && selectedLens.mount_type && c.mount_type.toLowerCase() === selectedLens.mount_type.toLowerCase()
    );
  }, [selectedLens, detMap]);

  const leftPanel = (
    <DomainFormPanel
      title="摄影参数"
      subtitle="配置您的摄影系统需求"
      icon={<Camera size={16} />}
      domain="photography"
      onPresetSelect={(preset: PresetConfigItem) => {
        setForm((prev) => ({ ...prev, ...preset.params }));
      }}
      onSubmit={handleSubmit}
      isLoading={isLoading}
      progress={progress}
      stage={stage}
      submitIcon={<Search size={16} />}
    >
      <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
        <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">相机配置</p>
        <Input as="select" label="画幅" icon={<Image size={14} />} layout="horizontal" learnHint={hint("sensor_format")} hintExpanded={expanded}
          value={form.format}
          onChange={(e: InputChangeEvent) => setForm({ ...form, format: e.target.value })}>
          {FORMATS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
        </Input>

        <Input as="select" label="镜头类型" icon={<Aperture size={14} />} layout="horizontal" learnHint={hint("lens_type")} hintExpanded={expanded}
          value={form.lens_type}
          onChange={(e: InputChangeEvent) => setForm({ ...form, lens_type: e.target.value })}>
          {LENS_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </Input>

        <Input as="select" label="焦距范围" icon={<Ruler size={14} />} layout="horizontal" learnHint={hint("focal_range")} hintExpanded={expanded}
          value={form.focal_range}
          onChange={(e: InputChangeEvent) => setForm({ ...form, focal_range: e.target.value })}>
          {FOCAL_RANGES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
        </Input>

        <Input as="select" label="最大光圈" icon={<Aperture size={14} />} layout="horizontal" learnHint={hint("max_aperture")} hintExpanded={expanded}
          value={form.max_aperture}
          onChange={(e: InputChangeEvent) => setForm({ ...form, max_aperture: e.target.value })}>
          {APERTURES.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
        </Input>

        <Input as="select" label="拍摄用途" icon={<Eye size={14} />} layout="horizontal" learnHint={hint("purpose")} hintExpanded={expanded}
          value={form.purpose}
          onChange={(e: InputChangeEvent) => setForm({ ...form, purpose: e.target.value })}>
          {PURPOSES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
        </Input>
      </div>

      <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
        <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">品牌与预算</p>
        <Input as="select" label="品牌偏好" icon={<Tag size={14} />} layout="horizontal" learnHint={hint("brand")} hintExpanded={expanded}
          value={form.brand}
          onChange={(e: InputChangeEvent) => setForm({ ...form, brand: e.target.value })}>
          {BRANDS.map((b) => <option key={b.value} value={b.value}>{b.label}</option>)}
        </Input>

        <Input as="select" label="卡口" icon={<Plug size={14} />} layout="horizontal" learnHint={hint("mount")} hintExpanded={expanded}
          value={form.mount}
          onChange={(e: InputChangeEvent) => setForm({ ...form, mount: e.target.value })}>
          {MOUNTS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
        </Input>

        <Input type="number" label="预算上限" icon={<DollarSign size={14} />} unit="USD" layout="horizontal" learnHint={hint("budget_usd")} hintExpanded={expanded}
          value={form.budget}
          onChange={(e: InputChangeEvent) => setForm({ ...form, budget: parseFloat(e.target.value) || 0 })} />
      </div>
    </DomainFormPanel>
  );

  const centerPanel = (
    <DomainResultsPanel
      title={compareMode ? "方案对比" : "推荐镜头"}
      subtitle={hasSearched ? `从后端匹配结果中筛选出 ${displayResults.length} 支推荐${paretoOnly ? "（Pareto 前沿）" : ""}` : "等待参数输入"}
      icon={<Star size={16} />}
      action={
        hasSearched ? (
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
            <ExportActions
              requirements={backendRequirements}
              results={results}
              disabled={results.length === 0}
            />
          </div>
        ) : undefined
      }
    >
      {!hasSearched ? (
        <div className="flex-1 flex items-center justify-center">
          <EmptyState
            icon={<Camera size={24} />}
            title="等待匹配"
            description="在左侧配置摄影参数后点击「自动匹配」，系统将为您推荐最适合的镜头"
          />
        </div>
      ) : displayResults.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          {!isLoading && diagnostics && diagnostics.length > 0 ? (
            <DiagnosticsPanel
              diagnostics={diagnostics}
              onAdjustParam={(name, value) => {
                setForm((prev) => ({ ...prev, [name]: value as string | number }));
                toast("info", "参数已调整", `${name} 已设为 ${String(value)}，请重新匹配`);
              }}
            />
          ) : (
            <EmptyState
              icon={<Search size={24} />}
              title={isLoading ? "计算中..." : "无匹配结果"}
              description={isLoading ? "后端正在执行光学计算与评分..." : "当前参数组合没有找到匹配的镜头，请放宽条件后重试"}
            />
          )}
        </div>
      ) : (
        <>
          {compareSelection.length >= 2 && (
            <div className="mb-4">
              <CompareView results={compareSelection} />
            </div>
          )}
          <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1 stagger-children">
            {(showAllResults ? displayResults : displayResults.slice(0, 20)).map(({ match, lens }, i) => (
              <div key={lens.id} className="relative">
                {compareMode && (
                  <label className="absolute left-2 top-1/2 -translate-y-1/2 z-10 flex items-center justify-center w-7 h-7 rounded-lg bg-white/90 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-600 shadow-sm cursor-pointer">
                    <input
                      type="checkbox"
                      className="w-4 h-4 accent-indigo-600"
                      checked={isCompareSelected(match)}
                      onChange={() => toggleCompare(match)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </label>
                )}
                <LensCard
                  lens={lens}
                  rank={i + 1}
                  isSelected={selectedMatch?.lens_id === lens.id}
                  onClick={() => setSelectedResult(match)}
                  score={match.score}
                />
              </div>
            ))}
          </div>
          {!showAllResults && displayResults.length > 20 && (
            <button
              onClick={() => setShowAllResults(true)}
              className="mt-2.5 w-full py-2 rounded-lg text-xs font-semibold text-indigo-600 dark:text-indigo-400 bg-indigo-50/60 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors focus-ring"
            >
              显示全部 {displayResults.length} 条结果
            </button>
          )}
        </>
      )}
    </DomainResultsPanel>
  );

  const vizTab = (
    <div className="space-y-4">
      {selectedMatch && (
        <MatchExplanation result={selectedMatch} domain="photography" />
      )}
      {selectedLens ? (
        <>
          <div className="mb-4 rounded-xl overflow-hidden">
            <LensImage
              model={selectedLens.model}
              focal={selectedLens.focal_length_min && selectedLens.focal_length_min !== selectedLens.focal_length_max ? `${selectedLens.focal_length_min}-${selectedLens.focal_length_max}mm` : `${selectedLens.focal_length_mm}mm`}
              aperture={String(selectedLens.max_aperture)}
              brand=""
              imageUrl={selectedLens.image_url}
              size="lg"
            />
          </div>
          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">焦距</p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                {selectedLens.focal_length_min && selectedLens.focal_length_min !== selectedLens.focal_length_max
                  ? `${selectedLens.focal_length_min}-${selectedLens.focal_length_max}mm`
                  : `${selectedLens.focal_length_mm}mm`}
              </p>
            </div>
            <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">最大光圈</p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">f/{selectedLens.max_aperture}</p>
            </div>
            <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">卡口</p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{selectedLens.mount_type}</p>
            </div>
            <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">价格</p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">${selectedLens.price_usd.toFixed(0)}</p>
            </div>
            <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">像圈</p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{selectedLens.image_circle_mm}mm</p>
            </div>
            <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
              <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">类型</p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                {selectedLens.focal_length_min && selectedLens.focal_length_min !== selectedLens.focal_length_max ? "变焦" : "定焦"}
              </p>
            </div>
          </div>
          {selectedMatch?.score_vector && (
            <div className="mt-4">
              <ScoreRadarChart scoreVector={selectedMatch.score_vector} />
            </div>
          )}
          {selectedLens && selectedDet && (
            <>
              <div className="mt-4">
                <SensorCoveragePlot data={coverageData} width={320} height={280} />
              </div>
              <div className="mt-4">
                <MtfCurve data={mtfData} />
              </div>
              <div className="mt-4">
                <CocChart data={cocData} />
              </div>
            </>
          )}
          {compatibleCameras.length > 0 && (
            <div className="mt-4">
              <h3 className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">兼容机身</h3>
              <div className="space-y-2">
                {compatibleCameras.map((cam) => (
                  <div key={cam.id} className="flex items-center justify-between p-3 rounded-[10px] bg-indigo-50/60 dark:bg-indigo-900/30 border border-indigo-100 dark:border-indigo-800/40">
                    <div>
                      <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{cam.model}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{cam.sensor_format_inch} · {cam.sensor_diag_mm}mm · {cam.pixel_size_um}μm/px</p>
                    </div>
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-300">${cam.price_usd.toFixed(0)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <EmptyState
            icon={<Camera size={24} />}
            title="选择镜头"
            description="点击左侧推荐卡片查看镜头规格、兼容机身与评分雷达图"
          />
        </div>
      )}
    </div>
  );

  const traceTab = (
    <div>
      {selectedMatch?.derivation_chain && selectedMatch.derivation_chain.length > 0 ? (
        <PhysicsTrace traces={selectedMatch.derivation_chain} />
      ) : (
        <div className="text-center py-8">
          <EmptyState icon={<Activity size={24} />} title="推导链" description="选择一个匹配方案查看光学计算推导过程" />
        </div>
      )}
    </div>
  );

  const rightPanel = (
    <DomainDetailPanel
      title="镜头详情"
      subtitle="规格、兼容机身与评分"
      icon={<Camera size={16} />}
      activeTab={rightTab}
      onTabChange={setRightTab}
      theme="indigo"
      tabs={[
        { key: "viz", label: "镜头详情", icon: <BarChart3 size={13} /> },
        { key: "trace", label: "推导链", icon: <Activity size={13} /> },
        { key: "knowledge", label: "知识库", icon: <BookOpen size={13} /> },
        { key: "learning", label: "学习指导", icon: <GraduationCap size={13} /> },
      ]}
      viz={vizTab}
      trace={traceTab}
      knowledge={
        <KnowledgePanel
          form={form as unknown as Record<string, number | string>}
          domain="photography"
          activeTab="formulas"
          selectedResult={selectedMatch}
        />
      }
      learning={<PhotographyLearningHub form={form as unknown as Record<string, unknown>} />}
    />
  );

  return (
    <DomainPageShell
      left={leftPanel}
      center={centerPanel}
      right={rightPanel}
    />
  );
}
