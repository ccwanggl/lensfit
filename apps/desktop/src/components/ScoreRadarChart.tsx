import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
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

export default function ScoreRadarChart({ scoreVector, size = 240 }: Props) {
  const data = Object.entries(scoreVector).map(([key, value]) => ({
    dimension: LABEL_MAP[key] || key,
    value: Math.round((value || 0) * 100),
    fullMark: 100,
  }));

  if (data.length === 0) return null;

  return (
    <div className="w-full" style={{ height: size }}>
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
