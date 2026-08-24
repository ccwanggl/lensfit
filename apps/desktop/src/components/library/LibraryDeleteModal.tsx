import { AlertTriangle, Trash2 } from "lucide-react";
import { Modal, Button } from "../ui";
import type { CatalogLens, CatalogDetector } from "../../utils/api";

interface Props {
  item: CatalogLens | CatalogDetector | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function LibraryDeleteModal({ item, onConfirm, onCancel }: Props) {
  return (
    <Modal
      open={item !== null}
      onClose={onCancel}
      title="确认删除？"
      widthClass="max-w-sm"
      footer={
        <>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            取消
          </Button>
          <Button variant="danger" size="sm" leftIcon={<Trash2 size={14} />} onClick={onConfirm}>
            删除
          </Button>
        </>
      }
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-900/20 text-rose-500">
          <AlertTriangle size={16} />
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          「{item?.model}」将被永久删除，此操作不可撤销。
        </p>
      </div>
    </Modal>
  );
}
