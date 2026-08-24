import { ArrowLeftRight, CheckCircle2 } from "lucide-react";
import { type UnifiedMatchResult } from "../hooks/useMatching";

interface Props {
  results: UnifiedMatchResult[];
}

function formatVal(v: unknown): string {
  if (typeof v === "number") {
    if (Math.abs(v) >= 1000) return v.toFixed(0);
    if (Math.abs(v) >= 1) return v.toFixed(2);
    return v.toFixed(4);
  }
  if (typeof v === "boolean") return v ? "是" : "否";
  return String(v ?? "—");
}

function dimLabel(key: string): string {
  const map: Record<string, string> = {
    fov_accuracy: "视场精度",
    coverage_margin: "覆盖裕量",
    nyquist_match: "奈奎斯特匹配",
    direct_mount: "接口兼容性",
    cost_efficiency: "性价比",
    focal_match: "焦距匹配度",
    aperture_value: "光圈值",
    resolution_match: "分辨率匹配",
    magnification_accuracy: "放大倍率精度",
    fov_match: "视场匹配",
    spatial_resolution: "空间分辨率",
    band_match: "波段匹配",
    ifov: "瞬时视场",
  };
  return map[key] || key;
}

export function generateCompareReason(a: UnifiedMatchResult, b: UnifiedMatchResult): string {
  const diffs: Array<{ label: string; aVal: number; bVal: number; better: "a" | "b" | "eq" }> = [];

  // Compare score_vector
  const allKeys = new Set([...Object.keys(a.score_vector), ...Object.keys(b.score_vector)]);
  for (const k of allKeys) {
    const av = a.score_vector[k] ?? 0;
    const bv = b.score_vector[k] ?? 0;
    const diff = Math.abs(av - bv);
    if (diff > 0.05) {
      diffs.push({ label: dimLabel(k), aVal: av, bVal: bv, better: av > bv ? "a" : "b" });
    }
  }

  // Sort by diff magnitude
  diffs.sort((x, y) => Math.abs(y.aVal - y.bVal) - Math.abs(x.aVal - x.bVal));

  const topDiffs = diffs.slice(0, 3);
  if (topDiffs.length === 0) {
    return "两个方案在各项维度上表现接近，建议根据价格或品牌偏好选择。";
  }

  const aWins = topDiffs.filter((d) => d.better === "a");
  const bWins = topDiffs.filter((d) => d.better === "b");

  const aName = a.lens_model || `方案A`;
  const bName = b.lens_model || `方案B`;

  const parts: string[] = [];

  if (aWins.length > 0) {
    const items = aWins.map((d) => `${d.label}（${formatVal(d.aVal)} vs ${formatVal(d.bVal)}）`).join("、");
    parts.push(`${aName} 在 ${items} 上更优`);
  }
  if (bWins.length > 0) {
    const items = bWins.map((d) => `${d.label}（${formatVal(d.bVal)} vs ${formatVal(d.aVal)}）`).join("、");
    parts.push(`${bName} 在 ${items} 上更优`);
  }

  const scoreDiff = a.score - b.score;
  if (Math.abs(scoreDiff) > 0.1) {
    const leader = scoreDiff > 0 ? aName : bName;
    parts.push(`综合评分 ${leader} 领先 ${Math.abs(scoreDiff).toFixed(2)} 分`);
  }

  return parts.join("；") + "。";
}

export default function CompareView({ results }: Props) {
  if (!results || results.length < 2) return null;

  const rows: Array<{ label: string; key: string; type: "score" | "vector" | "derived" | "coverage" | "vignetting" }> = [
    { label: "综合评分", key: "score", type: "score" },
    { label: "覆盖比", key: "coverage_ratio", type: "coverage" },
    { label: "渐晕", key: "vignetting", type: "vignetting" },
  ];

  // Add score_vector dimensions
  const vectorKeys = new Set<string>();
  results.forEach((r) => Object.keys(r.score_vector).forEach((k) => vectorKeys.add(k)));
  vectorKeys.forEach((k) => rows.push({ label: dimLabel(k), key: k, type: "vector" }));

  // Add derived numeric values
  const derivedKeys = new Set<string>();
  results.forEach((r) => {
    if (r.derived && typeof r.derived === "object") {
      Object.entries(r.derived).forEach(([k, v]) => {
        if (typeof v === "number" && k !== "coverage" && k !== "nyquist") {
          derivedKeys.add(k);
        }
      });
    }
  });
  derivedKeys.forEach((k) => rows.push({ label: k.replace(/_/g, " "), key: k, type: "derived" }));

  function getCellValue(r: UnifiedMatchResult, row: (typeof rows)[0]): unknown {
    if (row.type === "score") return r.score;
    if (row.type === "coverage") return r.coverage_ratio;
    if (row.type === "vignetting") return r.vignetting;
    if (row.type === "vector") return r.score_vector[row.key] ?? 0;
    if (row.type === "derived") return (r.derived as Record<string, unknown> | undefined)?.[row.key] ?? 0;
    return 0;
  }

  function getBestWorst(row: (typeof rows)[0]): { bestIdx: number; worstIdx: number } {
    const vals = results.map((r, i) => ({ i, v: getCellValue(r, row) }));
    const numeric = vals.filter((x) => typeof x.v === "number") as Array<{ i: number; v: number }>;
    if (numeric.length === 0) return { bestIdx: -1, worstIdx: -1 };
    const sorted = [...numeric].sort((a, b) => b.v - a.v);
    return { bestIdx: sorted[0].i, worstIdx: sorted[sorted.length - 1].i };
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-3">
        <ArrowLeftRight size={16} className="text-indigo-500" />
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">方案对比</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700">
              <th className="text-left py-2.5 pr-3 text-slate-500 dark:text-slate-400 font-semibold">维度</th>
              {results.map((r, i) => (
                <th key={i} className="text-center py-2.5 px-2 text-slate-700 dark:text-slate-200 font-bold min-w-[100px]">
                  <div className="truncate max-w-[110px]">{r.lens_model || `方案${i + 1}`}</div>
                  <span className="text-xs font-normal text-slate-400 dark:text-slate-500">Rank {i + 1}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => {
              const { bestIdx, worstIdx } = getBestWorst(row);
              return (
                <tr key={ri} className="border-b border-slate-100 dark:border-slate-800/50">
                  <td className="py-2.5 pr-3 text-slate-600 dark:text-slate-300 font-semibold">{row.label}</td>
                  {results.map((r, ci) => {
                    const val = getCellValue(r, row);
                    const isBest = ci === bestIdx;
                    const isWorst = ci === worstIdx && results.length > 1 && bestIdx !== worstIdx;
                    return (
                      <td key={ci} className="py-2.5 px-2 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded ${
                            isBest
                              ? "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 font-bold"
                              : isWorst
                              ? "text-slate-400 dark:text-slate-500"
                              : "text-slate-700 dark:text-slate-200"
                          }`}
                        >
                          {isBest && <CheckCircle2 size={12} />}
                          {row.type === "vignetting" ? (val ? "有" : "无") : formatVal(val)}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {results.length >= 2 && (
        <div className="p-3 rounded-[10px] bg-indigo-50/60 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
          <p className="text-xs font-bold text-indigo-700 dark:text-indigo-300 mb-1.5">为什么选 {results[0].lens_model || "方案1"}？</p>
          <p className="text-xs text-indigo-600 dark:text-indigo-400 leading-relaxed">
            {generateCompareReason(results[0], results[1])}
          </p>
        </div>
      )}
    </div>
  );
}
