import "@testing-library/jest-dom/vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TutorialView from "./TutorialView";
import { useLabStore } from "../stores/labStore";
import type { ContentConcept, ContentConceptDetail } from "../utils/api";

vi.mock("../utils/api", () => ({
  listContentConcepts: vi.fn(),
  getContentConcept: vi.fn(),
  listContentQuizzes: vi.fn().mockResolvedValue({ items: [], errors: [] }),
  getContentQuiz: vi.fn(),
  putLearningProgress: vi.fn().mockResolvedValue({}),
}));

import { getContentConcept, listContentConcepts, listContentQuizzes, getContentQuiz } from "../utils/api";

const concepts: ContentConcept[] = [
  {
    id: "cmos-fundamentals",
    title: "CMOS Image Sensor 基础",
    module: "20-geometric-optics",
    difficulty: "intermediate",
    prerequisites: [],
    linked_experiments: ["sensor-coverage"],
    status: "draft",
  },
  {
    id: "cmos-spectral-response",
    title: "CMOS Sensor 光谱响应与色彩特性",
    module: "40-spectroscopy",
    difficulty: "intermediate",
    prerequisites: ["cmos-fundamentals"],
    linked_experiments: [],
    status: "draft",
  },
];

const detail: ContentConceptDetail = {
  ...concepts[0],
  body: "## 前言\n\nCMOS sensor 的本质是自带像素的相机芯片。",
};

function renderView() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <TutorialView />
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  useLabStore.setState({
    learningView: "tutorials",
    activeConceptId: null,
    activeExperimentId: null,
    recentExperiments: [],
  });
  vi.mocked(listContentConcepts).mockResolvedValue({ items: concepts, errors: [] });
  vi.mocked(getContentConcept).mockResolvedValue(detail);
});

describe("TutorialView", () => {
  it("按 module 分组列出概念", async () => {
    renderView();

    expect(await screen.findByText("几何光学")).toBeInTheDocument();
    expect(screen.getByText("光谱学")).toBeInTheDocument();
    expect(screen.getByText("CMOS Image Sensor 基础")).toBeInTheDocument();
    expect(screen.getByText("CMOS Sensor 光谱响应与色彩特性")).toBeInTheDocument();
  });

  it("点击概念后渲染 markdown 正文与关联实验入口", async () => {
    const user = userEvent.setup();
    renderView();

    await user.click(await screen.findByText("CMOS Image Sensor 基础"));

    expect(useLabStore.getState().activeConceptId).toBe("cmos-fundamentals");
    expect(await screen.findByText("前言")).toBeInTheDocument();
    expect(
      screen.getByText(/CMOS sensor 的本质是自带像素的相机芯片/)
    ).toBeInTheDocument();

    const expButton = screen.getByRole("button", { name: /sensor-coverage/ });
    await user.click(expButton);

    const state = useLabStore.getState();
    expect(state.learningView).toBe("sandbox");
    expect(state.activeExperimentId).toBe("sensor-coverage");
  });

  it("概念有配套测验时在文末渲染测验面板", async () => {
    const quiz = {
      id: "cmos-fundamentals-quiz",
      title: "CMOS 基础自测",
      module: "20-geometric-optics",
      concepts: ["cmos-fundamentals"],
      pass_score: 80,
      questions: [
        {
          question: "拜耳阵列中绿色滤色单元占比？",
          options: ["1/4", "1/2"],
          correct_index: 1,
          explanation: "RGGB 排列，G 占一半。",
        },
      ],
    };
    vi.mocked(listContentQuizzes).mockResolvedValue({ items: [quiz], errors: [] });
    vi.mocked(getContentQuiz).mockResolvedValue(quiz);
    const user = userEvent.setup();
    renderView();

    await user.click(await screen.findByText("CMOS Image Sensor 基础"));

    expect(await screen.findByText("配套测验")).toBeInTheDocument();
    expect(await screen.findByText("CMOS 基础自测")).toBeInTheDocument();
    expect(screen.getByText("拜耳阵列中绿色滤色单元占比？")).toBeInTheDocument();
    expect(listContentQuizzes).toHaveBeenCalledWith("cmos-fundamentals");
  });

  it("索引错误以警告形式展示", async () => {
    vi.mocked(listContentConcepts).mockResolvedValue({
      items: concepts,
      errors: [{ path: "10-foundations/learning/bad.md", error: "缺少必需字段：module" }],
    });
    renderView();

    expect(
      await screen.findByText(/1 篇文档未通过内容合同校验/)
    ).toBeInTheDocument();
    expect(screen.getByText("10-foundations/learning/bad.md")).toBeInTheDocument();
  });

  it("未选择概念时显示空态提示", async () => {
    renderView();
    await waitFor(() =>
      expect(screen.getByText("选择一篇教程开始阅读")).toBeInTheDocument()
    );
  });
});
