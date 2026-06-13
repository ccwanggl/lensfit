import { Lightbulb, CheckCircle2, AlertTriangle, Info } from "lucide-react";
import type { UnifiedMatchResult } from "../hooks/useMatching";

export type ExplanationDomain = "photography" | "microscope" | "infrared" | "industrial";

interface MatchExplanationProps {
  result: UnifiedMatchResult;
  domain: ExplanationDomain;
}

interface Bullet {
  type: "positive" | "neutral" | "warning";
  text: string;
}

function scoreLabel(value: number): string {
  const pct = Math.round((value || 0) * 100);
  if (pct >= 90) return "优秀";
  if (pct >= 75) return "良好";
  if (pct >= 60) return "中等";
  return "一般";
}

function getDimensionExplanation(name: string, value: number): string | null {
  const pct = Math.round(value * 100);
  switch (name) {
    case "coverage_margin":
      return pct >= 85 ? "像圈完全覆盖传感器，无暗角风险。" : pct >= 60 ? "像圈可覆盖传感器，但余量不大。" : "像圈较小，边角可能出现暗角。";
    case "nyquist_match":
      return pct >= 80 ? "传感器能充分记录镜头细节，匹配理想。" : pct >= 50 ? "传感器与镜头分辨率基本匹配。" : "传感器可能无法完全记录镜头细节。";
    case "direct_mount":
      return value >= 1.0 ? "镜头与探测器接口直接兼容。" : "接口不完全匹配，可能需要转接环。";
    case "cost_efficiency":
      return pct >= 80 ? "性价比高，预算利用合理。" : pct >= 50 ? "价格处于中等水平。" : "价格偏高，需确认是否在预算内。";
    case "fov_accuracy":
      return pct >= 80 ? "实际焦距与目标视场非常吻合。" : "焦距与目标视场有一定偏差。";
    case "focal_match":
      return pct >= 80 ? "镜头焦距与拍摄用途匹配。" : "焦距与拍摄用途匹配度一般。";
    case "aperture_value":
      return pct >= 80 ? "光圈满足进光量或虚化需求。" : "光圈表现一般。";
    case "brand_match":
      return value >= 1.0 ? "符合品牌偏好。" : "未完全匹配品牌偏好。";
    case "resolution_match":
      return pct >= 80 ? "物镜 NA 满足分辨率需求。" : "物镜 NA 与需求有差距。";
    case "magnification_accuracy":
      return pct >= 80 ? "放大倍率与目标需求吻合。" : "放大倍率与目标需求有偏差。";
    case "fov_match":
      return pct >= 80 ? "红外视场与需求匹配良好。" : "红外视场匹配度一般。";
    case "spatial_resolution":
      return pct >= 80 ? "空间分辨率满足目标检测要求。" : "空间分辨率可能不足。";
    case "band_match":
      return pct >= 80 ? "镜头波段与探测器波段匹配良好。" : "波段匹配度一般，需检查透过率。";
    case "ifov":
      return pct >= 80 ? "瞬时视场角较小，空间分辨率高。" : "瞬时视场角较大，远距离分辨率下降。";
    default:
      return null;
  }
}

function buildBullets(result: UnifiedMatchResult, domain: ExplanationDomain): Bullet[] {
  const bullets: Bullet[] = [];

  bullets.push({
    type: result.score >= 0.75 ? "positive" : result.score >= 0.5 ? "neutral" : "warning",
    text: `综合评分 ${(result.score * 100).toFixed(0)} 分（${scoreLabel(result.score)}），这是系统在当前约束下的推荐方案。`,
  });

  if (result.coverage_ratio !== undefined) {
    bullets.push({
      type: result.coverage_ratio >= 0.95 ? "positive" : result.coverage_ratio >= 0.8 ? "neutral" : "warning",
      text: `传感器覆盖率为 ${(result.coverage_ratio * 100).toFixed(0)}%，${result.coverage_ratio >= 0.95 ? "镜头像圈可完整覆盖传感器。" : result.coverage_ratio >= 0.8 ? "大部分区域可正常成像。" : "边角可能存在光线损失。"}`,
    });
  }

  if (result.vignetting) {
    bullets.push({ type: "warning", text: "检测到渐晕风险，实际成像四角可能偏暗。" });
  }

  const vectors = Object.entries(result.score_vector || {});
  if (vectors.length > 0) {
    const topDimensions = vectors
      .map(([name, value]) => ({ name, value: value as number }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 3);

    for (const dim of topDimensions) {
      const explanation = getDimensionExplanation(dim.name, dim.value);
      if (explanation) {
        bullets.push({ type: dim.value >= 0.7 ? "positive" : "neutral", text: explanation });
      }
    }
  }

  const derived = result.derived as Record<string, unknown> | undefined;
  if (derived) {
    if (domain === "photography" && derived.total_price_usd !== undefined) {
      bullets.push({ type: "neutral", text: `整套系统估算价格 $${(derived.total_price_usd as number).toFixed(0)}。` });
    }
    if (domain === "microscope" && derived.nyquist_ratio !== undefined) {
      const ratio = derived.nyquist_ratio as number;
      bullets.push({
        type: ratio >= 1 ? "positive" : ratio >= 0.5 ? "neutral" : "warning",
        text: `奈奎斯特采样比 ${ratio.toFixed(2)}，${ratio >= 1 ? "相机能充分记录光学细节。" : "相机采样可能不足，建议更小像元或更低放大倍率。"}`,
      });
    }
    if (domain === "infrared" && derived.ifov_mrad !== undefined) {
      bullets.push({ type: "neutral", text: `瞬时视场角 IFOV 为 ${(derived.ifov_mrad as number).toFixed(3)} mrad。` });
    }
    if (domain === "industrial" && derived.pixel_accuracy_mm !== undefined) {
      bullets.push({ type: "neutral", text: `像素精度约 ${(derived.pixel_accuracy_mm as number).toFixed(4)} mm/px。` });
    }
  }

  if (result.reason) {
    bullets.push({ type: "positive", text: result.reason });
  }

  return bullets;
}

const ICONS = {
  positive: <CheckCircle2 size={13} className="text-emerald-500 shrink-0 mt-0.5" />,
  neutral: <Info size={13} className="text-indigo-500 shrink-0 mt-0.5" />,
  warning: <AlertTriangle size={13} className="text-amber-500 shrink-0 mt-0.5" />,
};

const BG: Record<Bullet["type"], string> = {
  positive: "bg-emerald-50/60 dark:bg-emerald-900/15 border-emerald-100 dark:border-emerald-800/20",
  neutral: "bg-indigo-50/60 dark:bg-indigo-900/15 border-indigo-100 dark:border-indigo-800/20",
  warning: "bg-amber-50/60 dark:bg-amber-900/15 border-amber-100 dark:border-amber-800/20",
};

export default function MatchExplanation({ result, domain }: MatchExplanationProps) {
  const bullets = buildBullets(result, domain);

  return (
    <div className="rounded-[14px] border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb size={14} className="text-amber-500" />
        <h4 className="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider">
          为什么推荐这个方案？
        </h4>
      </div>
      <ul className="space-y-2">
        {bullets.map((b, i) => (
          <li
            key={i}
            className={`flex items-start gap-2 p-2.5 rounded-lg text-xs leading-relaxed border ${BG[b.type]}`}
          >
            {ICONS[b.type]}
            <span className="text-slate-700 dark:text-slate-200">{b.text}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
