import { useState, useMemo } from "react";
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
} from "lucide-react";
import {
  Card,
  Button,
  Input,
  Badge,
  SectionHeader,
  EmptyState,
} from "../components/ui";
import { listLenses, listDetectors } from "../utils/api";
import { toast } from "../hooks/useToast";
import LensImage from "../components/LensImage";
import PresetSelector from "../components/PresetSelector";
import { type InputChangeEvent } from "../components/ui/Input";
import { useMatching, type UnifiedMatchResult } from "../hooks/useMatching";
import { useParamHint } from "../hooks/useParamHint";
import type { CatalogLens, CatalogDetector, PresetConfigItem } from "../utils/api";

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

/* ─── Components ─── */
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

/* ─── Main Page ─── */
export default function PhotographyPage() {
  const hint = useParamHint();
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

  const [lensMap, setLensMap] = useState<Map<number, CatalogLens>>(new Map());
  const [detMap, setDetMap] = useState<Map<number, CatalogDetector>>(new Map());
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<UnifiedMatchResult | null>(null);

  const backendRequirements = useMemo(() => ({
    purpose: form.purpose === "all" ? "portrait" : form.purpose,
    sensor_format: form.format === "all" ? "FF" : form.format,
    lens_type: form.lens_type,
    mount: form.mount,
    budget_usd: form.budget,
    max_aperture: form.max_aperture === "all" ? 2.8 : parseFloat(form.max_aperture),
  }), [form]);

  const { results, isLoading, start } = useMatching({
    domain: "photography",
    requirements: backendRequirements,
    onSuccess: (matches) => {
      setSelectedMatch(matches[0] ?? null);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    setSelectedMatch(null);

    try {
      const [lensData, detData] = await Promise.all([
        listLenses({ limit: 100 }),
        listDetectors({ limit: 100 }),
      ]);

      const lm = new Map<number, CatalogLens>();
      for (const l of lensData.items || []) lm.set(l.id, l);
      setLensMap(lm);

      const dm = new Map<number, CatalogDetector>();
      for (const d of detData.items || []) dm.set(d.id, d);
      setDetMap(dm);

      start();
    } catch (e) {
      console.error("Load photo data failed:", e);
      toast("error", "数据加载失败", "无法获取摄影镜头数据");
    }
  };

  const enrichedResults = useMemo(() => {
    let items = results
      .map((r) => ({ match: r, lens: lensMap.get(r.lens_id) }))
      .filter((item): item is { match: UnifiedMatchResult; lens: CatalogLens } => !!item.lens);

    // Frontend-only filters (not part of backend scoring)
    if (form.brand !== "all") {
      items = items.filter((item) => item.lens.model.startsWith(form.brand));
    }

    if (form.lens_type !== "all") {
      const isZoom = (l: CatalogLens) => l.focal_length_min !== l.focal_length_max && l.focal_length_min != null;
      items = items.filter((item) =>
        form.lens_type === "zoom" ? isZoom(item.lens) : !isZoom(item.lens)
      );
    }

    if (form.focal_range !== "all") {
      const range = FOCAL_RANGES.find((r) => r.value === form.focal_range);
      if (range) {
        items = items.filter((item) => {
          const focal = item.lens.focal_length_mm;
          return focal >= range.min && focal <= range.max;
        });
      }
    }

    return items;
  }, [results, lensMap, form.brand, form.lens_type, form.focal_range]);

  const selectedLens = selectedMatch ? lensMap.get(selectedMatch.lens_id) : undefined;

  // Find compatible cameras for selected lens
  const compatibleCameras = useMemo(() => {
    if (!selectedLens) return [];
    return Array.from(detMap.values()).filter(
      (c) => c.mount_type && selectedLens.mount_type && c.mount_type.toLowerCase() === selectedLens.mount_type.toLowerCase()
    );
  }, [selectedLens, detMap]);

  return (
    <div className="grid grid-cols-12 gap-5">
      {/* ── Left: Input Panel ── */}
      <div className="col-span-3">
        <Card padding="none" className="overflow-hidden">
          <div className="p-6">
            <SectionHeader title="摄影参数" subtitle="配置您的摄影系统需求" icon={<Camera size={16} />} />
            <div className="mb-3">
              <PresetSelector
                domain="photography"
                onSelect={(preset: PresetConfigItem) => {
                  setForm((prev) => ({ ...prev, ...preset.params }));
                }}
              />
            </div>
            <form onSubmit={handleSubmit} className="space-y-2">
              <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
                <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">相机配置</p>
                <Input as="select" label="画幅" icon={<Image size={14} />} layout="horizontal" learnHint={hint("sensor_format")}
                  value={form.format}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, format: e.target.value })}>
                  {FORMATS.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
                </Input>

                <Input as="select" label="镜头类型" icon={<Aperture size={14} />} layout="horizontal" learnHint={hint("lens_type")}
                  value={form.lens_type}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, lens_type: e.target.value })}>
                  {LENS_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </Input>

                <Input as="select" label="焦距范围" icon={<Ruler size={14} />} layout="horizontal" learnHint={hint("focal_range")}
                  value={form.focal_range}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, focal_range: e.target.value })}>
                  {FOCAL_RANGES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
                </Input>

                <Input as="select" label="最大光圈" icon={<Aperture size={14} />} layout="horizontal" learnHint={hint("max_aperture")}
                  value={form.max_aperture}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, max_aperture: e.target.value })}>
                  {APERTURES.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
                </Input>

                <Input as="select" label="拍摄用途" icon={<Eye size={14} />} layout="horizontal" learnHint={hint("purpose")}
                  value={form.purpose}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, purpose: e.target.value })}>
                  {PURPOSES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                </Input>
              </div>

              <div className="rounded-lg border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 p-2.5 space-y-2">
                <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ml-0.5">品牌与预算</p>
                <Input as="select" label="品牌偏好" icon={<Tag size={14} />} layout="horizontal" learnHint={hint("brand")}
                  value={form.brand}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, brand: e.target.value })}>
                  {BRANDS.map((b) => <option key={b.value} value={b.value}>{b.label}</option>)}
                </Input>

                <Input as="select" label="卡口" icon={<Plug size={14} />} layout="horizontal" learnHint={hint("mount")}
                  value={form.mount}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, mount: e.target.value })}>
                  {MOUNTS.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                </Input>

                <Input type="number" label="预算上限" icon={<DollarSign size={14} />} unit="USD" layout="horizontal" learnHint={hint("budget_usd")}
                  value={form.budget}
                  onChange={(e: InputChangeEvent) => setForm({ ...form, budget: parseFloat(e.target.value) || 0 })} />
              </div>

              <div className="pt-2">
                <Button type="submit" variant="primary" size="lg" loading={isLoading} leftIcon={<Search size={16} />} className="w-full">
                  {isLoading ? "匹配中..." : "自动匹配"}
                </Button>
              </div>
            </form>
          </div>
        </Card>
      </div>

      {/* ── Center: Results Panel ── */}
      <div className="col-span-5">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-6 flex-1 flex flex-col">
            <SectionHeader
              title="推荐镜头"
              subtitle={hasSearched ? `从后端匹配结果中筛选出 ${enrichedResults.length} 支推荐` : "等待参数输入"}
              icon={<Star size={16} />}
            />

            {!hasSearched ? (
              <div className="flex-1 flex items-center justify-center">
                <EmptyState
                  icon={<Camera size={24} />}
                  title="等待匹配"
                  description="在左侧配置摄影参数后点击「自动匹配」，系统将为您推荐最适合的镜头"
                />
              </div>
            ) : enrichedResults.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <EmptyState
                  icon={<Search size={24} />}
                  title={isLoading ? "计算中..." : "无匹配结果"}
                  description={isLoading ? "后端正在执行光学计算与评分..." : "当前参数组合没有找到匹配的镜头，请放宽条件后重试"}
                />
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[640px] overflow-y-auto pr-1 stagger-children">
                {enrichedResults.slice(0, 20).map(({ match, lens }, i) => (
                  <LensCard
                    key={lens.id}
                    lens={lens}
                    rank={i + 1}
                    isSelected={selectedMatch?.lens_id === lens.id}
                    onClick={() => setSelectedMatch(match)}
                    score={match.score}
                  />
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* ── Right: Detail Panel ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden">
          <div className="p-6">
            <SectionHeader
              title="镜头详情"
              subtitle={selectedLens ? selectedLens.model : "选择镜头查看详情"}
              icon={<Camera size={16} />}
            />

            {selectedLens && (
              <div className="space-y-4">
                {/* Specs grid */}
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
                    <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">焦距</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {selectedLens.focal_length_min && selectedLens.focal_length_min !== selectedLens.focal_length_max
                        ? `${selectedLens.focal_length_min}-${selectedLens.focal_length_max}mm`
                        : `${selectedLens.focal_length_mm}mm`}
                    </p>
                  </div>
                  <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                    <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">最大光圈</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">f/{selectedLens.max_aperture}</p>
                  </div>
                  <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                    <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">卡口</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{selectedLens.mount_type}</p>
                  </div>
                  <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                    <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">价格</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">${selectedLens.price_usd.toFixed(0)}</p>
                  </div>
                  <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                    <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">像圈</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">{selectedLens.image_circle_mm}mm</p>
                  </div>
                  <div className="p-3 rounded-[10px] bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700">
                    <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">类型</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {selectedLens.focal_length_min && selectedLens.focal_length_min !== selectedLens.focal_length_max ? "变焦" : "定焦"}
                    </p>
                  </div>
                </div>

                {/* Compatible cameras */}
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
              </div>
            )}

            {!selectedLens && (
              <div className="text-center py-8">
                <EmptyState
                  icon={<Camera size={24} />}
                  title="选择镜头"
                  description="点击左侧推荐卡片查看镜头规格与兼容机身"
                />
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
