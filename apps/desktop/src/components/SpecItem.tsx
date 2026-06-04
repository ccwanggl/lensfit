interface SpecItemProps {
  label: string;
  value: string | number;
  helper?: string;
  highlight?: boolean;
}

export default function SpecItem({ label, value, helper, highlight }: SpecItemProps) {
  return (
    <div
      className={`p-3 rounded-[10px] border ${
        highlight
          ? "bg-indigo-50/60 dark:bg-indigo-900/20 border-indigo-100 dark:border-indigo-800/40"
          : "bg-slate-50/80 dark:bg-slate-800/50 border-slate-100 dark:border-slate-700"
      }`}
    >
      <p className="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
        {label}
      </p>
      <p
        className={`text-sm font-bold truncate ${
          highlight ? "text-indigo-700 dark:text-indigo-300" : "text-slate-800 dark:text-slate-200"
        }`}
      >
        {value}
      </p>
      {helper && <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">{helper}</p>}
    </div>
  );
}
