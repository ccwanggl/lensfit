import { useState } from "react";
import { Upload, Download } from "lucide-react";
import { Button, Input, Modal } from "../ui";
import { type InputChangeEvent } from "../ui/Input";
import type { ImportResult } from "../../utils/api";

export type Kind = "lens" | "detector";

interface Props {
  kind: Kind;
  onClose: () => void;
  onDownloadTemplate: () => void;
  onImport: (file: File) => Promise<ImportResult>;
}

const KIND_LABEL: Record<Kind, string> = {
  lens: "镜头",
  detector: "探测器",
};

export default function LibraryImportModal({ kind, onClose, onDownloadTemplate, onImport }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [importing, setImporting] = useState(false);

  const handleImport = async () => {
    if (!file) return;
    setImporting(true);
    setResult(null);
    try {
      const res = await onImport(file);
      setResult(res);
    } finally {
      setImporting(false);
    }
  };

  return (
    <Modal open onClose={onClose} title={`批量导入${KIND_LABEL[kind]}`}>
      <div className="space-y-3">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
          <p className="text-xs text-slate-600 dark:text-slate-300 mb-2">
            当前导入类型：{KIND_LABEL[kind]}
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
            const selected = (e.target as HTMLInputElement).files?.[0] ?? null;
            setFile(selected);
            setResult(null);
          }}
        />
        <div className="flex items-center justify-between">
          <Button variant="outline" size="sm" leftIcon={<Download size={14} />} onClick={onDownloadTemplate}>
            下载模板
          </Button>
          <Button
            variant="primary"
            size="sm"
            loading={importing}
            leftIcon={<Upload size={14} />}
            onClick={handleImport}
            disabled={!file}
          >
            开始导入
          </Button>
        </div>
        {result && (
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 space-y-1">
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">
              导入结果：{result.kind === "lenses" ? "镜头" : "探测器"}
            </p>
            <p className="text-[11px] text-slate-600 dark:text-slate-400">
              新增 <strong className="text-emerald-600 dark:text-emerald-400">{result.inserted}</strong> 条，
              跳过 <strong className="text-amber-600 dark:text-amber-400">{result.skipped}</strong> 条
            </p>
            {result.errors.length > 0 && (
              <div className="max-h-32 overflow-y-auto text-[11px] text-rose-600 dark:text-rose-400 space-y-0.5 mt-2">
                {result.errors.map((err, i) => (
                  <p key={i}>{err}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
}
