/** Breadboard preset schematic header (moved verbatim from LearningHub, slice B).
 *
 * Re-exported from LearningHub for backward-compatible test imports.
 */
import { WAVELENGTH_PRESETS } from "../workbenchTypes";

export function BreadboardPresetHeader({
  presetId,
  params,
  onChange,
}: {
  presetId: string;
  params: Record<string, unknown>;
  onChange: (name: string, value: unknown) => void;
}) {
  const screen_x_mm = Number(params.screen_x_mm ?? 1600);
  const wavelength_nm = Number(params.wavelength_nm ?? 550);
  const clamped = Math.min(Math.max(screen_x_mm, 700), 3000);
  const screenSvgX = 40 + ((clamped - 700) / (3000 - 700)) * 220;
  const isDoubleSlit = presetId === "double-slit-breadboard";

  return (
    <div className="mb-4 space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
          波长
        </span>
        {WAVELENGTH_PRESETS.map((preset) => {
          const active = wavelength_nm === preset.value;
          return (
            <button
              key={preset.value}
              onClick={() => onChange("wavelength_nm", preset.value)}
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
                active
                  ? "border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-800/40 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              <span className={`h-2 w-2 rounded-full ${preset.color}`} />
              {preset.label}
            </button>
          );
        })}
      </div>

      <div className="rounded-lg border border-slate-200/60 bg-slate-50/60 p-2 dark:border-slate-700/60 dark:bg-slate-800/60">
        <div className="mb-1 text-xs font-medium text-slate-600 dark:text-slate-400">
          面包板示意
        </div>
        <svg viewBox="0 0 300 70" className="h-16 w-full">
          <line
            x1="20"
            y1="50"
            x2="280"
            y2="50"
            className="text-slate-300 dark:text-slate-600"
            stroke="currentColor"
            strokeWidth="2"
          />
          <circle cx="20" cy="50" r="5" className="text-red-500" fill="currentColor" />
          <text
            x="20"
            y="65"
            textAnchor="middle"
            className="text-[8px] text-slate-500 dark:text-slate-400"
            fill="currentColor"
          >
            激光
          </text>
          {isDoubleSlit ? (
            <>
              <line
                x1="36"
                y1="35"
                x2="36"
                y2="50"
                className="text-slate-800 dark:text-slate-200"
                stroke="currentColor"
                strokeWidth="3"
              />
              <line
                x1="44"
                y1="35"
                x2="44"
                y2="50"
                className="text-slate-800 dark:text-slate-200"
                stroke="currentColor"
                strokeWidth="3"
              />
            </>
          ) : (
            <line
              x1="40"
              y1="35"
              x2="40"
              y2="50"
              className="text-slate-800 dark:text-slate-200"
              stroke="currentColor"
              strokeWidth="3"
            />
          )}
          <text
            x="40"
            y="65"
            textAnchor="middle"
            className="text-[8px] text-slate-500 dark:text-slate-400"
            fill="currentColor"
          >
            {isDoubleSlit ? "双缝" : "单缝"}
          </text>
          <line
            x1={screenSvgX}
            y1="30"
            x2={screenSvgX}
            y2="50"
            className="text-indigo-500"
            stroke="currentColor"
            strokeWidth="3"
          />
          <text
            x={screenSvgX}
            y="22"
            textAnchor="middle"
            className="text-[8px] text-indigo-500"
            fill="currentColor"
          >
            屏幕
          </text>
        </svg>
      </div>
    </div>
  );
}
