import { useState, useMemo, useCallback, useEffect } from "react";
import {
  Sun,
  Search,
  Thermometer,
  Waves,
  Ruler,
  Eye,
  DollarSign,
  Info,
  Award,
  Radio,
  Crosshair,
  Focus,
  Gauge,
  Zap,
  BarChart3,
  Activity,
  BookOpen,
  GraduationCap,
} from "lucide-react";
import { Card, Input, SectionHeader, EmptyState } from "../components/ui";
import { type InputChangeEvent } from "../components/ui/Input";
import LensImage from "../components/LensImage";
import SaveToProjectButton from "../components/SaveToProjectButton";
import SpecItem from "../components/SpecItem";
import ResultCard from "../components/ResultCard";
import PhysicsTrace from "../components/PhysicsTrace";
import KnowledgePanel from "../components/KnowledgePanel";
import InfraredLearningHub from "../components/InfraredLearningHub";
import ScoreRadarChart from "../components/ScoreRadarChart";
import MtfCurve from "../components/MtfCurve";
import ExportActions from "../components/ExportActions";
import MatchExplanation from "../components/MatchExplanation";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import { useParamHint } from "../hooks/useParamHint";
import { toast } from "../hooks/useToast";
import { listLenses, listDetectors } from "../utils/api";
import { generateMtf, type MtfData } from "../utils/api";
import type { CatalogLens, CatalogDetector, PresetConfigItem } from "../utils/api";
import { useDomainMatching } from "../stores/matchingStore";
import {
  DomainPageShell,
  DomainFormPanel,
  DomainResultsPanel,
  DomainDetailPanel,
} from "../components/domain";

interface IRRequest {
  band: string;
  wavelength_um: number;
  fov_deg: number;
  working_distance_m: number;
  target_resolution_m: number;
  sensor_format: string;
  pixel_size_um: number;
  budget_usd: number;
}

const BANDS = [
  { value: "swir", label: "短波红外 (SWIR 0.9-2.5μm)", min: 0.9, max: 2.5 },
  { value: "mwir", label: "中波红外 (MWIR 3-5μm)", min: 3, max: 5 },
  { value: "lwir", label: "长波红外 (LWIR 8-14μm)", min: 8, max: 14 },
  { value: "any", label: "任意波段", min: 0.5, max: 20 },
];

const DEFAULTS: IRRequest = {
  band: "lwir",
  wavelength_um: 10.0,
  fov_deg: 24,
  working_distance_m: 10.0,
  target_resolution_m: 0.5,
  sensor_format: "1/2",
  pixel_size_um: 12.0,
  budget_usd: 5000,
};

function getBandLabel(_min: number, max: number): string {
  if (max <= 2.5) return "SWIR";
  if (max <= 5) return "MWIR";
  return "LWIR";
}

