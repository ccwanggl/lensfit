import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface ScoreVector {
  fov_accuracy?: number;
  coverage_margin?: number;
  nyquist_match?: number;
  direct_mount?: number;
  cost_efficiency?: number;
}

interface Props {
  scoreVector: ScoreVector;
  size?: number;
}

const LABEL_MAP: Record<string, string> = {
  fov_accuracy: "视场精度",
  coverage_margin: "覆盖余量",
  nyquist_match: "分辨率匹配",
  direct_mount: "直接适配",
  cost_efficiency: "性价比",
};

interface TooltipPayloadItem {
  payload: { dimension: string; value: number };
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload?.length) return null;
  const item = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-800">
      <span className="font-semibold text-slate-700 dark:text-slate-200">{item.dimension}</span>
      <span className="ml-2 tabular-nums font-bold text-indigo-600 dark:text-indigo-400">{item.value}</span>
    </div>
  );
}

export default function ScoreRadarChart({ scoreVector, size = 240 }: Props) {
  const data = Object.entries(scoreVector).map(([key, value]) => ({
    dimension: LABEL_MAP[key] || key,
    value: Math.round((value || 0) * 100),
    fullMark: 100,
  }));

  if (data.length === 0) {
    return (
      <div
        className="flex w-full items-center justify-center rounded-xl border border-dashed border-slate-200 text-xs text-slate-400 dark:border-slate-700 dark:text-slate-500"
        style={{ height: size }}
      >
        暂无评分数据
      </div>
    );
  }

  const summary = data.map((d) => `${d.dimension} ${d.value} 分`).join("，");

  return (
    <div className="w-full" style={{ height: size }} role="img" aria-label={`评分雷达图：${summary}`}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="currentColor" className="text-slate-200 dark:text-slate-700" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fontSize: 12, fill: "currentColor", fontWeight: 600 }}
            className="text-slate-600 dark:text-slate-300"
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 10, fill: "currentColor" }}
            tickCount={5}
            axisLine={false}
            className="text-slate-500 dark:text-slate-400"
          />
          <Tooltip content={<ChartTooltip />} />
          <Radar
            name="评分"
            dataKey="value"
            stroke="#6366f1"
            strokeWidth={2}
            fill="#6366f1"
            fillOpacity={0.15}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
