import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Package,
  Camera,
  Plus,
  Search,
  Trash2,
  Pencil,
  Upload,
  Download,
  X,
  Database,
  AlertTriangle,
  CheckCircle2,
  Building2,
  FileSpreadsheet,
} from "lucide-react";
import {
  Card,
  Button,
  Input,
  Badge,
  SectionHeader,
  EmptyState,
} from "../components/ui";
import { type InputChangeEvent } from "../components/ui/Input";
import { toast } from "../hooks/useToast";
import {
  listLenses,
  listDetectors,
  listManufacturers,
  createManufacturer,
  createLens,
  updateLens,
  deleteLens,
  createDetector,
  updateDetector,
  deleteDetector,
  importCatalog,
  type CatalogLens,
  type CatalogDetector,
  type Manufacturer,
} from "../utils/api";

type Kind = "lens" | "detector";
type View = "list" | "form" | "import";

const KIND_CONFIG: Record<Kind, { label: string; icon: React.ReactNode; color: string }> = {
  lens: { label: "镜头", icon: <Package size={16} />, color: "text-indigo-500" },
  detector: { label: "探测器", icon: <Camera size={16} />, color: "text-emerald-500" },
};

const LENS_CATEGORIES = ["industrial", "photography", "microscope", "infrared", "telecentric", "unknown"];
const DETECTOR_CATEGORIES = ["industrial", "photography", "microscope", "infrared", "unknown"];
const MOUNTS = ["C", "CS", "F", "M42", "M58", "M72", "EF", "RF", "E", "L", "V", "TFL", "TFL-II", "Other"];

function formatPrice(v: number | null | undefined) {
  if (v == null) return "—";
  return `$${v.toLocaleString("en-US")}`;
}

function toNumber(v: string): number | undefined {
  const trimmed = v.trim();
  if (trimmed === "") return undefined;
  const n = Number(trimmed);
  return Number.isFinite(n) ? n : undefined;
}

