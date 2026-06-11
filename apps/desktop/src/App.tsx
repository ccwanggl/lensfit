import { useState, Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Monitor, Microscope, Sun, Camera, Moon, User, FolderOpen, Loader2, GraduationCap } from "lucide-react";
import ToastContainer from "./components/ui/Toast";
import { useTheme } from "./hooks/useTheme";
import { LearningModeProvider, useLearningMode } from "./contexts/LearningModeContext";

const IndustrialPage = lazy(() => import("./pages/IndustrialPage"));
const MicroscopePage = lazy(() => import("./pages/MicroscopePage"));
const InfraredPage = lazy(() => import("./pages/InfraredPage"));
const PhotographyPage = lazy(() => import("./pages/PhotographyPage"));
const ProjectsPage = lazy(() => import("./pages/ProjectsPage"));

const queryClient = new QueryClient();

type TabId = "industrial" | "microscope" | "infrared" | "photography" | "projects";

const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
  { id: "industrial", label: "工业视觉", icon: <Monitor size={16} /> },
  { id: "photography", label: "摄影", icon: <Camera size={16} /> },
  { id: "microscope", label: "显微镜", icon: <Microscope size={16} /> },
  { id: "infrared", label: "红外成像", icon: <Sun size={16} /> },
  { id: "projects", label: "项目", icon: <FolderOpen size={16} /> },
];

function AppContent() {
  const [activeTab, setActiveTab] = useState<TabId>("industrial");
  const { theme, toggle } = useTheme();
  const { learningMode, setLearningMode } = useLearningMode();

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
                <h1 className="text-[15px] font-extrabold text-slate-900 dark:text-slate-100 leading-none tracking-tight">LensFit</h1>
                <p className="text-xs text-slate-400 dark:text-slate-500 font-medium leading-none mt-0.5 tracking-wide uppercase">光学选型</p>
              </div>
            </div>

            {/* Tab Navigation */}
            <nav className="flex items-center gap-0.5 bg-slate-100/80 dark:bg-slate-800/80 rounded-xl p-1">
              {tabs.map((tab) => {
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
            </nav>

            {/* Right side */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setLearningMode(!learningMode)}
                className={`h-8 px-2.5 rounded-lg flex items-center gap-1.5 text-xs font-semibold transition-colors border ${learningMode ? "bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-900/30 dark:border-emerald-800/40 dark:text-emerald-400" : "border-transparent text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"}`}
                title={learningMode ? "当前为学习模式" : "切换到学习模式"}
              >
                <GraduationCap size={14} />
                <span>{learningMode ? "学习模式" : "学习"}</span>
              </button>
              <button
                onClick={toggle}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                title={theme === "dark" ? "切换到亮色模式" : "切换到暗色模式"}
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
        </Suspense>
      </main>
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
