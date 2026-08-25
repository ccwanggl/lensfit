import { useState, useMemo, useCallback, useEffect } from "react";
import {
  Microscope,
  Search,
  Ruler,
  Focus,
  Eye,
  Zap,
  Camera,
  DollarSign,
  Info,
  Award,
  BarChart3,
  Activity,
  BookOpen,
  GraduationCap,
} from "lucide-react";
import { Card, Input, SectionHeader, EmptyState, Badge } from "../components/ui";
import { type InputChangeEvent } from "../components/ui/Input";
import LensImage from "../components/LensImage";
import PhysicsTrace from "../components/PhysicsTrace";
import KnowledgePanel from "../components/KnowledgePanel";
import MicroscopeLearningHub from "../components/MicroscopeLearningHub";
import ScoreRadarChart from "../components/ScoreRadarChart";
import MtfCurve from "../components/MtfCurve";
import SensorCoveragePlot from "../components/SensorCoveragePlot";
import ExportActions from "../components/ExportActions";
import MatchExplanation from "../components/MatchExplanation";
import DiagnosticsPanel from "../components/DiagnosticsPanel";
import CompareView from "../components/CompareView";
import CompareParetoToolbar, { computeParetoFrontier } from "../components/CompareParetoToolbar";
import SpecItem from "../components/SpecItem";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import { useParamHint } from "../hooks/useParamHint";
import { toast } from "../hooks/useToast";
import { listLenses, listDetectors } from "../utils/api";
import { generateMtf, generateCoverage, type MtfData, type CoverageData } from "../utils/api";
import type { CatalogLens, CatalogDetector, PresetConfigItem } from "../utils/api";
import { useDomainMatching } from "../stores/matchingStore";
import {
  DomainPageShell,
  DomainFormPanel,
  DomainResultsPanel,
  DomainDetailPanel,
} from "../components/domain";

interface MicroscopeRequest {
  microscope_type: "compound" | "stereo";
  objective_na: number;
  magnification: number;
  wavelength_nm: number;
  sensor_format: string;
  pixel_size_um: number;
  application: string;
  budget_usd: number;
}

const COMPOUND_DEFAULTS: MicroscopeRequest = {
  microscope_type: "compound",
  objective_na: 0.65,
  magnification: 20,
  wavelength_nm: 550,
  sensor_format: "2/3",
  pixel_size_um: 3.45,
  application: "biology",
  budget_usd: 5000,
};

const STEREO_DEFAULTS: MicroscopeRequest = {
  microscope_type: "stereo",
  objective_na: 0.08,
  magnification: 10,
  wavelength_nm: 550,
  sensor_format: "2/3",
  pixel_size_um: 3.45,
  application: "dissection",
  budget_usd: 3000,
};

