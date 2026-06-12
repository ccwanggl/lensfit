import { useState, useMemo } from "react";
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
} from "lucide-react";
import { Card, Button, Input, SectionHeader, EmptyState } from "../components/ui";
import { type InputChangeEvent } from "../components/ui/Input";
import LensImage from "../components/LensImage";
import PresetSelector from "../components/PresetSelector";
import SaveToProjectButton from "../components/SaveToProjectButton";
import SpecItem from "../components/SpecItem";
import ResultCard from "../components/ResultCard";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import { useParamHint } from "../hooks/useParamHint";
import { listLenses, listDetectors } from "../utils/api";
import type { CatalogLens, CatalogDetector, PresetConfigItem } from "../utils/api";

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
  const hint = useParamHint();
  const [form, setForm] = useState<IRRequest>(DEFAULTS);
  const [lensMap, setLensMap] = useState<Map<number, CatalogLens>>(new Map());
  const [detMap, setDetMap] = useState<Map<number, CatalogDetector>>(new Map());
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<UnifiedMatchResult | null>(null);

  const { results, isLoading, progress, stage, start } = useMatching({
    domain: "infrared",
    requirements: form,
    onSuccess: (matches) => {
      setSelectedMatch(matches[0] ?? null);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    setSelectedMatch(null);

    const [lensData, detData] = await Promise.all([
      listLenses({ category: "infrared", limit: 100 }),
      listDetectors({ category: "infrared", limit: 100 }),
    ]);

    const lm = new Map<number, CatalogLens>();
    for (const l of lensData.items || []) lm.set(l.id, l);
    setLensMap(lm);

    const dm = new Map<number, CatalogDetector>();
    for (const d of detData.items || []) dm.set(d.id, d);
    setDetMap(dm);

    start();
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

  return (
    <div className="grid grid-cols-12 gap-5">
      {/* ── Left: Parameters ── */}
      <div className="col-span-3 space-y-4">
        <Card padding="none" className="overflow-hidden">
          <div className="p-6">
            <SectionHeader
              title="红外参数"
              subtitle="配置红外成像系统需求"
              icon={<Sun size={16} />}
            />
            <div className="mb-3">
              <PresetSelector
                domain="infrared"
                onSelect={(preset: PresetConfigItem) => {
                  setForm((prev) => ({ ...prev, ...preset.params }));
                }}
              />
            </div>

            <form onSubmit={handleSubmit} className="space-y-2 mt-4">
              <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
                <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">波段与波长</p>
                <Input
                  as="select"
                  label="工作波段"
                  icon={<Radio size={14} />}
                  layout="horizontal"
                  learnHint={hint("band")}
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
                  learnHint={hint("wavelength_um")}
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
                  learnHint={hint("fov_deg")}
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
                  learnHint={hint("working_distance_m")}
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
                  learnHint={hint("target_resolution_m")}
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
                  learnHint={hint("sensor_format")}
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
                  learnHint={hint("pixel_size_um")}
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
                  learnHint={hint("budget_usd")}
                  value={form.budget_usd}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, budget_usd: parseFloat(e.target.value) || 0 })}
                />
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  leftIcon={<Search size={16} />}
                  className="w-full"
                  loading={isLoading}
                >
                  {isLoading ? "匹配中..." : "自动匹配"}
                </Button>
              </div>

              {isLoading && (
                <div className="space-y-2 pt-1">
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-orange-500 transition-all duration-300"
                      style={{ width: `${(progress || 0) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-400 text-center">{stage || "准备中"}</p>
                </div>
              )}
            </form>
          </div>
        </Card>

        {/* Quick formulas */}
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

      {/* ── Center: Results ── */}
      <div className="col-span-5">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title="匹配结果"
              subtitle={`${enrichedResults.length} 组镜头-探测器组合`}
              icon={<Thermometer size={16} />}
            />
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
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
                    onClick={() => setSelectedMatch(match)}
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
          </div>
        </Card>
      </div>

      {/* ── Right: Detail ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700">
            <SectionHeader
              title="方案详情"
              subtitle="红外系统参数分析"
              icon={<Award size={16} />}
            />
          </div>

          <div className="flex-1 overflow-y-auto p-5">
            {!selectedMatch || !selectedLens || !selectedDet ? (
              <div className="flex-1 flex items-center justify-center h-64">
                <EmptyState
                  icon={<Info size={24} />}
                  title="选择方案"
                  description="点击左侧匹配结果查看详细参数分析"
                />
              </div>
            ) : (
              <div className="space-y-5">
                {/* Lens image */}
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

                {/* Match score */}
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

                {/* Save action */}
                <div className="flex items-center justify-end">
                  <SaveToProjectButton
                    lensId={selectedMatch.lens_id}
                    detectorId={selectedMatch.detector_id}
                    lensModel={selectedLens.model}
                    detectorModel={selectedDet.model}
                  />
                </div>

                {/* Lens specs */}
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

                {/* Detector specs */}
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

                {/* Derived optical params */}
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
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
