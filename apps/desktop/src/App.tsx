import { useState, Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Monitor, Microscope, Sun, Camera, Moon, User, FolderOpen, Loader2, GraduationCap, TrendingUp, Settings, Database } from "lucide-react";
import ToastContainer from "./components/ui/Toast";
import { useTheme } from "./hooks/useTheme";
import { LearningModeProvider, useLearningMode } from "./contexts/LearningModeContext";
import SettingsPanel from "./components/SettingsPanel";
import { useAppStore, type AppTabId } from "./stores/appStore";

const IndustrialPage = lazy(() => import("./pages/IndustrialPage"));
const MicroscopePage = lazy(() => import("./pages/MicroscopePage"));
const InfraredPage = lazy(() => import("./pages/InfraredPage"));
const PhotographyPage = lazy(() => import("./pages/PhotographyPage"));
const ProjectsPage = lazy(() => import("./pages/ProjectsPage"));
const LibraryPage = lazy(() => import("./pages/LibraryPage"));
const FormulaPlayground = lazy(() => import("./components/FormulaPlayground"));
const LearningHub = lazy(() => import("./lab/LearningHub"));

const queryClient = new QueryClient();

interface NavTab {
  id: AppTabId;
  label: string;
  icon: React.ReactNode;
}

interface NavGroup {
  id: string;
  label: string;
  tabs: NavTab[];
}

/**
 * 阶段 4（应用壳导航反转）：学习中心为默认首页；
 * 导航分三组——学习（学习中心）、实践场（四领域工作台）、工具（项目/器件库/游乐场）。
 * 设置经右上角图标进入，不占 Tab。
 */
const NAV_GROUPS: NavGroup[] = [
  {
    id: "learn",
    label: "学习",
    tabs: [{ id: "learning", label: "学习中心", icon: <GraduationCap size={16} /> }],
  },
  {
    id: "practice",
    label: "实践场",
    tabs: [
      { id: "industrial", label: "工业视觉", icon: <Monitor size={16} /> },
      { id: "photography", label: "摄影", icon: <Camera size={16} /> },
      { id: "microscope", label: "显微镜", icon: <Microscope size={16} /> },
      { id: "infrared", label: "红外成像", icon: <Sun size={16} /> },
    ],
  },
  {
    id: "tools",
    label: "工具",
    tabs: [
      { id: "projects", label: "项目", icon: <FolderOpen size={16} /> },
      { id: "library", label: "器件库", icon: <Database size={16} /> },
      { id: "playground", label: "游乐场", icon: <TrendingUp size={16} /> },
    ],
  },
];

function AppContent() {
  const activeTab = useAppStore((s) => s.activeTab);
  const setActiveTab = useAppStore((s) => s.setActiveTab);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const { theme, toggle } = useTheme();
  const { learningMode } = useLearningMode();

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300"
      style={{ background: theme === "dark" ? "linear-gradient(180deg, #020617 0%, #0f172a 100%)" : "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)" }}>

      {/* Glass Header */}
      <header className="glass sticky top-0 z-50 transition-colors duration-300">
        <div className="max-w-[1440px] mx-auto px-6">
          <div className="flex items-center justify-between h-[60px]">
            {/* Brand */}
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-[0_2px_8px_rgba(99,102,241,0.3)]">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 2v4" /><path d="M12 18v4" />
                  <path d="m4.93 4.93 2.83 2.83" /><path d="m16.24 16.24 2.83 2.83" />
                  <path d="M2 12h4" /><path d="M18 12h4" />
                  <path d="m4.93 19.07 2.83-2.83" /><path d="m16.24 7.76 2.83-2.83" />
                </svg>
              </div>
              <div>
                <h1 className="text-[15px] font-extrabold text-slate-900 dark:text-slate-100 leading-none tracking-tight">OptiBench</h1>
                <p className="text-xs text-slate-400 dark:text-slate-500 font-medium leading-none mt-0.5 tracking-wide uppercase">光学学习</p>
              </div>
            </div>

            {/* Tab Navigation: 学习 / 实践场 / 工具 三组 */}
            <nav className="flex items-center gap-0.5 bg-slate-100/80 dark:bg-slate-800/80 rounded-xl p-1">
              {NAV_GROUPS.map((group, gi) => (
                <div key={group.id} className="flex items-center gap-0.5">
                  {gi > 0 && (
                    <span className="mx-1 h-5 w-px bg-slate-300/70 dark:bg-slate-600/70" aria-hidden="true" />
                  )}
                  <span className="hidden lg:block px-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                    {group.label}
                  </span>
                  {group.tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`
                          relative flex items-center gap-2 px-4 py-2 rounded-[10px] text-sm font-semibold
                          transition-all duration-200 ease-out
                          ${isActive
                            ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-[0_1px_3px_rgba(0,0,0,0.08)]"
                            : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-slate-700/50"
                          }
                        `}
                      >
                        <span className={isActive ? "text-indigo-500" : "text-slate-400 dark:text-slate-500"}>{tab.icon}</span>
                        {tab.label}

                      </button>
                    );
                  })}
                </div>
              ))}
            </nav>

            {/* Right side */}
            <div className="flex items-center gap-2">
              {learningMode && (
                <span className="hidden sm:inline-flex items-center gap-1 px-2 py-1 rounded-md bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-800/30 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
                  <GraduationCap size={12} />
                  学习辅助
                </span>
              )}
              <button
                onClick={() => setSettingsOpen(true)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title="设置" aria-label="设置"
              >
                <Settings size={16} />
              </button>
              <button
                onClick={toggle}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title={theme === "dark" ? "切换到亮色模式" : "切换到暗色模式"}
                aria-label={theme === "dark" ? "切换到亮色模式" : "切换到暗色模式"}
              >
                {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
              </button>
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 dark:from-indigo-900/30 dark:to-violet-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 text-xs font-bold">
                <User size={14} />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Learning-aid Notice */}
      {learningMode && (
        <div className="bg-emerald-50 dark:bg-emerald-900/20 border-b border-emerald-100 dark:border-emerald-800/30">
          <div className="max-w-[1440px] mx-auto px-6 py-2 flex items-center gap-2 text-xs text-emerald-700 dark:text-emerald-400">
            <GraduationCap size={14} />
            <span className="font-medium">实践场学习辅助已开启</span>
            <span className="text-emerald-600/70 dark:text-emerald-400/70">实践场工作台中参数旁会出现提示图标，知识面板会高亮并展开相关学习章节。</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 max-w-[1440px] w-full mx-auto px-6 py-6">
        <Suspense
          fallback={(
            <div className="flex items-center justify-center h-[60vh]">
              <Loader2 className="animate-spin text-indigo-500" size={32} />
            </div>
          )}
        >
          {activeTab === "industrial" && <IndustrialPage />}
          {activeTab === "photography" && <PhotographyPage />}
          {activeTab === "microscope" && <MicroscopePage />}
          {activeTab === "infrared" && <InfraredPage />}
          {activeTab === "projects" && <ProjectsPage />}
          {activeTab === "library" && <LibraryPage />}
          {activeTab === "playground" && <FormulaPlayground />}
          {activeTab === "learning" && <LearningHub />}
        </Suspense>
      </main>

      <SettingsPanel open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <LearningModeProvider>
        <AppContent />
        <ToastContainer />
      </LearningModeProvider>
    </QueryClientProvider>
  );
}

export default App;
