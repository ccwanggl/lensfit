import "@testing-library/jest-dom/vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PathView, { computeLocks } from "./PathView";
import { useLabStore } from "../stores/labStore";
import { useAppStore } from "../stores/appStore";
import type { CurriculumNode } from "../utils/api";

vi.mock("../utils/api", () => ({
  getCurriculumGraph: vi.fn(),
  getContentQuiz: vi.fn(),
  putLearningProgress: vi.fn().mockResolvedValue({}),
}));

import { getCurriculumGraph, getContentQuiz } from "../utils/api";

function node(
  id: string,
  kind: CurriculumNode["kind"],
  module: string,
  prerequisites: string[] = []
): CurriculumNode {
  return { id, kind, ref: id, title: `标题-${id}`, module, prerequisites, status: "not_started" };
}

const nodes: CurriculumNode[] = [
  node("thin-lens", "experiment", "20-geometric-optics"),
  node("angle-of-view", "experiment", "20-geometric-optics", ["thin-lens"]),
  node("cmos-fundamentals", "concept", "20-geometric-optics"),
  node("double-slit", "experiment", "30-wave-optics", ["thin-lens", "angle-of-view"]),
  node("industrial", "practice", "practice", ["thin-lens", "angle-of-view"]),
];

beforeEach(() => {
  vi.clearAllMocks();
  useLabStore.setState({
    learningView: "path",
    activeConceptId: null,
    activeExperimentId: null,
    recentExperiments: [],
  });
  useAppStore.setState({ activeTab: "learning" });
  vi.mocked(getCurriculumGraph).mockResolvedValue({ nodes, edges: [] });
});

describe("computeLocks", () => {
  it("空完成集合：有先修的节点锁定并列出缺失先修，无先修的节点解锁", () => {
    const locks = computeLocks(nodes, new Set());
    expect(locks.get("thin-lens")).toEqual({ locked: false, missing: [] });
    expect(locks.get("cmos-fundamentals")!.locked).toBe(false);
    expect(locks.get("angle-of-view")).toEqual({
      locked: true,
      missing: ["标题-thin-lens"],
    });
    expect(locks.get("double-slit")!.missing).toEqual([
      "标题-thin-lens",
      "标题-angle-of-view",
    ]);
  });

  it("先修完成后解锁，部分完成时只列剩余缺失", () => {
    const locks = computeLocks(nodes, new Set(["thin-lens"]));
    expect(locks.get("angle-of-view")!.locked).toBe(false);
    expect(locks.get("double-slit")).toEqual({
      locked: true,
      missing: ["标题-angle-of-view"],
    });
  });

  it("全部完成后无锁定节点", () => {
    const locks = computeLocks(
      nodes,
      new Set(["thin-lens", "angle-of-view", "double-slit"])
    );
    for (const info of locks.values()) {
      expect(info.locked).toBe(false);
    }
  });
});

function renderView() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <PathView />
    </QueryClientProvider>
  );
}

