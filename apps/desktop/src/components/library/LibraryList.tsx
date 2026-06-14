import { Package, Camera, Building2, Pencil, Trash2 } from "lucide-react";
import { Card, Badge, EmptyState, Button, SectionHeader } from "../ui";
import { Download } from "lucide-react";
import type { CatalogLens, CatalogDetector } from "../../utils/api";

export type Kind = "lens" | "detector";

interface Props {
  kind: Kind;
  items: (CatalogLens | CatalogDetector)[];
  loading: boolean;
  total: number;
  page: number;
  pageSize: number;
  manufacturerMap: Map<number, string>;
  onEdit: (item: CatalogLens | CatalogDetector) => void;
  onDelete: (item: CatalogLens | CatalogDetector) => void;
  onPageChange: (page: number) => void;
  onDownloadTemplate: () => void;
  onNew: () => void;
}

const KIND_LABEL: Record<Kind, string> = {
  lens: "镜头",
  detector: "探测器",
};

function formatPrice(v: number | null | undefined) {
  if (v == null) return "—";
  return `$${v.toLocaleString("en-US")}`;
}

export default function LibraryList({
  kind,
  items,
  loading,
  total,
  page,
  pageSize,
  manufacturerMap,
  onEdit,
  onDelete,
  onPageChange,
  onDownloadTemplate,
  onNew,
}: Props) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <Card padding="none" className="overflow-hidden h-full flex flex-col">
      <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
        <SectionHeader
          title={KIND_LABEL[kind] + "列表"}
          subtitle={`${items.length} / ${total} 个`}
          icon={kind === "lens" ? <Package size={16} /> : <Camera size={16} />}
          className="mb-0"
        />
        <div className="flex items-center gap-1.5">
          <Button size="sm" variant="outline" leftIcon={<Download size={14} />} onClick={onDownloadTemplate}>
            模板
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <EmptyState icon={<Package size={24} />} title="加载中" description="正在读取器件目录..." />
          </div>
        ) : items.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <EmptyState
              icon={kind === "lens" ? <Package size={24} /> : <Camera size={24} />}
              title={`暂无${KIND_LABEL[kind]}`}
              description={`点击「新建」或「批量导入」添加${KIND_LABEL[kind]}`}
              action={
                <Button size="sm" leftIcon={<Package size={14} />} onClick={onNew}>
                  新建
                </Button>
              }
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {items.map((it) => {
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
                        onClick={() => onEdit(it)}
                        className="p-1.5 rounded-md text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
                        title="编辑"
                      >
                        <Pencil size={14} />
                      </button>
                      {isUser && (
                        <button
                          type="button"
                          onClick={() => onDelete(it)}
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

      {totalPages > 1 && (
        <div className="p-3 border-t border-slate-100 dark:border-slate-700 flex items-center justify-between text-xs">
          <span className="text-slate-500 dark:text-slate-400">
            第 {page + 1} / {totalPages} 页
          </span>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="ghost" disabled={page === 0} onClick={() => onPageChange(page - 1)}>
              上一页
            </Button>
            <Button size="sm" variant="ghost" disabled={page >= totalPages - 1} onClick={() => onPageChange(page + 1)}>
              下一页
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
