import { useState, useEffect, useCallback, useMemo } from "react";
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
  Search,
  Trash2,
  AlertTriangle,
  FileText,
  ChevronRight,
  Activity,
  Eye,
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
  deleteProject,
  listSetups,
  deleteSetup,
  listLenses,
  listDetectors,
  generateProjectReport,
} from "../utils/api";
import { toast } from "../hooks/useToast";
import { type InputChangeEvent } from "../components/ui/Input";
import type { SetupItem } from "../utils/api";

interface Project {
  id: number;
  name: string;
  description?: string;
  domain: string;
  created_at?: string;
}

interface LensItem {
  id: number;
  model: string;
  category: string;
  price_usd?: number;
}

interface DetectorItem {
  id: number;
  model: string;
  category: string;
  price_usd?: number;
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

function formatDate(iso: string | undefined | null) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getSnapshotDrift(
  current: LensItem | DetectorItem | undefined,
  snapshot: Record<string, unknown> | null | undefined
): { drifted: boolean; fields: string[] } {
  if (!snapshot || !current) return { drifted: false, fields: [] };
  const fields: string[] = [];
  if (snapshot.model !== current.model) fields.push("model");
  if (
    snapshot.price_usd != null &&
    current.price_usd != null &&
    Number(snapshot.price_usd) !== Number(current.price_usd)
  ) {
    fields.push("price_usd");
  }
  return { drifted: fields.length > 0, fields };
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [setups, setSetups] = useState<SetupItem[]>([]);
  const [lenses, setLenses] = useState<LensItem[]>([]);
  const [detectors, setDetectors] = useState<DetectorItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState("");
  const [domainFilter, setDomainFilter] = useState<string>("all");
  const [selectedSetup, setSelectedSetup] = useState<SetupItem | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ type: "project" | "setup"; id: number; name: string } | null>(null);

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
      toast("error", "加载失败", "无法获取项目列表");
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
      setSelectedSetup(null);
      return;
    }
    setSelectedSetup(null);
    const load = async () => {
      setLoading(true);
      try {
        const data = await listSetups(selectedProject.id);
        setSetups(data.items || []);
      } catch (e) {
        console.error("Load setups failed:", e);
        toast("error", "加载失败", "无法获取方案列表");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [selectedProject]);

  const filteredProjects = useMemo(() => {
    const term = search.trim().toLowerCase();
    return projects.filter((p) => {
      const matchesSearch =
        !term ||
        p.name.toLowerCase().includes(term) ||
        (p.description ?? "").toLowerCase().includes(term);
      const matchesDomain = domainFilter === "all" || p.domain === domainFilter;
      return matchesSearch && matchesDomain;
    });
  }, [projects, search, domainFilter]);

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

  const handleDeleteProject = async () => {
    if (!deleteConfirm) return;
    try {
      await deleteProject(deleteConfirm.id);
      toast("success", "已删除", `项目「${deleteConfirm.name}」已删除`);
      if (selectedProject?.id === deleteConfirm.id) {
        setSelectedProject(null);
      }
      loadProjects();
    } catch (e) {
      toast("error", "删除失败", "无法删除项目");
    } finally {
      setDeleteConfirm(null);
    }
  };

  const handleDeleteSetup = async () => {
    if (!deleteConfirm || !selectedProject) return;
    try {
      await deleteSetup(selectedProject.id, deleteConfirm.id);
      toast("success", "已删除", `方案「${deleteConfirm.name}」已删除`);
      setSetups((prev) => prev.filter((s) => s.id !== deleteConfirm.id));
      if (selectedSetup?.id === deleteConfirm.id) {
        setSelectedSetup(null);
      }
    } catch (e) {
      toast("error", "删除失败", "无法删除方案");
    } finally {
      setDeleteConfirm(null);
    }
  };

  const handleExportProjectReport = async (format: "pdf" | "excel") => {
    if (!selectedProject) return;
    try {
      const blob = await generateProjectReport(selectedProject.id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = format === "pdf" ? `project-${selectedProject.id}-report.pdf` : `project-${selectedProject.id}-report.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast("success", "导出成功", `${format.toUpperCase()} 报告已下载`);
    } catch (e) {
      console.error("Export project report failed:", e);
      toast("error", "导出失败", "无法生成项目报告");
    }
  };

  const getLens = (id: number | null | undefined) =>
    id ? lenses.find((l) => l.id === id) : undefined;

  const getDetector = (id: number | null | undefined) =>
    id ? detectors.find((d) => d.id === id) : undefined;

  const getLensModel = (id: number | null | undefined) => {
    if (!id) return "—";
    return getLens(id)?.model || `镜头 #${id}`;
  };

  const getDetectorModel = (id: number | null | undefined) => {
    if (!id) return "—";
    return getDetector(id)?.model || `探测器 #${id}`;
  };

  const selectedLens = selectedSetup?.lens_id ? getLens(selectedSetup.lens_id) : undefined;
  const selectedDetector = selectedSetup?.detector_id ? getDetector(selectedSetup.detector_id) : undefined;
  const lensDrift = getSnapshotDrift(selectedLens, selectedSetup?.lens_snapshot);
  const detectorDrift = getSnapshotDrift(selectedDetector, selectedSetup?.detector_snapshot);

  return (
    <div className="grid grid-cols-12 gap-5">
      {/* ── Left: Project List ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title="项目列表"
              subtitle={`${filteredProjects.length} / ${projects.length} 个项目`}
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

          <div className="p-3 space-y-2 border-b border-slate-100 dark:border-slate-700">
            <Input
              placeholder="搜索项目名称或描述"
              icon={<Search size={14} />}
              value={search}
              onChange={(e: InputChangeEvent) => setSearch(e.target.value)}
            />
            <div className="flex items-center gap-2">
              {(["all", "industrial", "photography", "microscope", "infrared"] as const).map((d) => (
                <button
                  key={d}
                  onClick={() => setDomainFilter(d)}
                  className={`text-[10px] px-2 py-1 rounded-md transition-colors ${
                    domainFilter === d
                      ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 font-semibold"
                      : "bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
                  }`}
                >
                  {d === "all" ? "全部" : DOMAIN_LABELS[d] || d}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {filteredProjects.length === 0 && (
              <div className="flex-1 flex items-center justify-center h-48">
                <EmptyState
                  icon={<FolderOpen size={24} />}
                  title="暂无项目"
                  description={search || domainFilter !== "all" ? "没有匹配当前筛选的项目" : "点击右上角「新建」创建您的第一个选型项目"}
                />
              </div>
            )}

            {filteredProjects.map((p) => (
              <div
                key={p.id}
                role="button"
                tabIndex={0}
                onClick={() => setSelectedProject(p)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    setSelectedProject(p);
                  }
                }}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-200 group ${
                  selectedProject?.id === p.id
                    ? "border-indigo-300 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/20 shadow-sm"
                    : "border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-sm"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">{p.name}</h4>
                  <div className="flex items-center gap-1">
                    <Badge
                      variant="neutral"
                      size="sm"
                      className={DOMAIN_COLORS[p.domain] || ""}
                    >
                      {DOMAIN_LABELS[p.domain] || p.domain}
                    </Badge>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteConfirm({ type: "project", id: p.id, name: p.name });
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-all"
                      title="删除项目"
                      aria-label="删除项目"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>
                {p.description && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate mb-1.5">{p.description}</p>
                )}
                <div className="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500">
                  <Calendar size={10} />
                  <span>{formatDate(p.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* ── Center: Setup List ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title={selectedProject ? selectedProject.name : "方案详情"}
              subtitle={selectedProject ? `${setups.length} 个保存的方案` : "选择项目查看方案"}
              icon={<Layers size={16} />}
            />
            {selectedProject && (
              <div className="flex items-center gap-1">
                <Badge
                  variant="neutral"
                  size="sm"
                  className={DOMAIN_COLORS[selectedProject.domain] || ""}
                >
                  {DOMAIN_LABELS[selectedProject.domain] || selectedProject.domain}
                </Badge>
              </div>
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
            ) : loading ? (
              <div className="flex-1 flex items-center justify-center h-64">
                <EmptyState icon={<Activity size={24} />} title="加载中" description="正在读取方案列表..." />
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
                    role="button"
                    tabIndex={0}
                    onClick={() => setSelectedSetup(s)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setSelectedSetup(s);
                      }
                    }}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-200 group ${
                      selectedSetup?.id === s.id
                        ? "border-indigo-300 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/20 shadow-sm"
                        : "border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-sm"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">{s.name}</h4>
                      <div className="flex items-center gap-1">
                        <ChevronRight size={14} className={`text-slate-300 transition-transform ${selectedSetup?.id === s.id ? "rotate-90" : ""}`} />
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirm({ type: "setup", id: s.id, name: s.name });
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-all"
                          title="删除方案"
                          aria-label="删除方案"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                        <Package size={12} className="text-indigo-500" />
                        <span className="truncate">{getLensModel(s.lens_id)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                        <Camera size={12} className="text-emerald-500" />
                        <span className="truncate">{getDetectorModel(s.detector_id)}</span>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center gap-1 text-[10px] text-slate-400 dark:text-slate-500">
                      <Calendar size={10} />
                      <span>{formatDate(s.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* ── Right: Setup Detail ── */}
      <div className="col-span-4">
        <Card padding="none" className="overflow-hidden h-full flex flex-col">
          <div className="p-5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
            <SectionHeader
              title={selectedSetup ? selectedSetup.name : "方案快照"}
              subtitle={selectedSetup ? "目录数据与保存快照对比" : "选择方案查看详情"}
              icon={<Eye size={16} />}
            />
            {selectedProject && setups.length > 0 && (
              <div className="flex items-center gap-1">
                <button
                  title="导出 PDF"
                  onClick={() => handleExportProjectReport("pdf")}
                  className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors"
                >
                  <FileText size={14} />
                </button>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {!selectedSetup ? (
              <div className="flex-1 flex items-center justify-center h-64">
                <EmptyState
                  icon={<Eye size={24} />}
                  title="选择方案"
                  description="点击左侧方案卡片查看镜头、探测器和匹配结果快照"
                />
              </div>
            ) : (
              <div className="space-y-4">
                {(lensDrift.drifted || detectorDrift.drifted) && (
                  <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800/30 flex items-start gap-2.5">
                    <AlertTriangle size={14} className="text-amber-500 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs font-semibold text-amber-700 dark:text-amber-300">检测到数据漂移</p>
                      <p className="text-[11px] text-amber-600 dark:text-amber-400 mt-0.5">
                        {[
                          lensDrift.drifted && `镜头 ${lensDrift.fields.join(", ")}`,
                          detectorDrift.drifted && `探测器 ${detectorDrift.fields.join(", ")}`,
                        ]
                          .filter(Boolean)
                          .join("；")}
                        与保存快照不一致
                      </p>
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">镜头信息</h4>
                  <div className="p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 dark:text-slate-400">当前目录</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[180px]">{getLensModel(selectedSetup.lens_id)}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 dark:text-slate-400">保存快照</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[180px]">
                        {(selectedSetup.lens_snapshot?.model as string) || "—"}
                      </span>
                    </div>
                    {selectedSetup.lens_snapshot?.price_usd != null && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500 dark:text-slate-400">快照价格</span>
                        <span className="font-medium text-slate-800 dark:text-slate-200">${Number(selectedSetup.lens_snapshot.price_usd).toFixed(0)}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">探测器信息</h4>
                  <div className="p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 dark:text-slate-400">当前目录</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[180px]">{getDetectorModel(selectedSetup.detector_id)}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 dark:text-slate-400">保存快照</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-[180px]">
                        {(selectedSetup.detector_snapshot?.model as string) || "—"}
                      </span>
                    </div>
                    {selectedSetup.detector_snapshot?.price_usd != null && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500 dark:text-slate-400">快照价格</span>
                        <span className="font-medium text-slate-800 dark:text-slate-200">${Number(selectedSetup.detector_snapshot.price_usd).toFixed(0)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {selectedSetup.match_result_snapshot && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">匹配结果快照</h4>
                    <div className="p-3 rounded-xl bg-slate-50/80 dark:bg-slate-800/80 border border-slate-100 dark:border-slate-700 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500 dark:text-slate-400">综合得分</span>
                        <span className="font-bold text-indigo-600 dark:text-indigo-400">
                          {Number(selectedSetup.match_result_snapshot.score ?? 0).toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-500 dark:text-slate-400">覆盖比</span>
                        <span className="font-medium text-slate-800 dark:text-slate-200">
                          {((Number(selectedSetup.match_result_snapshot.coverage_ratio ?? 0)) * 100).toFixed(0)}%
                        </span>
                      </div>
                      {typeof selectedSetup.match_result_snapshot.reason === "string" && (
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                          {selectedSetup.match_result_snapshot.reason}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {selectedSetup.notes && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">备注</h4>
                    <p className="text-xs text-slate-600 dark:text-slate-400 whitespace-pre-wrap">{selectedSetup.notes}</p>
                  </div>
                )}
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
                type="button"
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
                <Button type="button" variant="ghost" size="sm" onClick={() => setShowCreate(false)}>
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

      {/* ── Delete Confirm Modal ── */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <Card className="w-full max-w-sm animate-fade-in">
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-900/20 text-rose-500">
                <AlertTriangle size={16} />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  确认删除{deleteConfirm.type === "project" ? "项目" : "方案"}？
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  「{deleteConfirm.name}」将被永久删除，此操作不可撤销。
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setDeleteConfirm(null)}>
                取消
              </Button>
              <Button
                variant="danger"
                size="sm"
                leftIcon={<Trash2 size={14} />}
                onClick={deleteConfirm.type === "project" ? handleDeleteProject : handleDeleteSetup}
              >
                删除
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
