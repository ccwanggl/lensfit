import { useToastStore } from "../../hooks/useToast";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  X,
} from "lucide-react";

const icons = {
  success: <CheckCircle2 size={18} className="text-emerald-500" />,
  error: <XCircle size={18} className="text-rose-500" />,
  warning: <AlertTriangle size={18} className="text-amber-500" />,
  info: <Info size={18} className="text-sky-500" />,
};

const bgColors = {
  success: "bg-emerald-50 border-emerald-200",
  error: "bg-rose-50 border-rose-200",
  warning: "bg-amber-50 border-amber-200",
  info: "bg-sky-50 border-sky-200",
};

export default function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts);
  const remove = useToastStore((s) => s.remove);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2.5 w-[340px]">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`
            flex items-start gap-3 p-4 rounded-xl border shadow-lg
            animate-slide-in-right
            ${bgColors[t.type]}
          `}
        >
          <div className="flex-shrink-0 mt-0.5">{icons[t.type]}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-800">{t.title}</p>
            {t.message && (
              <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{t.message}</p>
            )}
          </div>
          <button
            onClick={() => remove(t.id)}
            className="flex-shrink-0 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