function downloadBlob(filename: string, content: string, type = "text/csv;charset=utf-8;") {
  const blob = new Blob(["\ufeff" + content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

const LENS_TEMPLATE_HEADERS = [
  "manufacturer_name",
  "model",
  "category",
  "focal_length_mm",
  "max_aperture",
  "image_circle_mm",
  "mount_type",
  "nominal_wd_mm",
  "na",
  "wavelength_min_nm",
  "wavelength_max_nm",
  "price_usd",
];

const DETECTOR_TEMPLATE_HEADERS = [
  "manufacturer_name",
  "model",
  "category",
  "sensor_format_inch",
  "sensor_w_mm",
  "sensor_h_mm",
  "resolution_w",
  "resolution_h",
  "pixel_size_um",
  "mount_type",
  "netd_mk",
  "spectral_range_min_um",
  "spectral_range_max_um",
  "price_usd",
];

function makeTemplate(kind: Kind) {
  const headers = kind === "lens" ? LENS_TEMPLATE_HEADERS : DETECTOR_TEMPLATE_HEADERS;
  const sample = kind === "lens"
    ? ["MyOptics", "MOS-25mm", "industrial", "25", "2.8", "11", "C", "100", "", "400", "700", "299"]
    : ["MySensor", "MS-5M", "industrial", "1/1.8", "7.2", "5.4", "2592", "1944", "2.2", "C", "", "", "", "199"];
  return [headers.join(","), sample.join(",")].join("\n");
}

interface LensFormData {
  manufacturer_id: string;
  model: string;
  category: string;
  focal_length_mm: string;
  max_aperture: string;
  image_circle_mm: string;
  mount_type: string;
  nominal_wd_mm: string;
  na: string;
  wavelength_min_nm: string;
  wavelength_max_nm: string;
  price_usd: string;
}

interface DetectorFormData {
  manufacturer_id: string;
  model: string;
  category: string;
  sensor_format_inch: string;
  sensor_w_mm: string;
  sensor_h_mm: string;
  resolution_w: string;
  resolution_h: string;
  pixel_size_um: string;
  mount_type: string;
  netd_mk: string;
  spectral_range_min_um: string;
  spectral_range_max_um: string;
  price_usd: string;
}

const EMPTY_LENS_FORM: LensFormData = {
  manufacturer_id: "",
  model: "",
  category: "industrial",
  focal_length_mm: "",
  max_aperture: "",
  image_circle_mm: "",
  mount_type: "",
  nominal_wd_mm: "",
  na: "",
  wavelength_min_nm: "",
  wavelength_max_nm: "",
  price_usd: "",
};

const EMPTY_DETECTOR_FORM: DetectorFormData = {
  manufacturer_id: "",
  model: "",
  category: "industrial",
  sensor_format_inch: "",
  sensor_w_mm: "",
  sensor_h_mm: "",
  resolution_w: "",
  resolution_h: "",
  pixel_size_um: "",
  mount_type: "",
  netd_mk: "",
  spectral_range_min_um: "",
  spectral_range_max_um: "",
  price_usd: "",
};

function lensToForm(l: CatalogLens): LensFormData {
  return {
    manufacturer_id: l.manufacturer_id ? String(l.manufacturer_id) : "",
    model: l.model || "",
    category: l.category || "industrial",
    focal_length_mm: l.focal_length_mm != null ? String(l.focal_length_mm) : "",
    max_aperture: l.max_aperture != null ? String(l.max_aperture) : "",
    image_circle_mm: l.image_circle_mm != null ? String(l.image_circle_mm) : "",
    mount_type: l.mount_type || "",
    nominal_wd_mm: l.nominal_wd_mm != null ? String(l.nominal_wd_mm) : "",
    na: l.na != null ? String(l.na) : "",
    wavelength_min_nm: l.wavelength_min_nm != null ? String(l.wavelength_min_nm) : "",
    wavelength_max_nm: l.wavelength_max_nm != null ? String(l.wavelength_max_nm) : "",
    price_usd: l.price_usd != null ? String(l.price_usd) : "",
  };
}

function detectorToForm(d: CatalogDetector): DetectorFormData {
  return {
    manufacturer_id: d.manufacturer_id ? String(d.manufacturer_id) : "",
    model: d.model || "",
    category: d.category || "industrial",
    sensor_format_inch: d.sensor_format_inch || "",
    sensor_w_mm: d.sensor_w_mm != null ? String(d.sensor_w_mm) : "",
    sensor_h_mm: d.sensor_h_mm != null ? String(d.sensor_h_mm) : "",
    resolution_w: d.resolution_w != null ? String(d.resolution_w) : "",
    resolution_h: d.resolution_h != null ? String(d.resolution_h) : "",
    pixel_size_um: d.pixel_size_um != null ? String(d.pixel_size_um) : "",
    mount_type: d.mount_type || "",
    netd_mk: d.netd_mk != null ? String(d.netd_mk) : "",
    spectral_range_min_um: d.spectral_range_min_um != null ? String(d.spectral_range_min_um) : "",
    spectral_range_max_um: d.spectral_range_max_um != null ? String(d.spectral_range_max_um) : "",
    price_usd: d.price_usd != null ? String(d.price_usd) : "",
  };
}

function buildLensPayload(form: LensFormData) {
  return {
    manufacturer_id: form.manufacturer_id ? Number(form.manufacturer_id) : undefined,
    model: form.model.trim(),
    category: form.category,
    focal_length_mm: toNumber(form.focal_length_mm),
    max_aperture: toNumber(form.max_aperture),
    image_circle_mm: toNumber(form.image_circle_mm),
    mount_type: form.mount_type || undefined,
    nominal_wd_mm: toNumber(form.nominal_wd_mm),
    na: toNumber(form.na),
    wavelength_min_nm: toNumber(form.wavelength_min_nm),
    wavelength_max_nm: toNumber(form.wavelength_max_nm),
    price_usd: toNumber(form.price_usd),
  };
}

function buildDetectorPayload(form: DetectorFormData) {
  return {
    manufacturer_id: form.manufacturer_id ? Number(form.manufacturer_id) : undefined,
    model: form.model.trim(),
    category: form.category,
    sensor_format_inch: form.sensor_format_inch || undefined,
    sensor_w_mm: toNumber(form.sensor_w_mm),
    sensor_h_mm: toNumber(form.sensor_h_mm),
    resolution_w: toNumber(form.resolution_w),
    resolution_h: toNumber(form.resolution_h),
    pixel_size_um: toNumber(form.pixel_size_um),
    mount_type: form.mount_type || undefined,
    netd_mk: toNumber(form.netd_mk),
    spectral_range_min_um: toNumber(form.spectral_range_min_um),
    spectral_range_max_um: toNumber(form.spectral_range_max_um),
    price_usd: toNumber(form.price_usd),
  };
}

export default function LibraryPage() {
  const [kind, setKind] = useState<Kind>("lens");
  const [view, setView] = useState<View>("list");
  const [lenses, setLenses] = useState<CatalogLens[]>([]);
  const [detectors, setDetectors] = useState<CatalogDetector[]>([]);
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [sourceFilter, setSourceFilter] = useState<"all" | "seed" | "user">("all");
  const [editing, setEditing] = useState<CatalogLens | CatalogDetector | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<CatalogLens | CatalogDetector | null>(null);

  const [lensForm, setLensForm] = useState<LensFormData>(EMPTY_LENS_FORM);
  const [detectorForm, setDetectorForm] = useState<DetectorFormData>(EMPTY_DETECTOR_FORM);
  const [newManufacturerName, setNewManufacturerName] = useState("");
  const [showAddManufacturer, setShowAddManufacturer] = useState(false);

  const [importFile, setImportFile] = useState<File | null>(null);
  const [importResult, setImportResult] = useState<{ kind: string; inserted: number; skipped: number; errors: string[] } | null>(null);
  const [importing, setImporting] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [lData, dData, mData] = await Promise.all([
        listLenses({ limit: 2000 }),
        listDetectors({ limit: 2000 }),
        listManufacturers(),
      ]);
      setLenses(lData.items || []);
      setDetectors(dData.items || []);
      setManufacturers(mData.items || []);
    } catch (e) {
      console.error("Load library failed:", e);
      toast("error", "加载失败", "无法获取器件库数据");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const items = useMemo(() => (kind === "lens" ? lenses : detectors), [kind, lenses, detectors]);

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase();
    return items.filter((it) => {
      const matchesSearch =
        !term ||
        it.model.toLowerCase().includes(term) ||
        (it as CatalogLens).mount_type?.toLowerCase().includes(term) ||
        (it as CatalogDetector).mount_type?.toLowerCase().includes(term) ||
        (it.category || "").toLowerCase().includes(term);
      const matchesSource = sourceFilter === "all" || it.data_source === sourceFilter;
      return matchesSearch && matchesSource;
    });
  }, [items, search, sourceFilter]);

  const manufacturerMap = useMemo(() => {
    const map = new Map<number, string>();
    manufacturers.forEach((m) => map.set(m.id, m.name));
    return map;
  }, [manufacturers]);

  const handleOpenCreate = () => {
    setEditing(null);
    setLensForm(EMPTY_LENS_FORM);
    setDetectorForm(EMPTY_DETECTOR_FORM);
    setView("form");
  };

  const handleOpenEdit = (item: CatalogLens | CatalogDetector) => {
    if (item.data_source !== "user") {
      toast("warning", "不可编辑", "内置数据为只读，您可以通过「另存为」创建副本");
      return;
    }
    setEditing(item);
    if (kind === "lens") {
      setLensForm(lensToForm(item as CatalogLens));
    } else {
      setDetectorForm(detectorToForm(item as CatalogDetector));
    }
    setView("form");
  };

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();
    const isLens = kind === "lens";
    const model = isLens ? lensForm.model.trim() : detectorForm.model.trim();
    if (!model) {
      toast("error", "校验失败", "型号不能为空");
      return;
    }
    try {
      if (isLens) {
        const payload = buildLensPayload(lensForm);
        if (editing) {
          await updateLens(editing.id, payload);
          toast("success", "更新成功", `镜头 ${payload.model} 已更新`);
        } else {
          await createLens(payload);
          toast("success", "创建成功", `镜头 ${payload.model} 已加入库`);
        }
      } else {
        const payload = buildDetectorPayload(detectorForm);
        if (editing) {
          await updateDetector(editing.id, payload);
          toast("success", "更新成功", `探测器 ${payload.model} 已更新`);
        } else {
          await createDetector(payload);
          toast("success", "创建成功", `探测器 ${payload.model} 已加入库`);
        }
      }
      setView("list");
      await loadData();
    } catch (err) {
      console.error("Save failed:", err);
      toast("error", "保存失败", editing ? "无法更新条目" : "无法创建条目");
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      if (kind === "lens") {
        await deleteLens(deleteTarget.id);
      } else {
        await deleteDetector(deleteTarget.id);
      }
      toast("success", "已删除", `${deleteTarget.model} 已删除`);
      setDeleteTarget(null);
      await loadData();
    } catch (err) {
      console.error("Delete failed:", err);
      toast("error", "删除失败", "无法删除该条目");
    }
  };

  const handleAddManufacturer = async () => {
    const name = newManufacturerName.trim();
    if (!name) return;
    try {
      const m = await createManufacturer({ name });
      setManufacturers((prev) => [...prev, m].sort((a, b) => a.name.localeCompare(b.name)));
      if (kind === "lens") {
        setLensForm((f) => ({ ...f, manufacturer_id: String(m.id) }));
      } else {
        setDetectorForm((f) => ({ ...f, manufacturer_id: String(m.id) }));
      }
      setNewManufacturerName("");
      setShowAddManufacturer(false);
      toast("success", "厂商已添加", m.name);
    } catch (err) {
      toast("error", "添加失败", "无法创建新厂商");
    }
  };

  const handleImport = async () => {
    if (!importFile) return;
    setImporting(true);
    setImportResult(null);
    try {
      const result = await importCatalog(importFile);
      setImportResult(result);
      if (result.inserted > 0) {
        toast("success", "导入成功", `新增 ${result.inserted} 条${result.kind === "lenses" ? "镜头" : "探测器"}`);
        await loadData();
      } else if (result.skipped > 0) {
        toast("warning", "全部跳过", "文件中的条目已存在");
      } else {
        toast("error", "导入失败", result.errors[0] || "未导入任何数据");
      }
    } catch (err) {
      console.error("Import failed:", err);
      toast("error", "导入失败", "无法解析上传文件");
    } finally {
      setImporting(false);
    }
  };

  const renderManufacturerSelect = (value: string, onChange: (v: string) => void) => (
    <div className="space-y-2">
      <Input
        as="select"
        label="厂商"
        value={value}
        onChange={(e: InputChangeEvent) => onChange(e.target.value)}
      >
        <option value="">未知厂商</option>
        {manufacturers.map((m) => (
          <option key={m.id} value={m.id}>
            {m.name}
          </option>
        ))}
      </Input>
      {!showAddManufacturer ? (
        <button
          type="button"
          onClick={() => setShowAddManufacturer(true)}
          className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
        >
          + 新建厂商
        </button>
      ) : (
        <div className="flex items-center gap-2">
          <Input
            placeholder="厂商名称"
            value={newManufacturerName}
            onChange={(e: InputChangeEvent) => setNewManufacturerName(e.target.value)}
            className="flex-1"
          />
          <Button size="sm" onClick={handleAddManufacturer} leftIcon={<Plus size={12} />}>
            添加
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setShowAddManufacturer(false);
              setNewManufacturerName("");
            }}
          >
            取消
          </Button>
        </div>
      )}
    </div>
  );

  const renderLensForm = () => (
    <form onSubmit={handleSubmitForm} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="sm:col-span-2">{renderManufacturerSelect(lensForm.manufacturer_id, (v) => setLensForm({ ...lensForm, manufacturer_id: v }))}</div>
      <Input label="型号 *" value={lensForm.model} onChange={(e) => setLensForm({ ...lensForm, model: e.target.value })} required />
      <Input as="select" label="分类" value={lensForm.category} onChange={(e) => setLensForm({ ...lensForm, category: e.target.value })}>
        {LENS_CATEGORIES.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </Input>
      <Input type="number" step="0.01" label="焦距 (mm)" value={lensForm.focal_length_mm} onChange={(e) => setLensForm({ ...lensForm, focal_length_mm: e.target.value })} />
      <Input type="number" step="0.01" label="最大光圈" value={lensForm.max_aperture} onChange={(e) => setLensForm({ ...lensForm, max_aperture: e.target.value })} />
      <Input type="number" step="0.01" label="像圆 (mm)" value={lensForm.image_circle_mm} onChange={(e) => setLensForm({ ...lensForm, image_circle_mm: e.target.value })} />
      <Input as="select" label="接口" value={lensForm.mount_type} onChange={(e) => setLensForm({ ...lensForm, mount_type: e.target.value })}>
        <option value="">—</option>
        {MOUNTS.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </Input>
      <Input type="number" step="0.01" label="标称工作距离 (mm)" value={lensForm.nominal_wd_mm} onChange={(e) => setLensForm({ ...lensForm, nominal_wd_mm: e.target.value })} />
      <Input type="number" step="0.001" label="数值孔径 NA" value={lensForm.na} onChange={(e) => setLensForm({ ...lensForm, na: e.target.value })} />
      <Input type="number" step="1" label="波长下限 (nm)" value={lensForm.wavelength_min_nm} onChange={(e) => setLensForm({ ...lensForm, wavelength_min_nm: e.target.value })} />
      <Input type="number" step="1" label="波长上限 (nm)" value={lensForm.wavelength_max_nm} onChange={(e) => setLensForm({ ...lensForm, wavelength_max_nm: e.target.value })} />
      <Input type="number" step="0.01" label="价格 (USD)" value={lensForm.price_usd} onChange={(e) => setLensForm({ ...lensForm, price_usd: e.target.value })} />
      <div className="sm:col-span-2 flex items-center justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => setView("list")}>
          取消
        </Button>
        <Button type="submit" variant="primary" size="sm" leftIcon={<CheckCircle2 size={14} />}>
          {editing ? "保存" : "创建"}
        </Button>
      </div>
    </form>
  );

  const renderDetectorForm = () => (
    <form onSubmit={handleSubmitForm} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="sm:col-span-2">{renderManufacturerSelect(detectorForm.manufacturer_id, (v) => setDetectorForm({ ...detectorForm, manufacturer_id: v }))}</div>
      <Input label="型号 *" value={detectorForm.model} onChange={(e) => setDetectorForm({ ...detectorForm, model: e.target.value })} required />
      <Input as="select" label="分类" value={detectorForm.category} onChange={(e) => setDetectorForm({ ...detectorForm, category: e.target.value })}>
        {DETECTOR_CATEGORIES.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </Input>
      <Input label="靶面尺寸 (inch)" placeholder="例如 1/1.8" value={detectorForm.sensor_format_inch} onChange={(e) => setDetectorForm({ ...detectorForm, sensor_format_inch: e.target.value })} />
      <Input type="number" step="0.01" label="靶面宽 (mm)" value={detectorForm.sensor_w_mm} onChange={(e) => setDetectorForm({ ...detectorForm, sensor_w_mm: e.target.value })} />
      <Input type="number" step="0.01" label="靶面高 (mm)" value={detectorForm.sensor_h_mm} onChange={(e) => setDetectorForm({ ...detectorForm, sensor_h_mm: e.target.value })} />
      <Input type="number" step="1" label="分辨率宽 (px)" value={detectorForm.resolution_w} onChange={(e) => setDetectorForm({ ...detectorForm, resolution_w: e.target.value })} />
      <Input type="number" step="1" label="分辨率高 (px)" value={detectorForm.resolution_h} onChange={(e) => setDetectorForm({ ...detectorForm, resolution_h: e.target.value })} />
      <Input type="number" step="0.01" label="像元尺寸 (µm)" value={detectorForm.pixel_size_um} onChange={(e) => setDetectorForm({ ...detectorForm, pixel_size_um: e.target.value })} />
      <Input as="select" label="接口" value={detectorForm.mount_type} onChange={(e) => setDetectorForm({ ...detectorForm, mount_type: e.target.value })}>
        <option value="">—</option>
        {MOUNTS.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </Input>
      <Input type="number" step="0.01" label="NETD (mK)" value={detectorForm.netd_mk} onChange={(e) => setDetectorForm({ ...detectorForm, netd_mk: e.target.value })} />
      <Input type="number" step="0.01" label="光谱下限 (µm)" value={detectorForm.spectral_range_min_um} onChange={(e) => setDetectorForm({ ...detectorForm, spectral_range_min_um: e.target.value })} />
      <Input type="number" step="0.01" label="光谱上限 (µm)" value={detectorForm.spectral_range_max_um} onChange={(e) => setDetectorForm({ ...detectorForm, spectral_range_max_um: e.target.value })} />
      <Input type="number" step="0.01" label="价格 (USD)" value={detectorForm.price_usd} onChange={(e) => setDetectorForm({ ...detectorForm, price_usd: e.target.value })} />
      <div className="sm:col-span-2 flex items-center justify-end gap-2 pt-2">
        <Button type="button" variant="ghost" size="sm" onClick={() => setView("list")}>
          取消
        </Button>
        <Button type="submit" variant="primary" size="sm" leftIcon={<CheckCircle2 size={14} />}>
          {editing ? "保存" : "创建"}
        </Button>
      </div>
    </form>
  );

  return (
    <div className="grid grid-cols-12 gap-5">
      {/* ── Left: Navigation / filters ── */}
      <div className="col-span-3">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700">
            <SectionHeader title="器件库" subtitle="管理镜头与探测器目录" icon={<Database size={16} />} />
          </div>
          <div className="p-3 space-y-2">
            {(["lens", "detector"] as Kind[]).map((k) => {
              const cfg = KIND_CONFIG[k];
              const active = kind === k;
              return (
                <button
                  key={k}
                  onClick={() => {
                    setKind(k);
                    setView("list");
                    setSearch("");
                    setSourceFilter("all");
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                    active
                      ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                  }`}
                >
                  <span className={active ? cfg.color : "text-slate-400 dark:text-slate-500"}>{cfg.icon}</span>
                  {cfg.label}
                </button>
              );
            })}
          </div>

          <div className="px-3 pb-3 space-y-3">
            <Input
              placeholder="搜索型号、分类、接口"
              icon={<Search size={14} />}
              value={search}
              onChange={(e: InputChangeEvent) => setSearch(e.target.value)}
            />
            <div>
              <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5">数据来源</p>
              <div className="flex flex-wrap gap-1.5">
                {(["all", "seed", "user"] as const).map((s) => (
                  <button
                    key={s}
                    onClick={() => setSourceFilter(s)}
                    className={`text-[10px] px-2 py-1 rounded-md transition-colors ${
                      sourceFilter === s
                        ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 font-semibold"
                        : "bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
                    }`}
                  >
                    {s === "all" ? "全部" : s === "seed" ? "内置" : "自定义"}
                  </button>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800">
                <p className="text-lg font-bold text-slate-800 dark:text-slate-100">{lenses.length}</p>
                <p className="text-[10px] text-slate-400 dark:text-slate-500">镜头</p>
              </div>
              <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800">
                <p className="text-lg font-bold text-slate-800 dark:text-slate-100">{detectors.length}</p>
                <p className="text-[10px] text-slate-400 dark:text-slate-500">探测器</p>
              </div>
            </div>
            <div className="space-y-2 pt-1">
              <Button variant="primary" size="sm" className="w-full" leftIcon={<Plus size={14} />} onClick={handleOpenCreate}>
                新建{KIND_CONFIG[kind].label}
              </Button>
              <Button variant="outline" size="sm" className="w-full" leftIcon={<Upload size={14} />} onClick={() => { setView("import"); setImportFile(null); setImportResult(null); }}>
                批量导入
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* ── Center: Item list ── */}
      <div className="col-span-6">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title={KIND_CONFIG[kind].label + "列表"}
              subtitle={`${filteredItems.length} / ${items.length} 个`}
              icon={KIND_CONFIG[kind].icon}
              className="mb-0"
            />
            <div className="flex items-center gap-1.5">
              <Button size="sm" variant="outline" leftIcon={<Download size={14} />} onClick={() => downloadBlob(`${kind}_template.csv`, makeTemplate(kind))}>
                模板
              </Button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <EmptyState icon={<Database size={24} />} title="加载中" description="正在读取器件目录..." />
              </div>
            ) : filteredItems.length === 0 ? (
              <div className="flex items-center justify-center h-64">
                <EmptyState
                  icon={kind === "lens" ? <Package size={24} /> : <Camera size={24} />}
                  title={`暂无${KIND_CONFIG[kind].label}`}
                  description={search || sourceFilter !== "all" ? "没有匹配当前筛选的条目" : `点击左侧「新建」或「批量导入」添加${KIND_CONFIG[kind].label}`}
                  action={
                    <Button size="sm" leftIcon={<Plus size={14} />} onClick={handleOpenCreate}>
                      新建
                    </Button>
                  }
                />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {filteredItems.map((it) => {
                  const isUser = it.data_source === "user";
                  const manufacturer = it.manufacturer_id ? manufacturerMap.get(it.manufacturer_id) : undefined;
                  return (
                    <div
                      key={it.id}
                      className="group p-4 rounded-xl border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-200 dark:hover:border-indigo-700 transition-all"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">{it.model}</h4>
                            <Badge variant={isUser ? "success" : "neutral"} size="sm">
                              {isUser ? "自定义" : "内置"}
                            </Badge>
                            <Badge variant="info" size="sm">{it.category}</Badge>
                          </div>
                          <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400 mb-2">
                            <Building2 size={12} />
                            <span className="truncate">{manufacturer || "未知厂商"}</span>
                          </div>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-500 dark:text-slate-400">
                            {kind === "lens" ? (
                              <>
                                <span>焦距: {(it as CatalogLens).focal_length_mm ?? "—"} mm</span>
                                <span>光圈: f/{(it as CatalogLens).max_aperture ?? "—"}</span>
                                <span>像圆: {(it as CatalogLens).image_circle_mm ?? "—"} mm</span>
                                <span>接口: {(it as CatalogLens).mount_type || "—"}</span>
                              </>
                            ) : (
                              <>
                                <span>靶面: {(it as CatalogDetector).sensor_format_inch || "—"}</span>
                                <span>分辨率: {(it as CatalogDetector).resolution_w ?? "—"} × {(it as CatalogDetector).resolution_h ?? "—"}</span>
                                <span>像元: {(it as CatalogDetector).pixel_size_um ?? "—"} µm</span>
                                <span>接口: {(it as CatalogDetector).mount_type || "—"}</span>
                              </>
                            )}
                            <span className="font-medium text-slate-700 dark:text-slate-300">{formatPrice(it.price_usd)}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            onClick={() => handleOpenEdit(it)}
                            className="p-1.5 rounded-md text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
                            title="编辑"
                          >
                            <Pencil size={14} />
                          </button>
                          {isUser && (
                            <button
                              type="button"
                              onClick={() => setDeleteTarget(it)}
                              className="p-1.5 rounded-md text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-colors"
                              title="删除"
                            >
                              <Trash2 size={14} />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* ── Right: Tips / details ── */}
      <div className="col-span-3">
        <Card className="h-full">
          <SectionHeader title="使用说明" subtitle="如何管理自定义器件" icon={<FileSpreadsheet size={16} />} />
          <div className="space-y-4 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            <p>
              <strong className="text-slate-800 dark:text-slate-200">内置数据：</strong>
              来自系统预置目录，只读。匹配引擎会自动将其纳入候选。
            </p>
            <p>
              <strong className="text-slate-800 dark:text-slate-200">自定义数据：</strong>
              通过表单或 CSV / Excel 批量导入。创建后立即可在各领域选型页面参与匹配。
            </p>
            <p>
              <strong className="text-slate-800 dark:text-slate-200">去重规则：</strong>
              导入时按「厂商 + 型号」去重。已存在条目会被跳过，不会覆盖。
            </p>
            <p>
              <strong className="text-slate-800 dark:text-slate-200">文件要求：</strong>
              文件名需包含 <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700">lens</code> 或
              <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700">detector</code> /
              <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-700">camera</code> 以便自动识别。
            </p>
          </div>
        </Card>
      </div>

      {/* ── Form Modal ── */}
      {view === "form" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-6">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                {editing ? `编辑${KIND_CONFIG[kind].label}` : `新建${KIND_CONFIG[kind].label}`}
              </h3>
              <button
                type="button"
                onClick={() => setView("list")}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
            {kind === "lens" ? renderLensForm() : renderDetectorForm()}
          </Card>
        </div>
      )}

      {/* ── Import Modal ── */}
      {view === "import" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-6">
          <Card className="w-full max-w-md animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                批量导入{KIND_CONFIG[kind].label}
              </h3>
              <button
                type="button"
                onClick={() => setView("list")}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
            <div className="space-y-4">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <p className="text-xs text-slate-600 dark:text-slate-300 mb-2">
                  当前导入类型：{KIND_CONFIG[kind].label}
                </p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  请确保文件名包含 <strong>{kind === "lens" ? "lens" : "detector / camera"}</strong>，否则后端无法识别。
                </p>
              </div>
              <Input
                type="file"
                accept=".csv,.xlsx"
                label="选择文件"
                helper="支持 CSV 或 .xlsx 格式"
                onChange={(e: InputChangeEvent) => {
                  const file = (e.target as HTMLInputElement).files?.[0] ?? null;
                  setImportFile(file);
                  setImportResult(null);
                }}
              />
              <div className="flex items-center justify-between">
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<Download size={14} />}
                  onClick={() => downloadBlob(`${kind}_template.csv`, makeTemplate(kind))}
                >
                  下载模板
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  loading={importing}
                  leftIcon={<Upload size={14} />}
                  onClick={handleImport}
                  disabled={!importFile}
                >
                  开始导入
                </Button>
              </div>
              {importResult && (
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 space-y-1">
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                    导入结果：{importResult.kind === "lenses" ? "镜头" : "探测器"}
                  </p>
                  <p className="text-[11px] text-slate-600 dark:text-slate-400">
                    新增 <strong className="text-emerald-600 dark:text-emerald-400">{importResult.inserted}</strong> 条，
                    跳过 <strong className="text-amber-600 dark:text-amber-400">{importResult.skipped}</strong> 条
                  </p>
                  {importResult.errors.length > 0 && (
                    <div className="max-h-32 overflow-y-auto text-[11px] text-rose-600 dark:text-rose-400 space-y-0.5 mt-2">
                      {importResult.errors.map((err, i) => (
                        <p key={i}>{err}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* ── Delete Confirm Modal ── */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-6">
          <Card className="w-full max-w-sm animate-fade-in">
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-900/20 text-rose-500">
                <AlertTriangle size={16} />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">确认删除？</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  「{deleteTarget.model}」将被永久删除，此操作不可撤销。
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setDeleteTarget(null)}>
                取消
              </Button>
              <Button variant="danger" size="sm" leftIcon={<Trash2 size={14} />} onClick={handleConfirmDelete}>
                删除
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
