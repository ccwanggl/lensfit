import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useReportProgress } from "./reportProgress";

vi.mock("../utils/api", () => ({
  putLearningProgress: vi.fn(),
}));

import { putLearningProgress } from "../utils/api";

function makeWrapper(client: QueryClient) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(putLearningProgress).mockResolvedValue({
    learner_id: "default",
    item_kind: "experiment",
    item_id: "thin-lens",
    status: "completed",
    score: null,
    updated_at: null,
  });
});

describe("useReportProgress", () => {
  it("同一 (kind, id, status) 只上报一次", async () => {
    const client = new QueryClient();
    const { result } = renderHook(() => useReportProgress(), {
      wrapper: makeWrapper(client),
    });

    act(() => {
      result.current("experiment", "thin-lens", "completed");
      result.current("experiment", "thin-lens", "completed");
    });

    await waitFor(() =>
      expect(putLearningProgress).toHaveBeenCalledTimes(1)
    );
    expect(putLearningProgress).toHaveBeenCalledWith({
      item_kind: "experiment",
      item_id: "thin-lens",
      status: "completed",
    });
  });

  it("不同 kind/id/status 分别上报", async () => {
    const client = new QueryClient();
    const { result } = renderHook(() => useReportProgress(), {
      wrapper: makeWrapper(client),
    });

    act(() => {
      result.current("experiment", "thin-lens", "completed");
      result.current("concept", "cmos-fundamentals", "viewed");
    });

    await waitFor(() =>
      expect(putLearningProgress).toHaveBeenCalledTimes(2)
    );
  });

  it("上报成功后使 curriculum-graph 查询失效", async () => {
    const client = new QueryClient();
    const invalidate = vi.spyOn(client, "invalidateQueries");
    const { result } = renderHook(() => useReportProgress(), {
      wrapper: makeWrapper(client),
    });

    act(() => {
      result.current("preset", "single-slit-diffraction", "completed");
    });

    await waitFor(() =>
      expect(invalidate).toHaveBeenCalledWith({
        queryKey: ["curriculum-graph"],
      })
    );
  });

  it("上报失败后清除去重标记，下次触发重试", async () => {
    vi.mocked(putLearningProgress)
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValue({
        learner_id: "default",
        item_kind: "experiment",
        item_id: "thin-lens",
        status: "completed",
        score: null,
        updated_at: null,
      });
    const client = new QueryClient();
    const { result } = renderHook(() => useReportProgress(), {
      wrapper: makeWrapper(client),
    });

    act(() => {
      result.current("experiment", "thin-lens", "completed");
    });
    await waitFor(() =>
      expect(putLearningProgress).toHaveBeenCalledTimes(1)
    );

    act(() => {
      result.current("experiment", "thin-lens", "completed");
    });
    await waitFor(() =>
      expect(putLearningProgress).toHaveBeenCalledTimes(2)
    );
  });
});
