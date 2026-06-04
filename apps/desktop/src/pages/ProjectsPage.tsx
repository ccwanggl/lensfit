import { useState, useEffect, useCallback } from "react";
import {
  FolderOpen,
  Plus,
  Save,

  Package,
  Camera,
  Calendar,

  X,

  HardDrive,
  Layers,
} from "lucide-react";
import {
  Card,
  Button,
  Input,
  Badge,
  SectionHeader,
  EmptyState,
} from "../components/ui";
import {
  listProjects,
  createProject,
  listSetups,

  listLenses,
  listDetectors,
} from "../utils/api";
import { toast } from "../hooks/useToast";
import { type InputChangeEvent } from "../components/ui/Input";

interface Project {
  id: number;
  name: string;
  description?: string;
  domain: string;
  created_at?: string;
}

interface Setup {
  id: number;
  project_id: number;
  name: string;
  lens_id?: number;
  detector_id?: number;
  created_at?: string;
}

interface LensItem {
  id: number;
  model: string;
  category: string;
}

interface DetectorItem {
  id: number;
  model: string;
  category: string;
}

const DOMAIN_LABELS: Record<string, string> = {
  industrial: "工业视觉",
  photography: "摄影",
  microscope: "显微镜",
  infrared: "红外成像",
};

const DOMAIN_COLORS: Record<string, string> = {
  industrial: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  photography: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  microscope: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  infrared: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [setups, setSetups] = useState<Setup[]>([]);
  const [lenses, setLenses] = useState<LensItem[]>([]);
  const [detectors, setDetectors] = useState<DetectorItem[]>([]);
  // loading state reserved
  const [showCreate, setShowCreate] = useState(false);

  const [newProject, setNewProject] = useState({
    name: "",
    description: "",
    domain: "industrial",
  });

  const loadProjects = useCallback(async () => {
    try {
      const data = await listProjects();
      setProjects(data.items || []);
    } catch (e) {
      console.error("Load projects failed:", e);
    }
  }, []);

  const loadCatalog = useCallback(async () => {
    try {
      const [lData, dData] = await Promise.all([
        listLenses({ limit: 500 }),
        listDetectors({ limit: 500 }),
      ]);
      setLenses((lData.items || []).map((l) => ({ id: l.id, model: l.model, category: l.category })));
      setDetectors((dData.items || []).map((d) => ({ id: d.id, model: d.model, category: d.category })));
    } catch (e) {
      console.error("Load catalog failed:", e);
    }
  }, []);

  useEffect(() => {
    loadProjects();
    loadCatalog();
  }, [loadProjects, loadCatalog]);

  useEffect(() => {
    if (!selectedProject) {
      setSetups([]);
      return;
    }
    const load = async () => {
      try {
        const data = await listSetups(selectedProject.id);
        setSetups(data.items || []);
      } catch (e) {
        console.error("Load setups failed:", e);
      }
    };
    load();
  }, [selectedProject]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProject.name.trim()) return;
    try {
      await createProject(newProject);
      toast("success", "创建成功", `项目「${newProject.name}」已创建`);
      setNewProject({ name: "", description: "", domain: "industrial" });
      setShowCreate(false);
      loadProjects();
    } catch (e) {
      toast("error", "创建失败", "无法创建项目");
    }
  };

  const getLensModel = (id: number | null) => {
    if (!id) return "—";
    return lenses.find((l) => l.id === id)?.model || `镜头 #${id}`;
  };

  const getDetectorModel = (id: number | null) => {
    if (!id) return "—";
    return detectors.find((d) => d.id === id)?.model || `探测器 #${id}`;
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="grid grid-cols-12 gap-5">
      {/* ── Left: Project List ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title="项目列表"
              subtitle={`${projects.length} 个项目`}
              icon={<FolderOpen size={16} />}
            />
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus size={14} />}
              onClick={() => setShowCreate(true)}
            >
              新建
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {projects.length === 0 && (
              <div className="flex-1 flex items-center justify-center h-48">
                <EmptyState
                  icon={<FolderOpen size={24} />}
                  title="暂无项目"
                  description="点击右上角「新建」创建您的第一个选型项目"
                />
              </div>
            )}

            {projects.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedProject(p)}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                  selectedProject?.id === p.id
                    ? "border-indigo-300 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/20 shadow-sm"
                    : "border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-sm"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">{p.name}</h4>
                  <Badge
                    variant="neutral"
                    size="sm"
                    className={DOMAIN_COLORS[p.domain] || ""}
                  >
                    {DOMAIN_LABELS[p.domain] || p.domain}
                  </Badge>
                </div>
                {p.description && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate mb-1.5">{p.description}</p>
                )}
                <div className="flex items-center gap-1 text-[10px] text-slate-400 dark:text-slate-500">
                  <Calendar size={10} />
                  <span>{formatDate(p.created_at ?? "")}</span>
                </div>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* ── Right: Setup List ── */}
      <div className="col-span-8">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title={selectedProject ? selectedProject.name : "方案详情"}
              subtitle={selectedProject ? `${setups.length} 个保存的方案` : "选择项目查看方案"}
              icon={<Layers size={16} />}
            />
            {selectedProject && (
              <Badge
                variant="neutral"
                size="sm"
                className={DOMAIN_COLORS[selectedProject.domain] || ""}
              >
                {DOMAIN_LABELS[selectedProject.domain] || selectedProject.domain}
              </Badge>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {!selectedProject ? (
              <div className="flex-1 flex items-center justify-center h-64">
                <EmptyState
                  icon={<HardDrive size={24} />}
                  title="选择项目"
                  description="在左侧选择项目，查看和管理保存的选型方案"
                />
              </div>
            ) : setups.length === 0 ? (
              <div className="flex-1 flex items-center justify-center h-64">
                <EmptyState
                  icon={<Save size={24} />}
                  title="暂无方案"
                  description="在各选型页面点击「保存到项目」，将方案收藏到这里"
                />
              </div>
            ) : (
              <div className="space-y-3">
                {setups.map((s) => (
                  <div
                    key={s.id}
                    className="p-4 rounded-xl border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 transition-all hover:shadow-sm"
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">{s.name}</h4>
                      <span className="text-[10px] text-slate-400 dark:text-slate-500 flex items-center gap-1">
                        <Calendar size={10} />
                        {formatDate(s.created_at ?? "")}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                        <Package size={12} className="text-indigo-500" />
                        <span className="truncate">{getLensModel(s.lens_id ?? null)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                        <Camera size={12} className="text-emerald-500" />
                        <span className="truncate">{getDetectorModel(s.detector_id ?? null)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* ── Create Project Modal ── */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <Card className="w-full max-w-md animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">新建项目</h3>
              <button
                onClick={() => setShowCreate(false)}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <Input
                label="项目名称"
                value={newProject.name}
                onChange={(e: InputChangeEvent) => setNewProject({ ...newProject, name: e.target.value })}
                placeholder="例如：产线视觉检测项目"
                required
              />
              <Input
                label="项目描述"
                value={newProject.description}
                onChange={(e: InputChangeEvent) => setNewProject({ ...newProject, description: e.target.value })}
                placeholder="可选：项目背景和需求描述"
              />
              <Input
                as="select"
                label="应用领域"
                value={newProject.domain}
                onChange={(e: InputChangeEvent) => setNewProject({ ...newProject, domain: e.target.value })}
              >
                <option value="industrial">工业视觉</option>
                <option value="photography">摄影</option>
                <option value="microscope">显微镜</option>
                <option value="infrared">红外成像</option>
              </Input>
              <div className="flex items-center justify-end gap-2 pt-2">
                <Button variant="ghost" size="sm" onClick={() => setShowCreate(false)}>
                  取消
                </Button>
                <Button type="submit" variant="primary" size="sm" leftIcon={<Plus size={14} />}>
                  创建
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
