import { useState, useCallback } from "react";
import { listLenses, listDetectors, type CatalogLens, type CatalogDetector } from "../utils/api";
import { toast } from "../hooks/useToast";

export interface MatchFormState {
  [key: string]: string | number;
}

export interface ScoredResult<T = unknown> {
  lens: CatalogLens;
  detector: CatalogDetector;
  score: number;
  reasons: string[];
  derived: T;
}

interface UseLensMatchingOptions {
  lensCategory: string;
  detectorCategory: string;
  scoreFn: (
    lens: CatalogLens,
    detector: CatalogDetector,
    form: MatchFormState
  ) => { score: number; reasons: string[]; derived: unknown } | null;
}

export function useLensMatching(options: UseLensMatchingOptions) {
  const [form, setForm] = useState<MatchFormState>({});
  const [results, setResults] = useState<ScoredResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<ScoredResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const updateForm = useCallback((patch: Partial<MatchFormState>) => {
    setForm((prev) => ({ ...prev, ...patch }) as MatchFormState);
  }, []);

  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      if (e) e.preventDefault();
      setLoading(true);
      setHasSearched(true);
      setSelectedResult(null);

      try {
        const [lensData, detData] = await Promise.all([
          listLenses({ category: options.lensCategory, limit: 100 }),
          listDetectors({ category: options.detectorCategory, limit: 100 }),
        ]);

        const lenses: CatalogLens[] = lensData.items || [];
        const detectors: CatalogDetector[] = detData.items || [];

        if (lenses.length === 0 || detectors.length === 0) {
          toast("warning", "数据不足", "镜头或探测器数据尚未加载完成");
          setResults([]);
          setLoading(false);
          return;
        }

        const scored: ScoredResult[] = [];
        for (const lens of lenses) {
          for (const detector of detectors) {
            const scoredItem = options.scoreFn(lens, detector, form);
            if (scoredItem) {
              scored.push({
                lens,
                detector,
                score: scoredItem.score,
                reasons: scoredItem.reasons,
                derived: scoredItem.derived,
              });
            }
          }
        }

        scored.sort((a, b) => b.score - a.score);
        const top = scored.slice(0, 20);
        setResults(top);
        if (top.length > 0) {
          setSelectedResult(top[0]);
        }
      } catch (err) {
        console.error("Matching error:", err);
        toast("error", "匹配失败", "系统匹配过程中发生错误");
      } finally {
        setLoading(false);
      }
    },
    [form, options]
  );

  return {
    form,
    updateForm,
    results,
    selectedResult,
    setSelectedResult,
    loading,
    hasSearched,
    handleSubmit,
  };
}
