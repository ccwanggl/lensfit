import LensImage from "./LensImage";
import { Badge } from "./ui";

interface ResultCardProps {
  rank: number;
  isSelected: boolean;
  onClick: () => void;
  lensModel: string;
  lensFocal: string;
  lensAperture: string;
  lensImageUrl?: string;
  detectorModel: string;
  badgeLabel: string;
  price: number;
  score: number;
  reasons: string[];
}

export default function ResultCard({
  rank,
  isSelected,
  onClick,
  lensModel,
  lensFocal,
  lensAperture,
  lensImageUrl,
  detectorModel,
  badgeLabel,
  price,
  score,
  reasons,
}: ResultCardProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 focus-ring ${
        isSelected
          ? "border-indigo-300 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/30 shadow-sm"
          : "border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-200 hover:shadow-sm"
      }`}
    >
      <div className="flex items-center gap-3">
        <span
          className={`flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
            rank === 1
              ? "bg-gradient-to-br from-amber-400 to-amber-500 text-white"
              : rank === 2
              ? "bg-gradient-to-br from-slate-300 to-slate-400 text-white"
              : rank === 3
              ? "bg-gradient-to-br from-orange-300 to-orange-400 text-white"
              : "bg-slate-100 text-slate-500"
          }`}
        >
          {rank}
        </span>

        <LensImage
          model={lensModel}
          focal={lensFocal}
          aperture={lensAperture}
          brand=""
          imageUrl={lensImageUrl}
          size="sm"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-0.5">
            <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">
              {lensModel}
            </h4>
            <span className="text-base font-extrabold text-indigo-600 tabular-nums">
              {score.toFixed(0)}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
            <Badge variant="neutral" size="sm">
              {badgeLabel}
            </Badge>
            <span className="text-slate-400 dark:text-slate-500">·</span>
            <span>{detectorModel}</span>
            <span className="text-slate-400 dark:text-slate-500">·</span>
            <span className="font-semibold text-slate-700 dark:text-slate-200">${price.toFixed(0)}</span>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap mt-1.5">
            {reasons.slice(0, 3).map((reason, i) => (
              <Badge key={i} variant="success" size="sm">
                {reason}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </button>
  );
}
