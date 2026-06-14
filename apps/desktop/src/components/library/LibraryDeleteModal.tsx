import { AlertTriangle, Trash2 } from "lucide-react";
import { Card, Button } from "../ui";
import type { CatalogLens, CatalogDetector } from "../../utils/api";

interface Props {
  item: CatalogLens | CatalogDetector | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function LibraryDeleteModal({ item, onConfirm, onCancel }: Props) {
  if (!item) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-6">
      <Card className="w-full max-w-sm animate-fade-in">
        <div className="flex items-start gap-3 mb-4">
          <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-900/20 text-rose-500">
            <AlertTriangle size={16} />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">确认删除？</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              「{item.model}」将被永久删除，此操作不可撤销。
            </p>
          </div>
        </div>
        <div className="flex items-center justify-end gap-2">
          <Button variant="ghost" size="sm" onClick={onCancel}>
            取消
          </Button>
          <Button variant="danger" size="sm" leftIcon={<Trash2 size={14} />} onClick={onConfirm}>
            删除
          </Button>
        </div>
      </Card>
    </div>
  );
}