export default function MicroscopePage() {
  const { hint, expanded } = useParamHint();
  const [form, setForm] = useState<MicroscopeRequest>(COMPOUND_DEFAULTS);

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
  } = useDomainMatching("microscope");

  const { lensMap, detMap } = catalogs;

  const [mtfData, setMtfData] = useState<MtfData | null>(null);
  const [coverageData, setCoverageData] = useState<CoverageData | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareSelection, setCompareSelection] = useState<UnifiedMatchResult[]>([]);
  const [paretoOnly, setParetoOnly] = useState(false);

  const handleMatchSuccess = useCallback((matches: UnifiedMatchResult[]) => {
    setResults(matches);
  }, [setResults]);

  const { isLoading, progress, stage, diagnostics, start } = useMatching({
    domain: "microscope",
    requirements: form,
    onSuccess: handleMatchSuccess,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    setSelectedResult(null);

    try {
      const lensCategory = form.microscope_type === "stereo" ? "microscope_stereo" : "microscope";
      const [lensData, camData] = await Promise.all([
        listLenses({ category: lensCategory, limit: 100 }),
        listDetectors({ category: "microscope", limit: 100 }),
      ]);

      const lm = new Map<number, CatalogLens>();
      for (const l of lensData.items || []) lm.set(l.id, l);

      const dm = new Map<number, CatalogDetector>();
      for (const d of camData.items || []) dm.set(d.id, d);

      setCatalogs({ lensMap: lm, detMap: dm });

      start();
    } catch (e) {
      console.error("Load microscope data failed:", e);
      toast("error", "数据加载失败", "无法获取显微镜头数据");
    }
  };

  const enrichedResults = useMemo(() => {
    return results
      .map((r) => ({
        match: r,
        lens: lensMap.get(r.lens_id),
        det: detMap.get(r.detector_id),
      }))
      .filter((item): item is { match: UnifiedMatchResult; lens: CatalogLens; det: CatalogDetector } =>
        !!item.lens && !!item.det
      );
  }, [results, lensMap, detMap]);

  const nyquistStatus = (ratio: number) => {
    if (ratio >= 2) return { label: "过采样", color: "green" };
    if (ratio >= 1) return { label: "理想", color: "blue" };
    if (ratio >= 0.5) return { label: "欠采样", color: "orange" };
    return { label: "严重欠采样", color: "red" };
  };

  const selectedLens = selectedMatch ? lensMap.get(selectedMatch.lens_id) : undefined;
  const selectedDet = selectedMatch ? detMap.get(selectedMatch.detector_id) : undefined;
  const selectedDerived = selectedMatch?.derived as Record<string, unknown> | undefined;

  const paretoResults = useMemo(() => computeParetoFrontier(enrichedResults.map((e) => e.match)), [enrichedResults]);
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
      setCoverageData(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const [mtf, coverage] = await Promise.all([
          generateMtf(selectedLens.id, selectedDet.id),
          generateCoverage(selectedLens.id, selectedDet.id),
        ]);
        if (!cancelled) {
          setMtfData(mtf);
          setCoverageData(coverage);
        }
      } catch {
        if (!cancelled) {
          setMtfData(null);
          setCoverageData(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedMatch, selectedLens, selectedDet]);

  const leftPanel = (
    <div className="space-y-4">
      <DomainFormPanel
        title="显微镜参数"
        subtitle="配置显微成像系统需求"
        icon={<Microscope size={16} />}
        domain="microscope"
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
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">显微镜类型</p>
          <Input
            as="select"
            label="类型"
            icon={<Microscope size={14} />}
            layout="horizontal"
            learnHint={hint("microscope_type")} hintExpanded={expanded}
            value={form.microscope_type}
            onChange={(e: InputChangeEvent) => {
              const newType = e.target.value as "compound" | "stereo";
              setForm(newType === "stereo" ? STEREO_DEFAULTS : COMPOUND_DEFAULTS);
              setSelectedResult(null);
              setHasSearched(false);
            }}
          >
            <option value="compound">复式显微镜（高倍、短WD）</option>
            <option value="stereo">体视显微镜（低倍、长WD、三维）</option>
          </Input>

          {form.microscope_type === "compound" ? (
            <>
              <Input
                type="number"
                step="0.01"
                label="数值孔径"
                icon={<Focus size={14} />}
                layout="horizontal"
                learnHint={hint("objective_na")} hintExpanded={expanded}
                value={form.objective_na}
                onChange={(e: InputChangeEvent) => setForm({ ...form, objective_na: parseFloat(e.target.value) || 0 })}
              />
              <Input
                type="number"
                label="放大倍率"
                icon={<Eye size={14} />}
                layout="horizontal"
                learnHint={hint("magnification")} hintExpanded={expanded}
                value={form.magnification}
                onChange={(e: InputChangeEvent) => setForm({ ...form, magnification: parseFloat(e.target.value) || 0 })}
              />
            </>
          ) : (
            <>
              <Input
                type="number"
                step="0.01"
                label="变焦下限"
                icon={<Eye size={14} />}
                layout="horizontal"
                unit="×"
                learnHint={hint("magnification")} hintExpanded={expanded}
                value={form.magnification}
                onChange={(e: InputChangeEvent) => setForm({ ...form, magnification: parseFloat(e.target.value) || 0 })}
              />
              <Input
                type="number"
                step="0.01"
                label="数值孔径"
                icon={<Focus size={14} />}
                layout="horizontal"
                learnHint={hint("objective_na")} hintExpanded={expanded}
                value={form.objective_na}
                onChange={(e: InputChangeEvent) => setForm({ ...form, objective_na: parseFloat(e.target.value) || 0 })}
              />
            </>
          )}
        </div>

        <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">光学参数</p>
          <Input
            type="number"
            label="照明波长"
            icon={<Ruler size={14} />}
            unit="nm"
            layout="horizontal"
            learnHint={hint("wavelength_nm")} hintExpanded={expanded}
            value={form.wavelength_nm}
            onChange={(e: InputChangeEvent) => setForm({ ...form, wavelength_nm: parseFloat(e.target.value) || 0 })}
          />
          <Input
            as="select"
            label="传感器"
            icon={<Camera size={14} />}
            layout="horizontal"
            learnHint={hint("sensor_format")} hintExpanded={expanded}
            value={form.sensor_format}
            onChange={(e: InputChangeEvent) => setForm({ ...form, sensor_format: e.target.value })}
          >
            <option value="1/3">1/3&quot;</option>
            <option value="1/2.5">1/2.5&quot;</option>
            <option value="1/2">1/2&quot;</option>
            <option value="2/3">2/3&quot;</option>
            <option value="1">1&quot;</option>
          </Input>
          <Input
            type="number"
            step="0.01"
            label="像元尺寸"
            icon={<Ruler size={14} />}
            unit="μm"
            layout="horizontal"
            learnHint={hint("pixel_size_um")} hintExpanded={expanded}
            value={form.pixel_size_um}
            onChange={(e: InputChangeEvent) => setForm({ ...form, pixel_size_um: parseFloat(e.target.value) || 0 })}
          />
        </div>

        <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">应用与预算</p>
          <Input
            as="select"
            label="应用场景"
            icon={<Zap size={14} />}
            layout="horizontal"
            learnHint={hint("application")} hintExpanded={expanded}
            value={form.application}
            onChange={(e: InputChangeEvent) => setForm({ ...form, application: e.target.value })}
          >
            {form.microscope_type === "compound" ? (
              <>
                <option value="biology">生物/生命科学</option>
                <option value="materials">材料/金相分析</option>
                <option value="semiconductor">半导体检测</option>
                <option value="fluorescence">荧光成像</option>
              </>
            ) : (
              <>
                <option value="dissection">解剖/手术</option>
                <option value="inspection">工业检测</option>
                <option value="biology">生物观察</option>
                <option value="materials">材料分析</option>
              </>
            )}
          </Input>
          <Input
            type="number"
            label="预算上限"
            icon={<DollarSign size={14} />}
            unit="USD"
            layout="horizontal"
            learnHint={hint("budget_usd")} hintExpanded={expanded}
            value={form.budget_usd}
            onChange={(e: InputChangeEvent) => setForm({ ...form, budget_usd: parseFloat(e.target.value) || 0 })}
          />
        </div>
      </DomainFormPanel>

      <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 border-indigo-100 dark:border-indigo-800/40">
        <SectionHeader title="光学公式" subtitle="关键计算参考" icon={<Info size={14} />} />
        <div className="mt-3 space-y-2 text-xs text-slate-600 dark:text-slate-400">
          {form.microscope_type === "stereo" && (
            <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
              <span className="font-semibold text-indigo-700 dark:text-indigo-300">总放大倍率</span>
              <code className="block mt-0.5 text-slate-500 dark:text-slate-400">总放大 = 变焦倍率 × 10×目镜</code>
            </div>
          )}
          <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
            <span className="font-semibold text-indigo-700 dark:text-indigo-300">瑞利分辨率</span>
            <code className="block mt-0.5 text-slate-500 dark:text-slate-400">d = 0.61 × λ / NA</code>
          </div>
          <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
            <span className="font-semibold text-indigo-700 dark:text-indigo-300">数字分辨率</span>
            <code className="block mt-0.5 text-slate-500 dark:text-slate-400">d = 像素尺寸 / 放大倍率</code>
          </div>
          <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
            <span className="font-semibold text-indigo-700 dark:text-indigo-300">奈奎斯特采样</span>
            <code className="block mt-0.5 text-slate-500 dark:text-slate-400">光学分辨率 / 数字分辨率 ≥ 2</code>
          </div>
        </div>
      </Card>
    </div>
  );

  const centerPanel = (
    <DomainResultsPanel
      title={compareMode ? "方案对比" : "匹配结果"}
      subtitle={`${displayResults.length} 组物镜-相机组合${paretoOnly ? "（Pareto 前沿）" : ""}`}
      icon={<Microscope size={16} />}
      headerBorder
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
              requirements={form}
              results={results}
              disabled={results.length === 0}
            />
          </div>
        ) : undefined
      }
    >
      {!hasSearched ? (
        <div className="flex-1 flex items-center justify-center h-64">
          <EmptyState
            icon={<Microscope size={24} />}
            title="等待匹配"
            description="设置左侧参数并点击「自动匹配」，系统将推荐最优的显微镜物镜与相机组合"
          />
        </div>
      ) : displayResults.length === 0 ? (
        <div className="flex-1 flex items-center justify-center h-auto min-h-[16rem]">
          {!isLoading && diagnostics && diagnostics.length > 0 ? (
            <DiagnosticsPanel
              diagnostics={diagnostics}
              onAdjustParam={(name, value) => {
                setForm((prev) => ({ ...prev, [name]: value as number | string }));
                toast("info", "参数已调整", `${name} 已设为 ${String(value)}，请重新匹配`);
              }}
            />
          ) : (
            <EmptyState
              icon={<Search size={24} />}
              title={isLoading ? "计算中..." : "无匹配结果"}
              description={isLoading ? "后端正在执行光学计算与评分..." : "请放宽预算或调整参数后重试"}
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
          <div className="space-y-2.5">
            {displayResults.map(({ match, lens, det }, idx) => (
              <div key={`${match.lens_id}-${match.detector_id}`} className="relative">
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
                <button
                  onClick={() => setSelectedResult(match)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                    selectedMatch?.lens_id === match.lens_id && selectedMatch?.detector_id === match.detector_id
                      ? "border-indigo-300 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/30 shadow-sm"
                      : "border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-200 hover:shadow-sm"
                  } ${compareMode ? "pl-12" : ""}`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
                      idx === 0 ? "bg-gradient-to-br from-amber-400 to-amber-500 text-white" :
                      idx === 1 ? "bg-gradient-to-br from-slate-300 to-slate-400 text-white" :
                      idx === 2 ? "bg-gradient-to-br from-orange-300 to-orange-400 text-white" :
                      "bg-slate-100 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400"
                    }`}>{idx + 1}</span>

                    <LensImage
                      model={lens.model}
                      focal={`${lens.focal_length_mm}x`}
                      aperture={lens.na ? String(lens.na) : "N/A"}
                      brand=""
                      imageUrl={lens.image_url}
                      size="sm"
                    />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-0.5">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">{lens.model}</h4>
                        <span className="text-base font-extrabold text-indigo-600 dark:text-indigo-400 tabular-nums">{match.score.toFixed(2)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                        {form.microscope_type === "stereo" ? (
                          <span>{lens.focal_length_mm}x-{lens.focal_length_max || lens.focal_length_mm}x 变焦</span>
                        ) : (
                          <span>NA {lens.na}</span>
                        )}
                        <span>·</span>
                        <span>{det.model}</span>
                        <span>·</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300">${(lens.price_usd + det.price_usd).toFixed(0)}</span>
                      </div>
                    </div>
                  </div>
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </DomainResultsPanel>
  );

  const vizTab = (
    <div className="space-y-4">
      {selectedMatch && (
        <MatchExplanation result={selectedMatch} domain="microscope" />
      )}
      {!selectedMatch || !selectedLens || !selectedDet ? (
        <div className="flex-1 flex items-center justify-center h-64">
          <EmptyState
            icon={<Info size={24} />}
            title="选择方案"
            description="点击左侧匹配结果查看详细参数分析"
          />
        </div>
      ) : (
        <>
          <div className="rounded-xl overflow-hidden">
            <LensImage
              model={selectedLens.model}
              focal={`${selectedLens.focal_length_mm}x`}
              aperture={selectedLens.na ? String(selectedLens.na) : "N/A"}
              brand=""
              imageUrl={selectedLens.image_url}
              size="lg"
            />
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 border border-indigo-100 dark:border-indigo-800/40">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">匹配得分</span>
              <span className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">{selectedMatch.score.toFixed(2)}</span>
            </div>
            <div className="w-full h-2 bg-white dark:bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all"
                style={{ width: `${Math.min(selectedMatch.score * 100, 100)}%` }}
              />
            </div>
          </div>

          {selectedMatch?.score_vector && (
            <ScoreRadarChart scoreVector={selectedMatch.score_vector} />
          )}

          {selectedLens && selectedDet && (
            <div className="mt-4">
              <SensorCoveragePlot data={coverageData} width={320} height={280} />
            </div>
          )}

          {selectedLens && selectedDet && (
            <div className="mt-4">
              <MtfCurve data={mtfData} />
            </div>
          )}

          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
              <Focus size={14} className="text-indigo-500" />
              {form.microscope_type === "stereo" ? "变焦主体参数" : "物镜参数"}
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <SpecItem label="型号" value={selectedLens.model} />
              {form.microscope_type === "stereo" ? (
                <>
                  <SpecItem label="变焦范围" value={`${selectedLens.focal_length_mm}x-${selectedLens.focal_length_max || selectedLens.focal_length_mm}x`} />
                  <SpecItem label="总放大倍率" value={`${(selectedDerived?.total_magnification as number)?.toFixed(1) ?? "N/A"}× (含10×目镜)`} />
                  <SpecItem label="工作距离" value={selectedLens.nominal_wd_mm ? `${selectedLens.nominal_wd_mm}mm` : "N/A"} />
                </>
              ) : (
                <>
                  <SpecItem label="放大倍率" value={`${selectedLens.focal_length_mm}×`} />
                  <SpecItem label="数值孔径" value={selectedLens.na?.toFixed(2) || "N/A"} />
                </>
              )}
              <SpecItem label="像场数" value={`${selectedLens.image_circle_mm}mm`} />
              <SpecItem label="接口" value={selectedLens.mount_type || "N/A"} />
              <SpecItem label="价格" value={`$${selectedLens.price_usd.toFixed(0)}`} />
            </div>
          </div>

          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
              <Camera size={14} className="text-indigo-500" />
              相机参数
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <SpecItem label="型号" value={selectedDet.model} />
              <SpecItem label="传感器" value={selectedDet.sensor_format_inch || "N/A"} />
              <SpecItem label="分辨率" value={`${selectedDet.resolution_w ?? "?"}×${selectedDet.resolution_h ?? "?"}`} />
              <SpecItem label="像元尺寸" value={`${selectedDet.pixel_size_um}μm`} />
              <SpecItem label="接口" value={selectedDet.mount_type || "N/A"} />
              <SpecItem label="价格" value={`$${selectedDet.price_usd.toFixed(0)}`} />
            </div>
          </div>

          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
              <Zap size={14} className="text-indigo-500" />
              光学分析
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <SpecItem
                label="光学分辨率"
                value={`${(selectedDerived?.optical_resolution_um as number)?.toFixed(3) ?? "N/A"}μm`}
                helper={`瑞利判据: 0.61×${form.wavelength_nm}nm/${selectedLens.na?.toFixed(2)}`}
              />
              <SpecItem
                label="数字分辨率"
                value={`${(selectedDerived?.digital_resolution_um as number)?.toFixed(3) ?? "N/A"}μm`}
                helper="像素尺寸/放大倍率"
              />
              <div className="col-span-2">
                <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">奈奎斯特采样比</p>
                      <p className={`text-sm font-bold ${
                        (selectedDerived?.nyquist_ratio as number) >= 2 ? "text-green-600 dark:text-green-400" :
                        (selectedDerived?.nyquist_ratio as number) >= 1 ? "text-blue-600 dark:text-blue-400" :
                        "text-orange-500"
                      }`}>
                        {((selectedDerived?.nyquist_ratio as number) ?? 0).toFixed(2)}
                      </p>
                    </div>
                    <Badge
                      variant={
                        (selectedDerived?.nyquist_ratio as number) >= 2 ? "success" :
                        (selectedDerived?.nyquist_ratio as number) >= 1 ? "info" : "warning"
                      }
                    >
                      {nyquistStatus((selectedDerived?.nyquist_ratio as number) ?? 0).label}
                    </Badge>
                  </div>
                  <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full mt-2">
                    <div
                      className={`h-full rounded-full transition-all ${
                        (selectedDerived?.nyquist_ratio as number) >= 2 ? "bg-green-500" :
                        (selectedDerived?.nyquist_ratio as number) >= 1 ? "bg-blue-500" : "bg-orange-400"
                      }`}
                      style={{ width: `${Math.min(((selectedDerived?.nyquist_ratio as number) ?? 0) / 3 * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
              <SpecItem label="总放大倍率" value={`${(selectedDerived?.total_magnification as number)?.toFixed(1) ?? "N/A"}×`} />
              <SpecItem label="视场大小" value={`${(selectedDerived?.fov_w_mm as number)?.toFixed(3) ?? "N/A"}×${(selectedDerived?.fov_h_mm as number)?.toFixed(3) ?? "N/A"}mm`} />
              <SpecItem label="组合总价" value={`$${(selectedLens.price_usd + selectedDet.price_usd).toFixed(0)}`} highlight />
            </div>
          </div>
        </>
      )}
    </div>
  );

  const traceTab = (
    <div>
      {selectedMatch?.derivation_chain && selectedMatch.derivation_chain.length > 0 ? (
        <PhysicsTrace traces={selectedMatch.derivation_chain} />
      ) : (
        <div className="text-center py-6">
          <EmptyState icon={<Activity size={24} />} title="推导链" description="选择一个匹配方案查看光学计算推导过程" />
        </div>
      )}
    </div>
  );

  const rightPanel = (
    <DomainDetailPanel
      title="方案分析"
      subtitle="物镜-相机组合参数与学习指导"
      icon={<Award size={16} />}
      activeTab={rightTab}
      onTabChange={setRightTab}
      theme="indigo"
      tabs={[
        { key: "viz", label: "方案详情", icon: <BarChart3 size={13} /> },
        { key: "trace", label: "推导链", icon: <Activity size={13} /> },
        { key: "knowledge", label: "知识库", icon: <BookOpen size={13} /> },
        { key: "learning", label: "学习指导", icon: <GraduationCap size={13} /> },
      ]}
      viz={vizTab}
      trace={traceTab}
      knowledge={
        <KnowledgePanel
          form={form as unknown as Record<string, number | string>}
          domain="microscope"
          activeTab="formulas"
          selectedResult={selectedMatch}
        />
      }
      learning={<MicroscopeLearningHub form={form as unknown as Record<string, unknown>} />}
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
