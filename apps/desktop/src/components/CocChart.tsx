import {
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Line,
  ComposedChart,
} from "recharts";
import { useTheme } from "../hooks/useTheme";
import type { CocData } from "../utils/api";

interface Props {
  data: CocData | null;
  height?: number;
}

interface ChartRow {
  aperture: string;
  near: number;
  far: number;
  dof: number;
  hyperfocal: number;
  isInfinity: boolean;
}

function formatDistance(m: number | null): string {
  if (m === null || !isFinite(m)) return "∞";
  if (m >= 1000) return `${(m / 1000).toFixed(1)}km`;
  if (m >= 1) return `${m.toFixed(2)}m`;
  return `${(m * 1000).toFixed(1)}mm`;
}

export default function CocChart({ data, height = 240 }: Props) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  if (!data || !data.apertures || data.apertures.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-[14px] border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/40"
        style={{ height }}
      >
        <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">无景深数据</span>
      </div>
    );
  }

  const rows: ChartRow[] = data.apertures.map((a) => {
    const isInfinity = a.far_limit_m === null;
    // Cap the displayed far limit to hyperfocal when infinity.
    const far: number = isInfinity
      ? a.hyperfocal_m
      : (a.far_limit_m ?? a.hyperfocal_m);
    const dof = isInfinity ? a.hyperfocal_m - a.near_limit_m : (a.dof_total_m ?? 0);
    return {
      aperture: `f/${a.aperture.toFixed(1)}`,
      near: a.near_limit_m,
      far,
      dof,
      hyperfocal: a.hyperfocal_m,
      isInfinity,
    };
  });

  const gridColor = isDark ? "#334155" : "#e2e8f0";
  const textColor = isDark ? "#94a3b8" : "#64748b";

  // Compute a sensible Y-axis upper bound.
  const maxFar = Math.max(...rows.map((r) => r.far));
  const yMax = Math.max(maxFar * 1.15, data.focus_distance_m * 1.5);

  return (
    <div className="rounded-[14px] border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider">
            估算景深
          </h4>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
            对焦距离 {data.focus_distance_m.toFixed(1)}m · CoC {data.coc_mm.toFixed(3)}mm
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-400 dark:text-slate-500">焦距</p>
          <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
            {data.focal_length_mm.toFixed(0)}mm
          </p>
        </div>
      </div>

      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={rows} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
            <XAxis
              dataKey="aperture"
              tick={{ fontSize: 10, fill: textColor }}
              stroke={textColor}
            />
            <YAxis
              domain={[0, yMax]}
              tick={{ fontSize: 10, fill: textColor }}
              stroke={textColor}
              tickFormatter={(v: number) => formatDistance(v)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? "#1e293b" : "#ffffff",
                border: `1px solid ${isDark ? "#334155" : "#e2e8f0"}`,
                borderRadius: 8,
              }}
              labelStyle={{ color: isDark ? "#e2e8f0" : "#1f2937", fontSize: 11 }}
              itemStyle={{ color: isDark ? "#e2e8f0" : "#1f2937", fontSize: 11 }}
              formatter={(value: number, name: string, props: { payload?: ChartRow }) => {
                const row = props.payload;
                if (name === "近端") return [formatDistance(row?.near ?? value), name];
                if (name === "远端") {
                  return [row?.isInfinity ? "∞" : formatDistance(row?.far ?? value), name];
                }
                return [formatDistance(value), name];
              }}
            />
            <ReferenceLine
              y={data.focus_distance_m}
              stroke="#6366f1"
              strokeDasharray="5 5"
              label={{
                value: `对焦 ${data.focus_distance_m.toFixed(1)}m`,
                position: "top",
                fill: "#6366f1",
                fontSize: 10,
              }}
            />
            <Bar dataKey="near" name="近端" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            <Bar dataKey="far" name="远端" fill="#10b981" radius={[4, 4, 0, 0]} />
            <Line
              type="monotone"
              dataKey="hyperfocal"
              name="超焦距"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 rounded-full bg-slate-400" />
          <span>近端</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 rounded-full bg-emerald-500" />
          <span>远端</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 rounded-full bg-amber-500" />
          <span>超焦距</span>
        </div>
      </div>
    </div>
  );
}
