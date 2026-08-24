import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { Button, Input, Modal } from "./ui";
import { type InputChangeEvent } from "./ui/Input";
import { listProjects, createProject, saveSetup } from "../utils/api";
import { toast } from "../hooks/useToast";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  lensId?: number;
  detectorId?: number;
  matchResultSnapshot?: object;
}

interface Project {
  id: number;
  name: string;
  description?: string;
  domain?: string;
}

export default function SaveToProjectDialog({
  isOpen,
  onClose,
  lensId,
  detectorId,
  matchResultSnapshot,
}: Props) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [newProjectName, setNewProjectName] = useState("");
  const [mode, setMode] = useState<"select" | "create">("select");

  useEffect(() => {
    if (!isOpen) {
      // Reset state when dialog closes
      setSelectedProjectId(null);
      setNewProjectName("");
      setMode("select");
      return;
    }
    setLoading(true);
    listProjects()
      .then((data) => {
        setProjects(data.items ?? []);
        if (data.items?.length > 0) {
          setSelectedProjectId(data.items[0].id);
        }
      })
      .catch(() => toast("error", "加载失败", "无法获取项目列表"))
      .finally(() => setLoading(false));
  }, [isOpen]);

  const handleSave = async () => {
    let projectId = selectedProjectId;
    if (mode === "create") {
      if (!newProjectName.trim()) {
        toast("error", "请输入项目名称");
        return;
      }
      try {
        const project = await createProject({ name: newProjectName.trim(), domain: "industrial" });
        projectId = project.id;
      } catch {
        toast("error", "创建失败", "无法创建新项目");
        return;
      }
    }
    if (!projectId) {
      toast("error", "请选择或创建一个项目");
      return;
    }
    setSaving(true);
    try {
      await saveSetup(projectId, {
        name: `方案 ${new Date().toLocaleString("zh-CN")}`,
        lens_id: lensId,
        detector_id: detectorId,
        match_result_snapshot: matchResultSnapshot,
      });
      toast("success", "保存成功", "方案已保存到项目");
      onClose();
    } catch {
      toast("error", "保存失败", "无法保存方案");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      title="保存到项目"
      widthClass="max-w-sm"
      footer={
        loading ? undefined : (
          <>
            <Button variant="ghost" size="sm" onClick={onClose}>取消</Button>
            <Button variant="primary" size="sm" loading={saving} onClick={handleSave}>保存</Button>
          </>
        )
      }
    >
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 size={20} className="animate-spin text-indigo-500" />
        </div>
      ) : (
        <>
          <div className="flex items-center gap-2 mb-3">
            <button
              onClick={() => setMode("select")}
              aria-pressed={mode === "select"}
              className={`text-xs px-2.5 py-1 rounded-full transition-colors ${
                mode === "select"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              选择项目
            </button>
            <button
              onClick={() => setMode("create")}
              aria-pressed={mode === "create"}
              className={`text-xs px-2.5 py-1 rounded-full transition-colors ${
                mode === "create"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              新建项目
            </button>
          </div>

          {mode === "select" ? (
            <div className="space-y-1.5 max-h-[200px] overflow-y-auto">
              {projects.length === 0 && (
                <p className="text-xs text-slate-400 dark:text-slate-500 py-4 text-center">暂无项目，请新建</p>
              )}
              {projects.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProjectId(p.id)}
                  aria-pressed={selectedProjectId === p.id}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors ${
                    selectedProjectId === p.id
                      ? "bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-200 dark:border-indigo-800/40 text-indigo-700 dark:text-indigo-300"
                      : "bg-slate-50 dark:bg-slate-800 border border-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                  }`}
                >
                  <span className="font-semibold">{p.name}</span>
                  {p.description && <span className="text-slate-400 dark:text-slate-500 ml-2">{p.description}</span>}
                </button>
              ))}
            </div>
          ) : (
            <Input
              label="项目名称"
              value={newProjectName}
              onChange={(e: InputChangeEvent) => setNewProjectName(e.target.value)}
              placeholder="输入项目名称..."
            />
          )}
        </>
      )}
    </Modal>
  );
}
