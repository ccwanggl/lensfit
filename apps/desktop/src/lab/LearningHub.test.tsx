import "@testing-library/jest-dom/vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LearningHub from "./LearningHub";
import { useLabStore } from "../stores/labStore";
import type { LabExperiment, LabRunResult } from "../utils/api";

vi.mock("../utils/api", () => ({
  listLabExperiments: vi.fn(),
  getLabExperiment: vi.fn(),
  runLabExperiment: vi.fn(),
  runWorkbench: vi.fn(),
  putLearningProgress: vi.fn().mockResolvedValue({}),
}));

import {
  getLabExperiment,
  listLabExperiments,
  runLabExperiment,
} from "../utils/api";

const experiment: LabExperiment = {
  id: "exp-flicker",
  title: "闪烁回归实验",
  description: "用于验证调参时图像不清空",
  difficulty: "foundation",
  linked_concepts: [],
  linked_formulas: [],
  prerequisites: [],
  learning_objectives: [],
  parameters: [
    {
      name: "wavelength",
      label: "波长",
      type: "number",
      default: 500,
      min: 400,
      max: 700,
      step: 1,
      unit: "nm",
    },
  ],
};

function result(svgText: string): LabRunResult {
  return {
    data: {},
    svg: `<svg viewBox="0 0 10 10"><text>${svgText}</text></svg>`,
    warnings: [],
    learning_hints: [],
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

function renderHub() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <LearningHub />
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  useLabStore.setState({
    learningView: "sandbox",
    activeExperimentId: "exp-flicker",
    paramDrafts: {},
    sceneDrafts: {},
  });
  vi.mocked(listLabExperiments).mockResolvedValue({ items: [experiment] });
  vi.mocked(getLabExperiment).mockResolvedValue({ items: [experiment] });
});

describe("LearningHub 调参重绘", () => {
  it("调参后新结果返回前保留上一次 SVG，不清空闪烁", async () => {
    const second = deferred<LabRunResult>();
    vi.mocked(runLabExperiment)
      .mockResolvedValueOnce(result("FIRST"))
      .mockReturnValueOnce(second.promise);

    renderHub();

    // 首次结果渲染
    expect(await screen.findByText("FIRST")).toBeInTheDocument();

    // 调参：拖动波长滑块 → 60ms 防抖后触发第二次运行（挂起）
    fireEvent.change(screen.getByRole("slider"), { target: { value: "600" } });
    await waitFor(() =>
      expect(runLabExperiment).toHaveBeenCalledTimes(2)
    );

    // 回归断言：第二次运行挂起期间，上一次的 SVG 必须仍然可见
    expect(screen.getByText("FIRST")).toBeInTheDocument();

    // 第二次结果到达后替换
    second.resolve(result("SECOND"));
    expect(await screen.findByText("SECOND")).toBeInTheDocument();
  });
});
