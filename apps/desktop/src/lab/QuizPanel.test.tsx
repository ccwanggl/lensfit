import "@testing-library/jest-dom/vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import QuizPanel from "./QuizPanel";
import type { ContentQuiz } from "../utils/api";

vi.mock("../utils/api", () => ({
  getContentQuiz: vi.fn(),
  putLearningProgress: vi.fn().mockResolvedValue({}),
}));

import { getContentQuiz, putLearningProgress } from "../utils/api";

const quiz: ContentQuiz = {
  id: "geo-optics-imaging-quiz",
  title: "几何光学成像与像差自测",
  module: "20-geometric-optics",
  concepts: [],
  pass_score: 80,
  questions: [
    {
      question: "薄透镜焦距 f = 50 mm，u = 150 mm，像距 v？",
      options: ["37.5 mm", "75 mm"],
      correct_index: 1,
      explanation: "1/v = 1/50 − 1/150。",
    },
    {
      question: "F 数 = f/D，f=50、D=25 时 F 数是？",
      options: ["F/2", "F/25"],
      correct_index: 0,
      explanation: "F = 50/25 = 2。",
    },
  ],
};

function renderPanel() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <QuizPanel quizId={quiz.id} />
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(getContentQuiz).mockResolvedValue(quiz);
});

describe("QuizPanel", () => {
  it("加载并渲染通用测验组件（标题、题干、选项）", async () => {
    renderPanel();

    expect(await screen.findByText(quiz.title)).toBeInTheDocument();
    expect(screen.getByText(quiz.questions[0].question)).toBeInTheDocument();
    for (const opt of quiz.questions[0].options) {
      expect(screen.getByText(opt)).toBeInTheDocument();
    }
    expect(getContentQuiz).toHaveBeenCalledWith(quiz.id);
  });

  it("全部答对提交后上报 scored=100（item_kind=assessment）", async () => {
    const user = userEvent.setup();
    renderPanel();

    // 第 1 题：选正确答案（correct_index=1）
    await user.click(await screen.findByText("75 mm"));
    await user.click(screen.getByRole("button", { name: "下一题" }));
    // 第 2 题：选正确答案（correct_index=0）
    await user.click(await screen.findByText("F/2"));
    await user.click(screen.getByRole("button", { name: "查看结果" }));

    expect(await screen.findByText("2 / 2")).toBeInTheDocument();
    expect(putLearningProgress).toHaveBeenCalledTimes(1);
    expect(putLearningProgress).toHaveBeenCalledWith({
      item_kind: "assessment",
      item_id: quiz.id,
      status: "scored",
      score: 100,
    });
  });

  it("答对一半上报 score=50", async () => {
    const user = userEvent.setup();
    renderPanel();

    // 第 1 题答错，第 2 题答对
    await user.click(await screen.findByText("37.5 mm"));
    await user.click(screen.getByRole("button", { name: "下一题" }));
    await user.click(await screen.findByText("F/2"));
    await user.click(screen.getByRole("button", { name: "查看结果" }));

    expect(await screen.findByText("1 / 2")).toBeInTheDocument();
    expect(putLearningProgress).toHaveBeenCalledWith({
      item_kind: "assessment",
      item_id: quiz.id,
      status: "scored",
      score: 50,
    });
  });

  it("加载失败显示错误提示", async () => {
    vi.mocked(getContentQuiz).mockRejectedValue(new Error("404"));
    renderPanel();

    expect(await screen.findByText(/无法加载测验/)).toBeInTheDocument();
  });
});
