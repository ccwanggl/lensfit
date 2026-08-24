import { useCallback, useEffect, useMemo, useState } from "react";
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
  type LensCreatePayload,
  type DetectorCreatePayload,
  type ImportResult,
} from "../utils/api";
import {
  LibraryFilters,
  LibraryList,
  LibraryFormModal,
  LibraryImportModal,
  LibraryDeleteModal,
  LibraryHelpPanel,
} from "../components/library";

export type Kind = "lens" | "detector";

type View = "list" | "form" | "import";

const PAGE_SIZE = 20;

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

function makeTemplate(kind: Kind) {
  const headers = kind === "lens" ? LENS_TEMPLATE_HEADERS : DETECTOR_TEMPLATE_HEADERS;
  const sample =
    kind === "lens"
      ? ["MyOptics", "MOS-25mm", "industrial", "25", "2.8", "11", "C", "100", "", "400", "700", "299"]
      : ["MySensor", "MS-5M", "industrial", "1/1.8", "7.2", "5.4", "2592", "1944", "2.2", "C", "", "", "", "199"];
  return [headers.join(","), sample.join(",")].join("\n");
}

export default function LibraryPage() {
  const [kind, setKind] = useState<Kind>("lens");
  const [view, setView] = useState<View>("list");
  const [items, setItems] = useState<(CatalogLens | CatalogDetector)[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sourceFilter, setSourceFilter] = useState<"all" | "seed" | "user">("all");
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [lensTotal, setLensTotal] = useState(0);
  const [detectorTotal, setDetectorTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState<CatalogLens | CatalogDetector | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<CatalogLens | CatalogDetector | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search.trim());
      setPage(0);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const manufacturerMap = useMemo(() => {
    const map = new Map<number, string>();
    manufacturers.forEach((m) => map.set(m.id, m.name));
    return map;
  }, [manufacturers]);

  const loadManufacturers = useCallback(async () => {
    try {
      const data = await listManufacturers();
      setManufacturers(data.items || []);
    } catch (e) {
      console.error("Load manufacturers failed:", e);
    }
  }, []);

  const loadCounts = useCallback(async () => {
    try {
      const [lData, dData] = await Promise.all([
        listLenses({ limit: 1 }),
        listDetectors({ limit: 1 }),
      ]);
      setLensTotal(lData.total ?? 0);
      setDetectorTotal(dData.total ?? 0);
    } catch (e) {
      console.error("Load counts failed:", e);
    }
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        q: debouncedSearch || undefined,
        data_source: sourceFilter,
        offset: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      };
      const data = kind === "lens" ? await listLenses(params) : await listDetectors(params);
      setItems(data.items || []);
      setTotal(data.total ?? 0);
    } catch (e) {
      console.error("Load library failed:", e);
      toast("error", "加载失败", "无法获取器件库数据");
    } finally {
      setLoading(false);
    }
  }, [kind, debouncedSearch, sourceFilter, page]);

  useEffect(() => {
    loadManufacturers();
    loadCounts();
  }, [loadManufacturers, loadCounts]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleKindChange = (k: Kind) => {
    setKind(k);
    setPage(0);
    setView("list");
    setSearch("");
    setSourceFilter("all");
    setEditing(null);
    setDeleteTarget(null);
  };

  const handleOpenCreate = () => {
    setEditing(null);
    setView("form");
  };

  const handleOpenEdit = (item: CatalogLens | CatalogDetector) => {
    if (item.data_source !== "user") {
      toast("warning", "不可编辑", "内置数据为只读，您可以通过「另存为」创建副本");
      return;
    }
    setEditing(item);
    setView("form");
  };

  const handleSubmitForm = async (payload: LensCreatePayload | DetectorCreatePayload) => {
    const isLens = kind === "lens";
    try {
      if (editing) {
        if (isLens) {
          await updateLens(editing.id, payload as LensCreatePayload);
        } else {
          await updateDetector(editing.id, payload as DetectorCreatePayload);
        }
        toast("success", "更新成功", `${editing.model} 已更新`);
      } else {
        if (isLens) {
          await createLens(payload as LensCreatePayload);
        } else {
          await createDetector(payload as DetectorCreatePayload);
        }
        toast("success", "创建成功", "新条目已加入库");
      }
      setView("list");
      await loadData();
      await loadCounts();
    } catch (err) {
      console.error("Save failed:", err);
      toast("error", "保存失败", editing ? "无法更新条目" : "无法创建条目");
      throw err;
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteTarget || deleting) return;
    setDeleting(true);
    try {
      if (kind === "lens") {
        await deleteLens(deleteTarget.id);
      } else {
        await deleteDetector(deleteTarget.id);
      }
      toast("success", "已删除", `${deleteTarget.model} 已删除`);
      setDeleteTarget(null);
      // Adjust page if the last item of the current page was removed
      const newTotal = Math.max(0, total - 1);
      const maxPage = Math.max(0, Math.ceil(newTotal / PAGE_SIZE) - 1);
      if (page > maxPage) {
        setPage(maxPage);
      } else {
        await loadData();
      }
      await loadCounts();
    } catch (err) {
      console.error("Delete failed:", err);
      toast("error", "删除失败", "无法删除该条目");
    } finally {
      setDeleting(false);
    }
  };

  const handleAddManufacturer = async (name: string) => {
    const m = await createManufacturer({ name });
    await loadManufacturers();
    return m;
  };

  const handleImport = async (file: File): Promise<ImportResult> => {
    const result = await importCatalog(file);
    if (result.inserted > 0) {
      toast("success", "导入成功", `新增 ${result.inserted} 条${result.kind === "lenses" ? "镜头" : "探测器"}`);
      await loadData();
      await loadCounts();
      await loadManufacturers();
    } else if (result.skipped > 0) {
      toast("warning", "全部跳过", "文件中的条目已存在");
    } else {
      toast("error", "导入失败", result.errors[0] || "未导入任何数据");
    }
    return result;
  };

  const handleDownloadTemplate = () => {
    downloadBlob(`${kind}_template.csv`, makeTemplate(kind));
  };

  return (
    <div className="grid grid-cols-12 gap-5">
      <div className="col-span-3">
        <LibraryFilters
          kind={kind}
          onKindChange={handleKindChange}
          search={search}
          onSearchChange={setSearch}
          sourceFilter={sourceFilter}
          onSourceFilterChange={(v) => {
            setSourceFilter(v);
            setPage(0);
          }}
          lensCount={lensTotal}
          detectorCount={detectorTotal}
          onNew={handleOpenCreate}
          onImport={() => setView("import")}
        />
      </div>

      <div className="col-span-6">
        <LibraryList
          kind={kind}
          items={items}
          loading={loading}
          total={total}
          page={page}
          pageSize={PAGE_SIZE}
          manufacturerMap={manufacturerMap}
          onEdit={handleOpenEdit}
          onDelete={setDeleteTarget}
          onPageChange={setPage}
          onDownloadTemplate={handleDownloadTemplate}
          onNew={handleOpenCreate}
        />
      </div>

      <div className="col-span-3">
        <LibraryHelpPanel />
      </div>

      {view === "form" && (
        <LibraryFormModal
          kind={kind}
          editing={editing}
          manufacturers={manufacturers}
          onClose={() => setView("list")}
          onSubmit={handleSubmitForm}
          onAddManufacturer={handleAddManufacturer}
        />
      )}

      {view === "import" && (
        <LibraryImportModal
          kind={kind}
          onClose={() => setView("list")}
          onDownloadTemplate={handleDownloadTemplate}
          onImport={handleImport}
        />
      )}

      <LibraryDeleteModal item={deleteTarget} onConfirm={handleConfirmDelete} onCancel={() => setDeleteTarget(null)} loading={deleting} />
    </div>
  );
}
