import { useCallback, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  putLearningProgress,
  type LearningProgressStatus,
} from "../utils/api";

/**
 * Report a learning-progress record, at most once per (kind, id, status)
 * per component lifetime (for scored records the score is part of the
 * dedupe key, so retaking a quiz with a different score re-reports).
 * Failures clear the dedupe mark so the next trigger retries. On success
 * the curriculum graph is invalidated so the path view picks up the
 * merged status.
 */
export function useReportProgress() {
  const reported = useRef(new Set<string>());
  const queryClient = useQueryClient();

  return useCallback(
    (
      itemKind: string,
      itemId: string,
      status: LearningProgressStatus,
      score?: number
    ) => {
      const key = `${itemKind}:${itemId}:${status}:${score ?? ""}`;
      if (reported.current.has(key)) return;
      reported.current.add(key);
      putLearningProgress({ item_kind: itemKind, item_id: itemId, status, score })
        .then(() =>
          queryClient.invalidateQueries({ queryKey: ["curriculum-graph"] })
        )
        .catch(() => reported.current.delete(key));
    },
    [queryClient]
  );
}
