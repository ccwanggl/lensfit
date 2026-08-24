import { useEffect, useState } from "react";
import { Plus, CheckCircle2 } from "lucide-react";
import { Button, Input, Modal } from "../ui";
import { type InputChangeEvent } from "../ui/Input";
import type {
  CatalogLens,
  CatalogDetector,
  Manufacturer,
  LensCreatePayload,
  DetectorCreatePayload,
} from "../../utils/api";

export type Kind = "lens" | "detector";

interface Props {
  kind: Kind;
  editing: CatalogLens | CatalogDetector | null;
  manufacturers: Manufacturer[];
  onClose: () => void;
  onSubmit: (payload: LensCreatePayload | DetectorCreatePayload) => Promise<void>;
  onAddManufacturer: (name: string) => Promise<Manufacturer>;
}

const LENS_CATEGORIES = ["industrial", "photography", "microscope", "infrared", "telecentric", "unknown"];
const DETECTOR_CATEGORIES = ["industrial", "photography", "microscope", "infrared", "unknown"];
const MOUNTS = ["C", "CS", "F", "M42", "M58", "M72", "EF", "RF", "E", "L", "V", "TFL", "TFL-II", "Other"];

const KIND_LABEL: Record<Kind, string> = {
  lens: "镜头",
  detector: "探测器",
};

function toNumber(v: string): number | undefined {
  const trimmed = v.trim();
  if (trimmed === "") return undefined;
  const n = Number(trimmed);
  return Number.isFinite(n) ? n : undefined;
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

function buildLensPayload(form: LensFormData): LensCreatePayload {
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

function buildDetectorPayload(form: DetectorFormData): DetectorCreatePayload {
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

export default function LibraryFormModal({
  kind,
  editing,
  manufacturers,
  onClose,
  onSubmit,
  onAddManufacturer,
}: Props) {
  const [lensForm, setLensForm] = useState<LensFormData>(EMPTY_LENS_FORM);
  const [detectorForm, setDetectorForm] = useState<DetectorFormData>(EMPTY_DETECTOR_FORM);
  const [newManufacturerName, setNewManufacturerName] = useState("");
  const [showAddManufacturer, setShowAddManufacturer] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (editing) {
      if (kind === "lens") {
        setLensForm(lensToForm(editing as CatalogLens));
      } else {
        setDetectorForm(detectorToForm(editing as CatalogDetector));
      }
    } else {
      setLensForm(EMPTY_LENS_FORM);
      setDetectorForm(EMPTY_DETECTOR_FORM);
    }
    setShowAddManufacturer(false);
    setNewManufacturerName("");
  }, [editing, kind]);

  const handleAddManufacturer = async () => {
    const name = newManufacturerName.trim();
    if (!name) return;
    const m = await onAddManufacturer(name);
    if (kind === "lens") {
      setLensForm((f) => ({ ...f, manufacturer_id: String(m.id) }));
    } else {
      setDetectorForm((f) => ({ ...f, manufacturer_id: String(m.id) }));
    }
    setNewManufacturerName("");
    setShowAddManufacturer(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const model = kind === "lens" ? lensForm.model.trim() : detectorForm.model.trim();
    if (!model) return;
    setSubmitting(true);
    try {
      const payload = kind === "lens" ? buildLensPayload(lensForm) : buildDetectorPayload(detectorForm);
      await onSubmit(payload);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  const renderManufacturerSelect = (value: string, onChange: (v: string) => void) => (
    <div className="space-y-2">
      <Input as="select" label="厂商" value={value} onChange={(e: InputChangeEvent) => onChange(e.target.value)}>
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
    <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
        <Button type="button" variant="ghost" size="sm" onClick={onClose}>
          取消
        </Button>
        <Button type="submit" variant="primary" size="sm" loading={submitting} leftIcon={<CheckCircle2 size={14} />}>
          {editing ? "保存" : "创建"}
        </Button>
      </div>
    </form>
  );

  const renderDetectorForm = () => (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
        <Button type="button" variant="ghost" size="sm" onClick={onClose}>
          取消
        </Button>
        <Button type="submit" variant="primary" size="sm" loading={submitting} leftIcon={<CheckCircle2 size={14} />}>
          {editing ? "保存" : "创建"}
        </Button>
      </div>
    </form>
  );

  return (
    <Modal
      open
      onClose={onClose}
      title={editing ? `编辑${KIND_LABEL[kind]}` : `新建${KIND_LABEL[kind]}`}
      widthClass="max-w-2xl"
    >
      <div className="max-h-[70vh] overflow-y-auto -mx-1 px-1">
        {kind === "lens" ? renderLensForm() : renderDetectorForm()}
      </div>
    </Modal>
  );
}
