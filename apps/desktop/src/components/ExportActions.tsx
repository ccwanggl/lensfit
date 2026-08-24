import { useState, useCallback, useRef } from "react";
import { Download, FileText, Table, Sheet } from "lucide-react";
import { exportReport } from "../utils/api";
import { toast } from "../hooks/useToast";

export type ExportFormat = "pdf" | "excel" | "csv";

interface ExportActionsProps {
  requirements: object;
  results: object[];
  diagnostics?: object[] | null;
  whatIfResults?: object[] | null;
  topK?: number;
  disabled?: boolean;
}

const FORMATS: { key: ExportFormat; label: string; icon: React.ReactNode; ext: string }[] = [
  { key: "pdf", label: "PDF 报告", icon: <FileText size={13} />, ext: "pdf" },
  { key: "excel", label: "Excel", icon: <Sheet size={13} />, ext: "xlsx" },
  { key: "csv", label: "CSV", icon: <Table size={13} />, ext: "csv" },
];

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export default function ExportActions({
  requirements,
  results,
  diagnostics,
  whatIfResults,
  topK = 10,
  disabled = false,
}: ExportActionsProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState<ExportFormat | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleExport = useCallback(
    async (format: ExportFormat) => {
      if (results.length === 0) {
        toast("error", "导出失败", "没有可导出的匹配结果");
        return;
      }
      setLoading(format);
      try {
        const blob = await exportReport(
          format,
          requirements,
          results,
          topK,
          diagnostics ?? undefined,
          whatIfResults ?? undefined
        );
        const fmt = FORMATS.find((f) => f.key === format);
        const date = new Date().toISOString().slice(0, 10);
        downloadBlob(blob, `optibench-report-${date}.${fmt?.ext ?? format}`);
        toast("success", "导出成功", `已下载 ${fmt?.label ?? format}`);
      } catch (e) {
        const message = e instanceof Error ? e.message : "导出失败";
        toast("error", "导出失败", message);
      } finally {
        setLoading(null);
        setOpen(false);
      }
    },
    [requirements, results, diagnostics, whatIfResults, topK]
  );

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        disabled={disabled || loading !== null}
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <Download size={13} />
        {loading ? "导出中..." : "导出"}
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 top-full mt-1.5 w-36 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg z-50 overflow-hidden">
            {FORMATS.map((fmt) => (
              <button
                key={fmt.key}
                type="button"
                disabled={loading !== null}
                onClick={() => handleExport(fmt.key)}
                className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 disabled:opacity-50 transition-colors"
              >
                <span className="text-slate-400 dark:text-slate-500">{fmt.icon}</span>
                {fmt.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
