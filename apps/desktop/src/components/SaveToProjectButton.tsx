import { useState, useEffect } from "react";
import { Bookmark, Plus, FolderOpen } from "lucide-react";
import { Button, Input, Badge, Modal } from "./ui";
import { type InputChangeEvent } from "./ui/Input";
import { listProjects, saveSetup } from "../utils/api";
import { toast } from "../hooks/useToast";

interface Project {
  id: number;
  name: string;
  domain: string;
}

interface SaveToProjectButtonProps {
  lensId: number | null;
  detectorId: number | null;
  lensModel: string;
  detectorModel: string;
  disabled?: boolean;
}

export default function SaveToProjectButton({
  lensId,
  detectorId,
  lensModel,
  detectorModel,
  disabled = false,
}: SaveToProjectButtonProps) {
  const [showModal, setShowModal] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [setupName, setSetupName] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!showModal) return;
    const load = async () => {
      try {
        const data = await listProjects();
        setProjects(data.items || []);
      } catch (e) {
        console.error("Load projects failed:", e);
      }
    };
    load();
    // Auto-generate name
    setSetupName(`${lensModel} + ${detectorModel}`);
  }, [showModal, lensModel, detectorModel]);

  const handleSave = async () => {
    if (!selectedProjectId || !setupName.trim()) return;
    setSaving(true);
    try {
      await saveSetup(selectedProjectId, {
        name: setupName.trim(),
        lens_id: lensId || undefined,
        detector_id: detectorId || undefined,
      });
      toast("success", "保存成功", `方案已保存到项目「${projects.find((p) => p.id === selectedProjectId)?.name}」`);
      setShowModal(false);
    } catch (e) {
      toast("error", "保存失败", "无法保存方案");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        leftIcon={<Bookmark size={14} />}
        onClick={() => setShowModal(true)}
        disabled={disabled}
      >
        保存
      </Button>

      <Modal
        open={showModal}
        onClose={() => setShowModal(false)}
        title="保存到项目"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setShowModal(false)}>
              取消
            </Button>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus size={14} />}
              onClick={handleSave}
              loading={saving}
              disabled={!selectedProjectId || !setupName.trim()}
            >
              保存
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="方案名称"
            value={setupName}
            onChange={(e: InputChangeEvent) => setSetupName(e.target.value)}
            placeholder="输入方案名称"
          />

          <div>
            <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2">
              选择项目
            </label>
            {projects.length === 0 ? (
              <div className="p-4 rounded-xl border border-dashed border-slate-200 dark:border-slate-700 text-center">
                <p className="text-xs text-slate-400 dark:text-slate-500">暂无项目，请先在「项目」页面创建</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {projects.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedProjectId(p.id)}
                    aria-pressed={selectedProjectId === p.id}
                    className={`w-full text-left p-3 rounded-xl border transition-all ${
                      selectedProjectId === p.id
                        ? "border-indigo-300 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/20"
                        : "border-slate-100 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-700"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <FolderOpen size={14} className="text-slate-400 dark:text-slate-500" />
                      <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{p.name}</span>
                      {selectedProjectId === p.id && (
                        <Badge variant="info" size="sm">已选</Badge>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </Modal>
    </>
  );
}