export default function InfraredPage() {
  const { hint, expanded } = useParamHint();
  const [form, setForm] = useState<IRRequest>(DEFAULTS);

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
  } = useDomainMatching("infrared");

  const { lensMap, detMap } = catalogs;

  const [mtfData, setMtfData] = useState<MtfData | null>(null);

  const handleMatchSuccess = useCallback((matches: UnifiedMatchResult[]) => {
    setResults(matches);
  }, [setResults]);

  const { isLoading, progress, stage, start } = useMatching({
    domain: "infrared",
    requirements: form,
    onSuccess: handleMatchSuccess,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    setSelectedResult(null);

    try {
      const [lensData, detData] = await Promise.all([
        listLenses({ category: "infrared", limit: 100 }),
        listDetectors({ category: "infrared", limit: 100 }),
      ]);

      const lm = new Map<number, CatalogLens>();
      for (const l of lensData.items || []) lm.set(l.id, l);

      const dm = new Map<number, CatalogDetector>();
      for (const d of detData.items || []) dm.set(d.id, d);

      setCatalogs({ lensMap: lm, detMap: dm });

      start();
    } catch (e) {
      console.error("Load infrared data failed:", e);
      toast("error", "数据加载失败", "无法获取红外镜头数据");
    }
  };

  const handleBandChange = (bandValue: string) => {
    const band = BANDS.find((b) => b.value === bandValue);
    if (band) {
      const midWavelength = (band.min + band.max) / 2;
      setForm((prev) => ({ ...prev, band: bandValue, wavelength_um: midWavelength }));
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

  const selectedLens = selectedMatch ? lensMap.get(selectedMatch.lens_id) : undefined;
  const selectedDet = selectedMatch ? detMap.get(selectedMatch.detector_id) : undefined;
  const selectedDerived = selectedMatch?.derived as Record<string, unknown> | undefined;
  const selectedBand = BANDS.find((b) => b.value === form.band);

  useEffect(() => {
    if (!selectedMatch || !selectedLens || !selectedDet) {
      setMtfData(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const mtf = await generateMtf(selectedLens.id, selectedDet.id);
        if (!cancelled) setMtfData(mtf);
      } catch {
        if (!cancelled) setMtfData(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedMatch, selectedLens, selectedDet]);

  const leftPanel = (
    <div className="space-y-4">
      <DomainFormPanel
        title="红外参数"
        subtitle="配置红外成像系统需求"
        icon={<Sun size={16} />}
        domain="infrared"
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
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">波段与波长</p>
          <Input
            as="select"
            label="工作波段"
            icon={<Radio size={14} />}
            layout="horizontal"
            learnHint={hint("band")} hintExpanded={expanded}
            value={form.band}
            onChange={(e: InputChangeEvent) => handleBandChange(e.target.value)}
          >
            {BANDS.map((b) => (
              <option key={b.value} value={b.value}>
                {b.label}
              </option>
            ))}
          </Input>

          <Input
            type="number"
            step="0.1"
            label="目标波长"
            icon={<Waves size={14} />}
            unit={`μm (${selectedBand?.min}-${selectedBand?.max})`}
            layout="horizontal"
            learnHint={hint("wavelength_um")} hintExpanded={expanded}
            value={form.wavelength_um}
            onChange={(e: InputChangeEvent) => setForm({ ...form, wavelength_um: parseFloat(e.target.value) || 0 })}
          />
        </div>

        <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">光学条件</p>
          <Input
            type="number"
            step="0.1"
            label="视场角"
            icon={<Eye size={14} />}
            unit="°"
            layout="horizontal"
            learnHint={hint("fov_deg")} hintExpanded={expanded}
            value={form.fov_deg}
            onChange={(e: InputChangeEvent) => setForm({ ...form, fov_deg: parseFloat(e.target.value) || 0 })}
          />

          <Input
            type="number"
            step="0.1"
            label="工作距离"
            icon={<Ruler size={14} />}
            unit="m"
            layout="horizontal"
            learnHint={hint("working_distance_m")} hintExpanded={expanded}
            value={form.working_distance_m}
            onChange={(e: InputChangeEvent) => setForm({ ...form, working_distance_m: parseFloat(e.target.value) || 0 })}
          />

          <Input
            type="number"
            step="0.001"
            label="分辨率"
            icon={<Crosshair size={14} />}
            unit="m"
            layout="horizontal"
            learnHint={hint("target_resolution_m")} hintExpanded={expanded}
            value={form.target_resolution_m}
            onChange={(e: InputChangeEvent) =>
              setForm({ ...form, target_resolution_m: parseFloat(e.target.value) || 0 })
            }
          />
        </div>

        <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">传感器</p>
          <Input
            as="select"
            label="传感器尺寸"
            icon={<Focus size={14} />}
            layout="horizontal"
            learnHint={hint("sensor_format")} hintExpanded={expanded}
            value={form.sensor_format}
            onChange={(e: InputChangeEvent) => setForm({ ...form, sensor_format: e.target.value })}
          >
            <option value="1/4">1/4&quot;</option>
            <option value="1/3">1/3&quot;</option>
            <option value="1/2">1/2&quot;</option>
            <option value="2/3">2/3&quot;</option>
            <option value="1">1&quot;</option>
          </Input>

          <Input
            type="number"
            step="0.1"
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
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">预算</p>
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

      <Card className="bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/30 dark:to-amber-900/30 border-orange-100 dark:border-orange-800/40">
        <SectionHeader title="红外公式" subtitle="关键计算参考" icon={<Info size={14} />} />
        <div className="mt-3 space-y-2 text-xs text-slate-600 dark:text-slate-400">
          <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
            <span className="font-semibold text-orange-700 dark:text-orange-300">瞬时视场角 (IFOV)</span>
            <code className="block mt-0.5 text-slate-500 dark:text-slate-400">IFOV = 像元尺寸 / 焦距 (mrad)</code>
          </div>
          <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
            <span className="font-semibold text-orange-700 dark:text-orange-300">空间分辨率</span>
            <code className="block mt-0.5 text-slate-500 dark:text-slate-400">SR = IFOV × 工作距离 (m)</code>
          </div>
          <div className="p-2 rounded-lg bg-white/60 dark:bg-slate-800/40">
            <span className="font-semibold text-orange-700 dark:text-orange-300">视场角 (FOV)</span>
            <code className="block mt-0.5 text-slate-500 dark:text-slate-400">FOV = 2×arctan(传感器/2f)</code>
          </div>
        </div>
      </Card>
    </div>
  );

  const centerPanel = (
    <DomainResultsPanel
      title="匹配结果"
      subtitle={`${enrichedResults.length} 组镜头-探测器组合`}
      icon={<Thermometer size={16} />}
      headerBorder
      action={
        hasSearched ? (
          <ExportActions
            requirements={form}
            results={results}
            disabled={results.length === 0}
          />
        ) : undefined
      }
    >
      {!hasSearched ? (
        <div className="flex-1 flex items-center justify-center h-64">
          <EmptyState
            icon={<Sun size={24} />}
            title="等待匹配"
            description="设置左侧红外参数并点击「自动匹配」，系统将推荐最优的红外镜头与探测器组合"
          />
        </div>
      ) : enrichedResults.length === 0 ? (
        <div className="flex-1 flex items-center justify-center h-64">
          <EmptyState
            icon={<Search size={24} />}
            title={isLoading ? "计算中..." : "无匹配结果"}
            description={isLoading ? "后端正在执行光学计算与评分..." : "请放宽预算、调整波段或视场要求后重试"}
          />
        </div>
      ) : (
        enrichedResults.map(({ match, lens, det }, idx) => {
          const d = match.derived as Record<string, unknown>;
          const focalRange = d.focal_range as string | undefined;
          const fNumber = d.f_number as number | undefined;
          const bandLabel = getBandLabel(
            (lens.wavelength_min_nm ?? 0) / 1000,
            (lens.wavelength_max_nm ?? 0) / 1000
          );
          return (
            <ResultCard
              key={`${match.lens_id}-${match.detector_id}`}
              rank={idx + 1}
              isSelected={selectedMatch?.lens_id === match.lens_id && selectedMatch?.detector_id === match.detector_id}
              onClick={() => setSelectedResult(match)}
              lensModel={lens.model}
              lensFocal={focalRange || `${lens.focal_length_mm}mm`}
              lensAperture={fNumber != null ? String(fNumber) : String(lens.max_aperture)}
              lensImageUrl={lens.image_url}
              detectorModel={det.model}
              badgeLabel={bandLabel}
              price={lens.price_usd + det.price_usd}
              score={match.score}
              reasons={[]}
            />
          );
        })
      )}
    </DomainResultsPanel>
  );

  const vizTab = (
    <div className="space-y-5">
      {selectedMatch && (
        <MatchExplanation result={selectedMatch} domain="infrared" />
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
              focal={(selectedDerived?.focal_range as string) || `${selectedLens.focal_length_mm}mm`}
              aperture={String(selectedDerived?.f_number as number | undefined ?? selectedLens.max_aperture)}
              brand=""
              imageUrl={selectedLens.image_url}
              size="lg"
            />
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/30 dark:to-amber-900/30 border border-orange-100 dark:border-orange-800/40">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">匹配得分</span>
              <span className="text-2xl font-extrabold text-orange-600">
                {selectedMatch.score.toFixed(2)}
              </span>
            </div>
            <div className="w-full h-2 bg-white dark:bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-orange-500 to-amber-500 transition-all"
                style={{ width: `${Math.min(selectedMatch.score * 100, 100)}%` }}
              />
            </div>
          </div>

          {selectedMatch?.score_vector && (
            <ScoreRadarChart scoreVector={selectedMatch.score_vector} />
          )}

          {selectedLens && selectedDet && (
            <div className="mt-4">
              <MtfCurve data={mtfData} />
            </div>
          )}

          <div className="flex items-center justify-end">
            <SaveToProjectButton
              lensId={selectedMatch.lens_id}
              detectorId={selectedMatch.detector_id}
              lensModel={selectedLens.model}
              detectorModel={selectedDet.model}
            />
          </div>

          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
              <Focus size={14} className="text-orange-500" />
              红外镜头参数
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <SpecItem label="型号" value={selectedLens.model} />
              <SpecItem
                label="焦距"
                value={(selectedDerived?.focal_range as string) || `${selectedLens.focal_length_mm}mm`}
              />
              <SpecItem label="F数" value={`F/${(selectedDerived?.f_number as number | undefined ?? selectedLens.max_aperture).toFixed(1)}`} />
              <SpecItem label="波段" value={getBandLabel((selectedLens.wavelength_min_nm ?? 0) / 1000, (selectedLens.wavelength_max_nm ?? 0) / 1000)} />
              <SpecItem
                label="波长范围"
                value={`${((selectedLens.wavelength_min_nm ?? 0) / 1000).toFixed(1)}-${((selectedLens.wavelength_max_nm ?? 0) / 1000).toFixed(1)}μm`}
              />
              <SpecItem label="接口" value={selectedLens.mount_type || "N/A"} />
              <SpecItem label="像面" value={`${selectedLens.image_circle_mm}mm`} />
              <SpecItem label="价格" value={`$${selectedLens.price_usd.toFixed(0)}`} />
            </div>
          </div>

          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
              <Gauge size={14} className="text-orange-500" />
              探测器参数
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <SpecItem label="型号" value={selectedDet.model} />
              <SpecItem label="传感器" value={selectedDet.sensor_format_inch || "N/A"} />
              <SpecItem
                label="分辨率"
                value={`${selectedDet.resolution_w ?? "?"}×${selectedDet.resolution_h ?? "?"}`}
              />
              <SpecItem label="像元尺寸" value={`${selectedDet.pixel_size_um}μm`} />
              <SpecItem label="NETD" value={`${(selectedDet.netd_mk ?? 0).toFixed(0)}mK`} />
              <SpecItem
                label="光谱范围"
                value={`${selectedDet.spectral_range_min_um}-${selectedDet.spectral_range_max_um}μm`}
              />
              <SpecItem label="接口" value={selectedDet.mount_type || "N/A"} />
              <SpecItem label="价格" value={`$${selectedDet.price_usd.toFixed(0)}`} />
            </div>
          </div>

          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-1.5">
              <Zap size={14} className="text-orange-500" />
              系统性能
            </h4>
            <div className="grid grid-cols-2 gap-2">
              <SpecItem label="IFOV" value={`${(selectedDerived?.ifov_mrad as number)?.toFixed(3) ?? "N/A"} mrad`} />
              <SpecItem
                label="空间分辨率"
                value={`${(selectedDerived?.spatial_resolution_m as number)?.toFixed(3) ?? "N/A"}m`}
                helper={`@ ${form.working_distance_m}m 工作距离`}
              />
              <SpecItem label="水平FOV" value={`${(selectedDerived?.fov_w_deg as number)?.toFixed(1) ?? "N/A"}°`} />
              <SpecItem label="垂直FOV" value={`${(selectedDerived?.fov_h_deg as number)?.toFixed(1) ?? "N/A"}°`} />
              <SpecItem label="对角FOV" value={`${(selectedDerived?.fov_diag_deg as number)?.toFixed(1) ?? "N/A"}°`} />
              <SpecItem
                label="波段重叠率"
                value={`${(((selectedDerived?.band_overlap_ratio as number) ?? 0) * 100).toFixed(0)}%`}
              />
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
        <div className="text-center py-8">
          <EmptyState icon={<Activity size={24} />} title="推导链" description="选择一个匹配方案查看光学计算推导过程" />
        </div>
      )}
    </div>
  );

  const rightPanel = (
    <DomainDetailPanel
      title="方案分析"
      subtitle="红外系统参数与学习指导"
      icon={<Award size={16} />}
      activeTab={rightTab}
      onTabChange={setRightTab}
      theme="orange"
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
          domain="infrared"
          activeTab="formulas"
          selectedResult={selectedMatch}
        />
      }
      learning={<InfraredLearningHub form={form as unknown as Record<string, unknown>} />}
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