describe("PathView", () => {
  it("按 module 分层展示并显示锁定原因", async () => {
    renderView();

    expect(await screen.findByText("几何光学")).toBeInTheDocument();
    expect(screen.getByText("实践场")).toBeInTheDocument();
    // 锁定节点显示缺失先修标题（double-slit 与 industrial 缺失列表相同）
    expect(
      screen.getAllByText(/需先完成：标题-thin-lens、标题-angle-of-view/).length
    ).toBeGreaterThan(0);
    // 锁定按钮不可用
    expect(screen.getByRole("button", { name: /标题-double-slit/ })).toBeDisabled();
  });

  it("点击未锁定实验节点跳转沙盘并加载实验", async () => {
    const user = userEvent.setup();
    renderView();

    await user.click(
      await screen.findByRole("button", { name: (n) => n.replace(/\s+/g, "") === "实验标题-thin-lens" })
    );

    const state = useLabStore.getState();
    expect(state.learningView).toBe("sandbox");
    expect(state.activeExperimentId).toBe("thin-lens");
  });

  it("点击 concept 节点跳转教程视图", async () => {
    const user = userEvent.setup();
    renderView();

    await user.click(
      await screen.findByRole("button", { name: (n) => n.replace(/\s+/g, "") === "概念标题-cmos-fundamentals" })
    );

    const state = useLabStore.getState();
    expect(state.learningView).toBe("tutorials");
    expect(state.activeConceptId).toBe("cmos-fundamentals");
  });

  it("锁定节点点击不触发跳转", async () => {
    const user = userEvent.setup();
    renderView();

    await user.click(await screen.findByRole("button", { name: /标题-double-slit/ }));

    expect(useLabStore.getState().learningView).toBe("path");
    expect(useLabStore.getState().activeExperimentId).toBeNull();
  });

  it("practice 节点解锁后点击跳转对应领域 Tab", async () => {
    // 阶段 1 完成集合为空，practice 默认锁定；这里模拟其先修已完成的情形
    vi.mocked(getCurriculumGraph).mockResolvedValue({
      nodes: [node("thin-lens", "experiment", "20-geometric-optics"),
              node("industrial", "practice", "practice")],
      edges: [],
    });
    const user = userEvent.setup();
    renderView();

    await user.click(
      await screen.findByRole("button", { name: (n) => n.replace(/\s+/g, "") === "实践标题-industrial" })
    );

    expect(useAppStore.getState().activeTab).toBe("industrial");
  });

  it("graph 返回 completed 状态时解锁依赖节点并显示已完成标记", async () => {
    // 阶段 2：completed 集合来自 graph 节点 status（learning_records 合并）
    vi.mocked(getCurriculumGraph).mockResolvedValue({
      nodes: [
        { ...node("thin-lens", "experiment", "20-geometric-optics"), status: "completed" },
        node("angle-of-view", "experiment", "20-geometric-optics", ["thin-lens"]),
      ],
      edges: [],
    });
    renderView();

    // thin-lens 行显示已完成标记（CheckCircle2 的 aria-label）
    expect(await screen.findByLabelText("已完成")).toBeInTheDocument();
    // 依赖 thin-lens 的 angle-of-view 解锁：不显示锁定原因且按钮可点击
    expect(screen.queryByText(/需先完成/)).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: (n) => n.replace(/\s+/g, "") === "实验标题-angle-of-view" })
    ).toBeEnabled();
  });

  it("completed 节点即使先修缺失也不显示锁定（状态以服务端合并为准）", async () => {
    vi.mocked(getCurriculumGraph).mockResolvedValue({
      nodes: [
        node("thin-lens", "experiment", "20-geometric-optics"),
        {
          ...node("angle-of-view", "experiment", "20-geometric-optics", ["thin-lens"]),
          status: "completed",
        },
      ],
      edges: [],
    });
    renderView();

    const btn = await screen.findByRole("button", {
      // completed 行的 accessible name 会拼上 CheckCircle2 的「已完成」
      name: (n) => n.replace(/\s+/g, "").startsWith("实验标题-angle-of-view"),
    });
    expect(btn).toBeEnabled();
    expect(screen.getByLabelText("已完成")).toBeInTheDocument();
  });

  it("点击 assessment 节点在路径视图内打开测验面板", async () => {
    // 阶段 3：测验节点不跳转视图，直接内嵌打开 QuizPanel
    vi.mocked(getCurriculumGraph).mockResolvedValue({
      nodes: [node("geo-quiz", "assessment", "20-geometric-optics")],
      edges: [],
    });
    vi.mocked(getContentQuiz).mockResolvedValue({
      id: "geo-quiz",
      title: "几何光学自测",
      module: "20-geometric-optics",
      concepts: [],
      pass_score: 80,
      questions: [
        {
          question: "题干：像距是多少？",
          options: ["75 mm", "100 mm"],
          correct_index: 0,
          explanation: "",
        },
      ],
    });
    const user = userEvent.setup();
    renderView();

    await user.click(
      await screen.findByRole("button", { name: (n) => n.replace(/\s+/g, "") === "测验标题-geo-quiz" })
    );

    expect(useLabStore.getState().activeQuizId).toBe("geo-quiz");
    expect(useLabStore.getState().learningView).toBe("path");
    expect(await screen.findByText("几何光学自测")).toBeInTheDocument();
    expect(screen.getByText("题干：像距是多少？")).toBeInTheDocument();

    // 关闭按钮收起面板
    await user.click(screen.getByRole("button", { name: "关闭测验" }));
    expect(useLabStore.getState().activeQuizId).toBeNull();
  });
});
