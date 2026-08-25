import { describe, expect, it } from "vitest";
import { useAppStore } from "./appStore";

describe("appStore", () => {
  it("默认 Tab 为学习中心（阶段 4 应用壳导航反转）", () => {
    expect(useAppStore.getState().activeTab).toBe("learning");
  });

  it("setActiveTab 切换 Tab（practice 节点跳领域工作台依赖此行为）", () => {
    useAppStore.getState().setActiveTab("industrial");
    expect(useAppStore.getState().activeTab).toBe("industrial");
    useAppStore.getState().setActiveTab("learning");
    expect(useAppStore.getState().activeTab).toBe("learning");
  });
});
