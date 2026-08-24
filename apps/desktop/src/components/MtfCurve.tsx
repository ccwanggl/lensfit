import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceDot,
} from "recharts";
import { useTheme } from "../hooks/useTheme";
import type { MtfData } from "../utils/api";

interface Props {
  data: MtfData | null;
  height?: number;
}

export default function MtfCurve({ data, height = 220 }: Props) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  if (!data || !data.points || data.points.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-[14px] border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/60 dark:bg-slate-800/40"
        style={{ height }}
      >
        <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">无 MTF 数据</span>
      </div>
    );
  }

  const nyquist = data.detector_nyquist_lpmm;
  const nyquistPoint = nyquist
    ? data.points.find((p) => p.is_nyquist) || data.points.reduce((prev, curr) =>
        Math.abs(curr.frequency_lpmm - nyquist) < Math.abs(prev.frequency_lpmm - nyquist)
          ? curr
          : prev
      )
    : null;

  const gridColor = isDark ? "#334155" : "#e2e8f0";
  const textColor = isDark ? "#94a3b8" : "#64748b";

  return (
    <div className="rounded-[14px] border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider">
            估算 MTF 曲线
          </h4>
          <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
            基于镜头 MTF50 估算，供对比参考
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-400 dark:text-slate-500">MTF50</p>
          <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
            {data.lens_mtf50_lpmm.toFixed(1)} lp/mm
          </p>
        </div>
      </div>

      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.points} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid stroke={gridColor} strokeDasharray="3 3" />
            <XAxis
              dataKey="frequency_lpmm"
              type="number"
              tick={{ fontSize: 10, fill: textColor }}
              stroke={textColor}
              tickFormatter={(v: number) => `${v.toFixed(0)}`}
              label={{ value: "空间频率 (lp/mm)", position: "insideBottom", offset: -2, fill: textColor, fontSize: 10 }}
            />
            <YAxis
              domain={[0, 1]}
              tick={{ fontSize: 10, fill: textColor }}
              stroke={textColor}
              tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? "#1e293b" : "#ffffff",
                border: `1px solid ${isDark ? "#334155" : "#e2e8f0"}`,
                borderRadius: 8,
              }}
              labelStyle={{ color: isDark ? "#e2e8f0" : "#1f2937", fontSize: 11 }}
              itemStyle={{ color: isDark ? "#e2e8f0" : "#1f2937", fontSize: 11 }}
              formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, "MTF"]}
              labelFormatter={(label: number) => `${label.toFixed(1)} lp/mm`}
            />
            <ReferenceLine y={0.5} stroke={isDark ? "#475569" : "#94a3b8"} strokeDasharray="4 4" />
            {nyquist && (
              <ReferenceLine
                x={nyquist}
                stroke="#f43f5e"
                strokeDasharray="5 5"
                label={{
                  value: `Nyquist ${nyquist.toFixed(1)}`,
                  position: "top",
                  fill: "#f43f5e",
                  fontSize: 10,
                }}
              />
            )}
            {nyquistPoint && (
              <ReferenceDot
                x={nyquistPoint.frequency_lpmm}
                y={nyquistPoint.mtf}
                r={4}
                fill="#f43f5e"
                stroke="none"
              />
            )}
            <Line
              type="monotone"
              dataKey="mtf"
              stroke="#6366f1"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: "#6366f1", stroke: "#fff", strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 rounded-full bg-indigo-500" />
          <span>MTF</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 rounded-full bg-rose-500" />
          <span>传感器奈奎斯特频率</span>
        </div>
      </div>
    </div>
  );
}
