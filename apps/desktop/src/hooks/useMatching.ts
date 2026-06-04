import { useState, useEffect, useCallback, useRef } from "react";
import {
  startMatch,
  getMatchStatus,
  getMatchResult,
  cancelMatch,
  startMatchStream,
} from "../utils/api";
import { toast } from "./useToast";

export interface PhysicsTraceItem {
  formula: string;
  inputs: Record<string, string | number>;
  output: number;
  unit: string;
  assumption: string;
}

/** Unified match result shape from the backend. */
export interface UnifiedMatchResult {
  lens_id: number;
  detector_id: number;
  lens_model: string;
  detector_model: string;
  score: number;
  score_vector: Record<string, number>;
  coverage_ratio: number;
  vignetting: boolean;
  derived: Record<string, unknown>;
  derivation_chain: PhysicsTraceItem[];
}

interface MatchingState {
  taskId: string | null;
  status: "idle" | "pending" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  stage: string;
  error: string | null;
  results: UnifiedMatchResult[];
}

interface UseMatchingOptions {
  domain: string;
  requirements: object;
  mode?: "poll" | "stream";
  onSuccess?: (results: UnifiedMatchResult[]) => void;
  onError?: (error: string) => void;
}

export function useMatching({ domain, requirements, mode = "poll", onSuccess, onError }: UseMatchingOptions) {
  const [state, setState] = useState<MatchingState>({
    taskId: null,
    status: "idle",
    progress: 0,
    stage: "",
    error: null,
    results: [],
  });

  const mountedRef = useRef(true);
  const streamCloseRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (streamCloseRef.current) {
        streamCloseRef.current();
        streamCloseRef.current = null;
      }
    };
  }, []);

  const start = useCallback(async () => {
    // Clean up any previous stream
    if (streamCloseRef.current) {
      streamCloseRef.current();
      streamCloseRef.current = null;
    }

    setState({
      taskId: null,
      status: "pending",
      progress: 0,
      stage: "",
      error: null,
      results: [],
    });

    if (mode === "stream") {
      // SSE progressive mode
      setState((prev) => ({ ...prev, status: "running" }));

      try {
        const { close } = await startMatchStream(
          { domain, requirements },
          (data) => {
            if (!mountedRef.current) {
              close();
              return;
            }

            const stage = String(data.stage ?? "");
            const progress = Number(data.progress ?? 0);

            setState((prev) => ({
              ...prev,
              progress,
              stage,
              status: stage === "completed" ? "completed" : stage === "error" ? "failed" : "running",
              results: stage === "completed" ? (data.results as UnifiedMatchResult[]) ?? [] : prev.results,
              error: stage === "error" ? String(data.error ?? "匹配失败") : null,
            }));

            if (stage === "completed") {
              const matches = (data.results as UnifiedMatchResult[]) ?? [];
              toast("success", "匹配完成", `共找到 ${matches.length} 组最优方案`);
              onSuccess?.(matches);
            } else if (stage === "error") {
              const errMsg = String(data.error ?? "匹配失败");
              toast("error", "匹配失败", errMsg);
              onError?.(errMsg);
            }
          },
          (err) => {
            if (!mountedRef.current) return;
            const message = err instanceof Error ? err.message : "流式连接失败";
            setState((prev) => ({
              ...prev,
              status: "failed",
              error: message,
            }));
            toast("error", "网络错误", message);
            onError?.(message);
          }
        );

        streamCloseRef.current = close;
      } catch (e) {
        if (!mountedRef.current) return;
        const message = e instanceof Error ? e.message : "启动流式匹配失败";
        setState((prev) => ({
          ...prev,
          status: "failed",
          error: message,
        }));
        toast("error", "匹配失败", message);
        onError?.(message);
      }

      return;
    }

    // Polling mode
    try {
      const response = await startMatch({ domain, requirements });
      if (!mountedRef.current) return;

      setState((prev) => ({
        ...prev,
        taskId: response.task_id,
        status: "running",
      }));
    } catch (e) {
      if (!mountedRef.current) return;
      const message = e instanceof Error ? e.message : "启动匹配失败";
      setState((prev) => ({
        ...prev,
        status: "failed",
        error: message,
      }));
      toast("error", "匹配失败", message);
      onError?.(message);
    }
  }, [domain, requirements, mode, onError, onSuccess]);

  const cancel = useCallback(async () => {
    if (streamCloseRef.current) {
      streamCloseRef.current();
      streamCloseRef.current = null;
      setState((prev) => ({
        ...prev,
        status: "cancelled",
      }));
      return;
    }

    const { taskId } = state;
    if (!taskId) return;
    try {
      await cancelMatch(taskId);
      setState((prev) => ({
        ...prev,
        status: "cancelled",
        taskId: null,
      }));
    } catch {
      // ignore
    }
  }, [state.taskId]);

  // Poll task status (only for poll mode)
  useEffect(() => {
    if (mode !== "poll") return;
    const { taskId, status } = state;
    if (!taskId || status !== "running") return;

    let interval: ReturnType<typeof setInterval>;
    let active = true;

    const poll = async () => {
      if (!active || !mountedRef.current) return;

      try {
        const statusRes = await getMatchStatus(taskId);
        if (!active || !mountedRef.current) return;

        setState((prev) => ({
          ...prev,
          progress: statusRes.progress ?? prev.progress,
          stage: statusRes.stage ?? prev.stage,
        }));

        if (statusRes.status === "completed") {
          active = false;
          clearInterval(interval);

          const resultData = await getMatchResult(taskId);
          if (!mountedRef.current) return;

          const matches = (resultData.top_matches ?? []) as UnifiedMatchResult[];
          setState((prev) => ({
            ...prev,
            status: "completed",
            taskId: null,
            results: matches,
            error: null,
          }));
          toast("success", "匹配完成", `共找到 ${matches.length} 组最优方案`);
          onSuccess?.(matches);
        } else if (statusRes.status === "failed") {
          active = false;
          clearInterval(interval);

          const errMsg = statusRes.error || "匹配失败";
          if (!mountedRef.current) return;

          setState((prev) => ({
            ...prev,
            status: "failed",
            taskId: null,
            error: errMsg,
          }));
          toast("error", "匹配失败", errMsg);
          onError?.(errMsg);
        }
      } catch (e) {
        if (!active) return;
        active = false;
        clearInterval(interval);

        if (!mountedRef.current) return;
        const message = e instanceof Error ? e.message : "轮询任务状态时出错";
        setState((prev) => ({
          ...prev,
          status: "failed",
          taskId: null,
          error: message,
        }));
        toast("error", "网络错误", "无法获取匹配结果，请重试");
        onError?.(message);
      }
    };

    interval = setInterval(poll, 300);
    poll();

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [state.taskId, state.status, mode, onSuccess, onError]);

  return {
    ...state,
    isLoading: state.status === "pending" || state.status === "running",
    start,
    cancel,
  };
}
